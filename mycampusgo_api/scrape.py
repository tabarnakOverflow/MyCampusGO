from __future__ import annotations

from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin
from datetime import datetime, timedelta
import httpx
import re
from typing import Any

from .config import settings
from .models import EventSummary, EventDetail, Announcement
from .utils import abs_url, slug_from_url, parse_dt, html_to_text


def _localize_dt(dt):
    """Ensure dt is timezone-aware in America/Halifax for safe comparisons."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=settings.timezone)
    return dt.astimezone(settings.timezone)

DEFAULT_HEADERS = {
    "User-Agent": settings.user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
}

AJAX_HEADERS = {
    **DEFAULT_HEADERS,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

async def fetch_html(url: str) -> str:
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30.0, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text

async def fetch_json(url: str, params: dict[str, Any], referer: str | None = None) -> Any:
    headers = dict(AJAX_HEADERS)
    if referer:
        headers["Referer"] = referer
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

def _find_next_page_href(soup: BeautifulSoup) -> str | None:
    next_a = soup.select_one("li.pager__item--next a[href]")
    if next_a and next_a.get("href"):
        return next_a["href"]
    next_a = soup.select_one("a[rel='next'][href]")
    if next_a and next_a.get("href"):
        return next_a["href"]
    return None

def _extract_view_dom_id(page_html: str) -> str | None:
    # Drupal renders a placeholder element with class 'js-view-dom-id-<64hex>'
    m = re.search(r"js-view-dom-id-([0-9a-f]{64})", page_html)
    return m.group(1) if m else None

def _extract_ajax_page_state(page_html: str) -> tuple[str | None, str | None]:
    # Optional; can help Drupal tailor the AJAX response.
    theme = None
    libs = None
    m = re.search(r'"ajaxPageState"\s*:\s*\{[^}]*"theme"\s*:\s*"([^"]+)"', page_html)
    if m:
        theme = m.group(1)
    m = re.search(r'"ajaxPageState"\s*:\s*\{[^}]*"libraries"\s*:\s*"([^"]+)"', page_html)
    if m:
        libs = m.group(1)
    return theme, libs

def parse_events_list(view_html: str) -> list[EventSummary]:
    """Parse the actual rendered *view HTML* (not the /events page source).

    Note: On stfx.ca, the /events page source often contains the view HTML as an escaped string
    that gets inserted via Drupal Views AJAX. This function expects the real HTML snippet.
    """
    base = settings.base_url
    soup = BeautifulSoup(view_html, "lxml")

    # The AJAX snippet typically includes <div class="view ..."> ... <div class="views-row"> ...</div>
    rows = soup.select("div.views-row")
    events: list[EventSummary] = []

    for row in rows:
        title_a = row.select_one(".views-field-title a[href]")
        if not title_a:
            continue
        title = title_a.get_text(" ", strip=True)
        url = abs_url(base, title_a.get("href")) or ""
        slug = slug_from_url(url)

        times = row.select(".views-field-field-dates time[datetime]")
        start = _localize_dt(parse_dt(times[0].get("datetime"))) if len(times) >= 1 else None
        end = _localize_dt(parse_dt(times[1].get("datetime"))) if len(times) >= 2 else None

        loc_el = row.select_one(".views-field-field-location .field-content")
        location = loc_el.get_text(" ", strip=True) if loc_el else None

        type_el = row.select_one(".views-field-field-event-type .field-content")
        event_type = type_el.get_text(" ", strip=True) if type_el else None

        teaser_el = row.select_one(".views-field-body .field-content")
        teaser = teaser_el.get_text(" ", strip=True) if teaser_el else None

        img = row.select_one("img[src]")
        image_url = abs_url(base, img.get("src")) if img else None

        events.append(EventSummary(
            title=title,
            url=url,
            slug=slug,
            start=start,
            end=end,
            location=location,
            event_type=event_type,
            teaser=teaser,
            image_url=image_url,
        ))

    return events

def _extract_view_html_from_ajax(payload: Any) -> str | None:
    # payload is an array of "commands". We want the "insert" command whose data contains the view.
    if not isinstance(payload, list):
        return None
    best = None
    for item in payload:
        if not isinstance(item, dict):
            continue
        if item.get("command") != "insert":
            continue
        data = item.get("data")
        if isinstance(data, str) and "view-events" in data:
            best = data
            break
    return best

async def _fetch_events_view_html(page_url: str, start_date_iso: str, page_index: int) -> str | None:
    """Fetch rendered events view HTML via Drupal Views AJAX.

    We first GET the page to discover the current view_dom_id token, then call /views/ajax.
    """
    page_html = await fetch_html(page_url)
    view_dom_id = _extract_view_dom_id(page_html)
    if not view_dom_id:
        return None

    # This view config is stable for StFX's events page in your captured data.
    ajax_params = {
        "_wrapper_format": "drupal_ajax",
        "view_name": "events",
        "view_display_id": "block_all",
        "view_args": "",
        "view_path": "/node/1756",
        "pager_element": 0,
        "view_dom_id": view_dom_id,
        "_drupal_ajax": 1,
        # Exposed filters:
        "type": "All",
        "start_date": start_date_iso,
        "end_date": "",
        "mycampus": 0,
        # Pagination:
        "page": page_index,
    }

    ajax_url = f"{settings.base_url}/views/ajax"

    payload = await fetch_json(ajax_url, ajax_params, referer=page_url)
    view_html = _extract_view_html_from_ajax(payload)

    # Fallback: retry with ajax_page_state fields if needed
    if not view_html:
        theme, libs = _extract_ajax_page_state(page_html)
        if theme:
            ajax_params["ajax_page_state[theme]"] = theme
        if libs:
            ajax_params["ajax_page_state[libraries]"] = libs
        payload = await fetch_json(ajax_url, ajax_params, referer=page_url)
        view_html = _extract_view_html_from_ajax(payload)

    return view_html

async def scrape_events(days_back: int = 7) -> list[EventSummary]:
    today = datetime.now(settings.timezone).date()
    start_date = today - timedelta(days=days_back)
    start_date_iso = start_date.isoformat()

    base_params = {
        "mycampus": 0,
        "type": "All",
        "start_date": start_date_iso,
    }

    all_events: list[EventSummary] = []
    seen: set[str] = set()

    page_index = 0
    while True:
        page_url = f"{settings.base_url}{settings.events_path}?{urlencode(base_params)}&page={page_index}"
        view_html = await _fetch_events_view_html(page_url, start_date_iso=start_date_iso, page_index=page_index)
        if not view_html:
            break

        page_events = parse_events_list(view_html)

        # Extra safety: enforce the window locally even if the view returns older items.
        window_start = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=settings.timezone)
        for e in page_events:
            s = _localize_dt(e.start)
            if s is not None and s < window_start:
                continue
            if s is not None:
                e.start = s
            if e.slug and e.slug not in seen:
                all_events.append(e)
                seen.add(e.slug)

        # Determine if there's a "next" pager link within the rendered view HTML.
        soup = BeautifulSoup(view_html, "lxml")
        next_href = _find_next_page_href(soup)
        if not next_href:
            break
        page_index += 1

        # Just in case: avoid infinite loops
        if page_index > 50:
            break

    return all_events

def parse_event_detail(html: str, page_url: str) -> EventDetail | None:
    base = settings.base_url
    soup = BeautifulSoup(html, "lxml")

    title_el = soup.select_one("h1.page-title .field--name-title") or soup.select_one("h1.page-title") or soup.select_one("h1")
    if not title_el:
        return None
    title = title_el.get_text(" ", strip=True)

    url = page_url
    slug = slug_from_url(url)

    article = soup.select_one("article.node--type-event")
    if not article:
        return None

    type_el = article.select_one(".field--name-field-event-type")
    event_type = type_el.get_text(" ", strip=True) if type_el else None

    loc_el = article.select_one(".field--name-field-custom-location")
    location = loc_el.get_text(" ", strip=True) if loc_el else None

    times = article.select(".field--name-field-dates time[datetime]")
    dts: list[str] = []
    for t in times:
        dtv = t.get("datetime")
        if dtv and (not dts or dts[-1] != dtv):
            dts.append(dtv)
    start = _localize_dt(parse_dt(dts[0])) if len(dts) >= 1 else None
    end = _localize_dt(parse_dt(dts[-1])) if len(dts) >= 2 else None

    img = article.select_one(".field--name-field-image img[src]")
    image_url = abs_url(base, img.get("src")) if img else None

    body_el = article.select_one(".field--name-body")
    body_html = str(body_el) if body_el else None
    body_text = html_to_text(body_html) if body_html else None

    return EventDetail(
        title=title,
        url=url,
        slug=slug,
        start=start,
        end=end,
        location=location,
        event_type=event_type,
        body_text=body_text,
        body_html=body_html,
        image_url=image_url,
    )

async def scrape_event_detail(slug: str) -> EventDetail | None:
    url = f"{settings.base_url}{settings.events_path}/{slug}"
    html = await fetch_html(url)
    return parse_event_detail(html, url)

def parse_announcements(html: str) -> list[Announcement]:
    soup = BeautifulSoup(html, "lxml")
    articles = soup.select("article.node--type-announcement")
    out: list[Announcement] = []

    for a in articles:
        headline_el = a.select_one(".field--name-field-announcement-headline")
        if not headline_el:
            continue
        headline = headline_el.get_text(" ", strip=True)

        is_new = bool(a.select_one(".new-sign"))

        full_el = a.select_one(".announcement-content-full .field--name-body")
        body_html = str(full_el) if full_el else None
        body_text = html_to_text(body_html) if body_html else None

        out.append(Announcement(headline=headline, body_text=body_text, body_html=body_html, is_new=is_new))
    return out

async def scrape_announcements() -> list[Announcement]:
    url = f"{settings.base_url}{settings.announcements_path}"
    html = await fetch_html(url)
    return parse_announcements(html)
