package com.barati.razi.ui.navigation

import android.net.Uri
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.barati.razi.AppContainer
import com.barati.razi.core.data.SessionState
import com.barati.razi.feature.announcements.AnnouncementsScreen
import com.barati.razi.feature.auth.ChangePasswordScreen
import com.barati.razi.feature.auth.LoginScreen
import com.barati.razi.feature.home.StaffHomeScreen
import com.barati.razi.feature.incident.IncidentDetailScreen
import com.barati.razi.feature.incident.IncidentFormScreen
import com.barati.razi.feature.incident.MyIncidentsScreen
import com.barati.razi.feature.incident.ReviewListScreen
import com.barati.razi.feature.incident.TrackIncidentScreen
import com.barati.razi.feature.publicinfo.FaqScreen
import com.barati.razi.feature.publicinfo.FeedbackScreen
import com.barati.razi.feature.publicinfo.PublicHomeScreen
import com.barati.razi.feature.publicinfo.PublicNewsScreen
import com.barati.razi.feature.publicinfo.UnitsScreen
import com.barati.razi.feature.requests.NewRequestScreen
import com.barati.razi.feature.requests.RequestDetailScreen
import com.barati.razi.feature.requests.RequestsHomeScreen
import com.barati.razi.feature.training.AttemptScreen
import com.barati.razi.feature.training.CourseItemScreen
import com.barati.razi.feature.training.CourseScreen
import com.barati.razi.feature.training.ExamTakeScreen
import com.barati.razi.feature.training.TrainingHomeScreen
import com.barati.razi.ui.components.LoadingBox
import kotlinx.coroutines.launch

object Routes {
    const val SPLASH = "splash"
    const val PUBLIC_HOME = "public"
    const val UNITS = "units"
    const val FAQ = "faq"
    const val NEWS = "news"
    const val FEEDBACK = "feedback"
    const val TRACK = "track?code={code}&secret={secret}"
    const val LOGIN = "login"
    const val CHANGE_PASSWORD = "change_password"
    const val STAFF_HOME = "staff"
    const val INCIDENT_NEW = "incident_new"
    const val MY_INCIDENTS = "my_incidents"
    const val INCIDENT_DETAIL = "incident/{id}"
    const val ANNOUNCEMENTS = "announcements"
    const val REVIEW = "review"
    const val TRAINING = "training"
    const val COURSE = "course/{id}"
    const val COURSE_ITEM = "course/{courseId}/item/{itemId}"
    const val EXAM_TAKE = "exam/{id}/take"
    const val ATTEMPT = "attempt/{id}"
    const val REQUESTS = "requests"
    const val REQUEST_NEW = "request_new"
    const val REQUEST_DETAIL = "request/{id}"

    /** صفحه‌هایی که بدون نشست معتبر باز نمی‌مانند. */
    val staffOnly = setOf(
        CHANGE_PASSWORD, STAFF_HOME, MY_INCIDENTS, INCIDENT_DETAIL, ANNOUNCEMENTS, REVIEW,
        TRAINING, COURSE, COURSE_ITEM, EXAM_TAKE, ATTEMPT, REQUESTS, REQUEST_DETAIL,
    )

    fun track(code: String = "", secret: String = "") = "track?code=${Uri.encode(code)}&secret=${Uri.encode(secret)}"
    fun incident(id: String) = "incident/$id"
    fun course(id: String) = "course/$id"
    fun courseItem(courseId: String, itemId: String) = "course/$courseId/item/$itemId"
    fun examTake(id: String) = "exam/$id/take"
    fun attempt(id: String) = "attempt/$id"
    fun request(id: String) = "request/$id"
}

