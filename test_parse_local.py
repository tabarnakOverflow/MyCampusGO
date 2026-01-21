from pathlib import Path
from mycampusgo_api.scrape import parse_events_list, parse_event_detail, parse_announcements
from mycampusgo_api.config import settings

fix = Path("fixtures")

def main():
    if (fix/"jan14.html").exists():
        html = (fix/"jan14.html").read_text(encoding="utf-8", errors="ignore")
        events = parse_events_list(html)
        print("events_list_count:", len(events))
        if events:
            print("first_event:", events[0].model_dump())

    if (fix/"event.html").exists():
        html = (fix/"event.html").read_text(encoding="utf-8", errors="ignore")
        detail = parse_event_detail(html, f"{settings.base_url}/events/example")
        print("event_detail_title:", detail.title if detail else None)

    if (fix/"announcements.html").exists():
        html = (fix/"announcements.html").read_text(encoding="utf-8", errors="ignore")
        anns = parse_announcements(html)
        print("announcements_count:", len(anns))
        if anns:
            print("first_announcement:", anns[0].model_dump())

if __name__ == "__main__":
    main()
