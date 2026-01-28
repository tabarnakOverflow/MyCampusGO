package ca.tkacz.mycampusgo.data

import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface MyCampusGoApi {

    // Example: /events?days_back=7
    @GET("events")
    suspend fun getEvents(@Query("days_back") daysBack: Int = 7): List<EventSummary>

    @GET("events/{slug}")
    suspend fun getEvent(@Path("slug") slug: String): EventDetail
}
