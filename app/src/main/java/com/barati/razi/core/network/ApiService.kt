package com.barati.razi.core.network

import kotlinx.serialization.json.JsonObject
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {
    @POST("auth/login")
    suspend fun login(@Body body: LoginRequest): TokenResponse

    @POST("auth/logout")
    suspend fun logout(@Body body: RefreshRequest)

    @POST("auth/change-password")
    suspend fun changePassword(@Body body: ChangePasswordRequest)

    @GET("auth/me")
    suspend fun me(): MeDto

    @GET("public/units")
    suspend fun publicUnits(): List<UnitDto>

    @GET("units")
    suspend fun allUnits(): List<UnitDto>

    @GET("public/faqs")
    suspend fun faqs(): List<FaqDto>

    @GET("public/announcements")
    suspend fun publicAnnouncements(): List<AnnouncementDto>

    @POST("public/feedback")
    suspend fun submitFeedback(@Body body: FeedbackRequest): FeedbackCreated

    @GET("public/feedback/{code}")
    suspend fun feedbackStatus(@Path("code") code: String): FeedbackStatusDto

    @POST("public/incidents/track")
    suspend fun trackIncident(@Body body: TrackRequest): TrackResponse

    @GET("announcements")
    suspend fun announcements(@Query("only_pending_ack") onlyPendingAck: Boolean = false): List<AnnouncementDto>

    @POST("announcements/{id}/read")
    suspend fun markRead(@Path("id") id: String): AnnouncementDto

    @POST("announcements/{id}/ack")
    suspend fun acknowledge(@Path("id") id: String): AnnouncementDto

    @GET("forms/{code}")
    suspend fun form(@Path("code") code: String): JsonObject

    @POST("incidents")
    suspend fun createIncident(@Body body: IncidentCreateRequest): IncidentCreated

    @GET("incidents/mine")
    suspend fun myIncidents(): List<IncidentSummaryDto>

    @GET("incidents/{id}")
    suspend fun incident(@Path("id") id: String): IncidentDetailDto
}
