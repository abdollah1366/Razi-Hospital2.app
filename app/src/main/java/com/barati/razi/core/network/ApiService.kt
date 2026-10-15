package com.barati.razi.core.network

import kotlinx.serialization.json.JsonObject
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.PUT
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

    @GET("incidents")
    suspend fun incidents(
        @Query("status") status: String? = null,
        @Query("page") page: Int = 1,
        @Query("size") size: Int = 50,
    ): IncidentPageDto

    @POST("incidents/{id}/status")
    suspend fun changeIncidentStatus(@Path("id") id: String, @Body body: StatusChangeRequest): IncidentSummaryDto

    @POST("incidents/{id}/assign")
    suspend fun assignIncident(@Path("id") id: String, @Body body: AssignRequest): IncidentSummaryDto

    @POST("incidents/{id}/actions")
    suspend fun addIncidentAction(@Path("id") id: String, @Body body: ActionRequest): ActionDto

    @PATCH("incidents/{id}/actions/{actionId}")
    suspend fun updateIncidentAction(
        @Path("id") id: String,
        @Path("actionId") actionId: String,
        @Body body: ActionUpdateRequest,
    ): ActionDto

    @GET("training/courses")
    suspend fun trainingCourses(): List<CourseDto>

    @GET("training/courses/{id}")
    suspend fun trainingCourse(@Path("id") id: String): CourseDto

    @POST("training/items/{id}/views")
    suspend fun startView(@Path("id") itemId: String): ViewStartDto

    @PATCH("training/views/{id}")
    suspend fun updateView(@Path("id") viewId: String, @Body body: ViewProgressRequest)

    @GET("training/exams")
    suspend fun trainingExams(): List<ExamDto>

    @POST("training/exams/{id}/attempts")
    suspend fun startAttempt(@Path("id") examId: String): AttemptDto

    @GET("training/attempts/{id}")
    suspend fun attempt(@Path("id") id: String): AttemptDto

    @PUT("training/attempts/{id}/answers")
    suspend fun saveAnswers(@Path("id") id: String, @Body body: AnswersRequest): AttemptDto

    @POST("training/attempts/{id}/submit")
    suspend fun submitAttempt(@Path("id") id: String, @Body body: AnswersRequest): AttemptDto

    @GET("request-types")
    suspend fun requestTypes(): List<RequestTypeDto>

    @POST("requests")
    suspend fun createRequest(@Body body: RequestCreateRequest): RequestCreatedDto

    @GET("requests/mine")
    suspend fun myRequests(): List<RequestSummaryDto>

    @GET("requests")
    suspend fun requestQueue(
        @Query("status") status: String? = null,
        @Query("assigned") assigned: String? = null,
        @Query("page") page: Int = 1,
        @Query("size") size: Int = 100,
    ): RequestPageDto

    @GET("requests/{id}")
    suspend fun request(@Path("id") id: String): RequestDetailDto

    @POST("requests/{id}/status")
    suspend fun changeRequestStatus(@Path("id") id: String, @Body body: RequestStatusBody): RequestDetailDto

    @GET("requests/{id}/agents")
    suspend fun requestAgents(@Path("id") id: String): List<PersonDto>

    @POST("requests/{id}/assign")
    suspend fun assignRequest(@Path("id") id: String, @Body body: RequestAssignBody): RequestDetailDto

    /** اگر کاربر پس از ارجاع دیگر به درخواست دسترسی نداشته باشد، پاسخ ۲۰۴ (بدون بدنه) است. */
    @POST("requests/{id}/transfer")
    suspend fun transferRequest(@Path("id") id: String, @Body body: RequestTransferBody): retrofit2.Response<RequestDetailDto>

    @POST("requests/{id}/comments")
    suspend fun commentRequest(@Path("id") id: String, @Body body: RequestCommentBody): RequestDetailDto

    @POST("requests/{id}/attachments")
    suspend fun attachToRequest(
        @Path("id") id: String,
        @Query("filename") filename: String,
        @Body body: RequestBody,
    ): RequestDetailDto

    @POST("requests/{id}/rate")
    suspend fun rateRequest(@Path("id") id: String, @Body body: RequestRateBody): RequestDetailDto

    @POST("requests/{id}/reopen")
    suspend fun reopenRequest(@Path("id") id: String, @Body body: RequestReopenBody): RequestDetailDto
}
