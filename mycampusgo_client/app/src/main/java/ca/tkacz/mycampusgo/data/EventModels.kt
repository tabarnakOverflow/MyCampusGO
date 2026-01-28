package ca.tkacz.mycampusgo.data

data class EventSummary(
    val slug: String,
    val title: String,
    val location: String? = null,
    val start: String? = null,   // ISO string from your API (keep as String first)
    val end: String? = null,
    val excerpt: String? = null,
    val event_type: String? = null,
    val image_url: String? = null
)

data class EventDetail(
    val slug: String,
    val title: String,
    val location: String? = null,
    val start: String? = null,
    val end: String? = null,
    val body_html: String? = null
)