@Composable
fun RaziNavHost(container: AppContainer, nav: NavHostController = rememberNavController()) {
    val session by container.authRepository.session.collectAsState()
    val scope = rememberCoroutineScope()
    val back: () -> Unit = { nav.popBackStack() }

    fun goStaffHome() = nav.navigate(Routes.STAFF_HOME) { popUpTo(Routes.PUBLIC_HOME) }

    // اگر نشست منقضی شد، کاربر از صفحه‌های کارکنان به صفحه ورود برده می‌شود.
    LaunchedEffect(session) {
        val route = nav.currentDestination?.route
        if (session is SessionState.LoggedOut && route != null && route in Routes.staffOnly) {
            nav.navigate(Routes.LOGIN) { popUpTo(Routes.PUBLIC_HOME) }
        }
    }

    NavHost(navController = nav, startDestination = Routes.SPLASH) {
        composable(Routes.SPLASH) {
            LoadingBox()
            LaunchedEffect(session) {
                val s = session
                if (s is SessionState.Unknown) return@LaunchedEffect
                nav.navigate(Routes.PUBLIC_HOME) { popUpTo(Routes.SPLASH) { inclusive = true } }
                if (s is SessionState.LoggedIn) {
                    nav.navigate(if (s.me.mustChangePassword) Routes.CHANGE_PASSWORD else Routes.STAFF_HOME)
                }
            }
        }
        composable(Routes.PUBLIC_HOME) {
            PublicHomeScreen(
                isLoggedIn = session is SessionState.LoggedIn,
                onUnits = { nav.navigate(Routes.UNITS) },
                onFaq = { nav.navigate(Routes.FAQ) },
                onNews = { nav.navigate(Routes.NEWS) },
                onFeedback = { nav.navigate(Routes.FEEDBACK) },
                onTrack = { nav.navigate(Routes.track()) },
                onStaff = {
                    val s = session
                    if (s is SessionState.LoggedIn && !s.me.mustChangePassword) goStaffHome() else nav.navigate(Routes.LOGIN)
                },
            )
        }
        composable(Routes.UNITS) { UnitsScreen(container, back) }
        composable(Routes.FAQ) { FaqScreen(container, back) }
        composable(Routes.NEWS) { PublicNewsScreen(container, back) }
        composable(Routes.FEEDBACK) { FeedbackScreen(container, back) }
        composable(
            Routes.TRACK,
            arguments = listOf(
                navArgument("code") { type = NavType.StringType; defaultValue = "" },
                navArgument("secret") { type = NavType.StringType; defaultValue = "" },
            ),
        ) { entry ->
            TrackIncidentScreen(
                container,
                entry.arguments?.getString("code").orEmpty(),
                entry.arguments?.getString("secret").orEmpty(),
                back,
            )
        }
        composable(Routes.LOGIN) {
            LoginScreen(container, onBack = back, onLoggedIn = { mustChange ->
                nav.navigate(if (mustChange) Routes.CHANGE_PASSWORD else Routes.STAFF_HOME) {
                    popUpTo(Routes.PUBLIC_HOME)
                }
            })
        }
        composable(Routes.CHANGE_PASSWORD) { ChangePasswordScreen(container, onDone = { goStaffHome() }) }
        composable(Routes.STAFF_HOME) {
            val s = session
            if (s is SessionState.LoggedIn) {
                StaffHomeScreen(
                    container,
                    s.me,
                    onNewIncident = { nav.navigate(Routes.INCIDENT_NEW) },
                    onMyIncidents = { nav.navigate(Routes.MY_INCIDENTS) },
                    onAnnouncements = { nav.navigate(Routes.ANNOUNCEMENTS) },
                    onReview = { nav.navigate(Routes.REVIEW) },
                    onTraining = { nav.navigate(Routes.TRAINING) },
                    onRequests = { nav.navigate(Routes.REQUESTS) },
                    onPublic = { nav.popBackStack(Routes.PUBLIC_HOME, inclusive = false) },
                    onLogout = { scope.launch { container.authRepository.logout() } },
                )
            } else {
                LoadingBox()
            }
        }
        // فرم گزارش عمداً در staffOnly نیست تا با منقضی‌شدن نشست، اطلاعات واردشده از دست نرود.
        composable(Routes.INCIDENT_NEW) {
            IncidentFormScreen(container, onBack = back, onDone = { nav.popBackStack(Routes.STAFF_HOME, inclusive = false) })
        }
        composable(Routes.MY_INCIDENTS) {
            MyIncidentsScreen(
                container,
                onBack = back,
                onOpen = { nav.navigate(Routes.incident(it)) },
                onTrack = { code, secret -> nav.navigate(Routes.track(code, secret)) },
            )
        }
        composable(Routes.INCIDENT_DETAIL, arguments = listOf(navArgument("id") { type = NavType.StringType })) { entry ->
            IncidentDetailScreen(container, entry.arguments?.getString("id").orEmpty(), back)
        }
        composable(Routes.ANNOUNCEMENTS) { AnnouncementsScreen(container, back) }
        composable(Routes.REVIEW) { ReviewListScreen(container, back, onOpen = { nav.navigate(Routes.incident(it)) }) }
        composable(Routes.TRAINING) {
            TrainingHomeScreen(
                container,
                onBack = back,
                onCourse = { nav.navigate(Routes.course(it)) },
                onTakeExam = { nav.navigate(Routes.examTake(it)) },
                onAttempt = { nav.navigate(Routes.attempt(it)) },
            )
        }
        composable(Routes.COURSE, arguments = listOf(navArgument("id") { type = NavType.StringType })) { entry ->
            val courseId = entry.arguments?.getString("id").orEmpty()
            CourseScreen(
                container,
                courseId,
                onBack = back,
                onItem = { nav.navigate(Routes.courseItem(courseId, it)) },
                onTakeExam = { nav.navigate(Routes.examTake(it)) },
                onAttempt = { nav.navigate(Routes.attempt(it)) },
            )
        }
        composable(
            Routes.COURSE_ITEM,
            arguments = listOf(
                navArgument("courseId") { type = NavType.StringType },
                navArgument("itemId") { type = NavType.StringType },
            ),
        ) { entry ->
            val courseId = entry.arguments?.getString("courseId").orEmpty()
            CourseItemScreen(
                container,
                courseId,
                entry.arguments?.getString("itemId").orEmpty(),
                onBack = back,
                // محتوای قبلی/بعدی جای صفحه فعلی را می‌گیرد تا «بازگشت» مستقیم به دوره برگردد.
                onOpenItem = { nav.navigate(Routes.courseItem(courseId, it)) { popUpTo(Routes.COURSE_ITEM) { inclusive = true } } },
            )
        }
        composable(Routes.EXAM_TAKE, arguments = listOf(navArgument("id") { type = NavType.StringType })) { entry ->
            ExamTakeScreen(container, entry.arguments?.getString("id").orEmpty(), back)
        }
        composable(Routes.REQUESTS) {
            val s = session
            if (s is SessionState.LoggedIn) {
                RequestsHomeScreen(
                    container,
                    s.me,
                    onBack = back,
                    onNew = { nav.navigate(Routes.REQUEST_NEW) },
                    onOpen = { nav.navigate(Routes.request(it)) },
                )
            } else {
                LoadingBox()
            }
        }
        // مثل فرم گزارش، در staffOnly نیست تا با منقضی‌شدن نشست، متن واردشده از دست نرود.
        composable(Routes.REQUEST_NEW) {
            NewRequestScreen(
                container,
                onBack = back,
                onCreated = { nav.navigate(Routes.request(it)) { popUpTo(Routes.REQUEST_NEW) { inclusive = true } } },
            )
        }
        composable(Routes.REQUEST_DETAIL, arguments = listOf(navArgument("id") { type = NavType.StringType })) { entry ->
            RequestDetailScreen(container, entry.arguments?.getString("id").orEmpty(), back)
        }
        composable(Routes.ATTEMPT, arguments = listOf(navArgument("id") { type = NavType.StringType })) { entry ->
            AttemptScreen(container, entry.arguments?.getString("id").orEmpty(), back)
        }
    }
}
