package com.barati.razi.feature.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.Campaign
import androidx.compose.material.icons.filled.ListAlt
import androidx.compose.material.icons.filled.Public
import androidx.compose.material.icons.filled.ReportProblem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.barati.razi.AppContainer
import com.barati.razi.core.data.can
import com.barati.razi.core.network.MeDto
import com.barati.razi.core.util.toPersianDigits
import com.barati.razi.ui.components.MenuTile
import com.barati.razi.ui.components.RaziScaffold

@Composable
fun StaffHomeScreen(
    container: AppContainer,
    me: MeDto,
    onNewIncident: () -> Unit,
    onMyIncidents: () -> Unit,
    onAnnouncements: () -> Unit,
    onPublic: () -> Unit,
    onLogout: () -> Unit,
) {
    var pendingAck by remember { mutableIntStateOf(0) }
    val pending by container.incidentRepository.pending.collectAsState(initial = emptyList())
    LaunchedEffect(me.id) {
        if (me.can("announcement.read")) pendingAck = container.contentRepository.pendingAckCount()
    }
    RaziScaffold(
        title = "بخش کارکنان",
        actions = {
            IconButton(onClick = onLogout) { Icon(Icons.AutoMirrored.Filled.Logout, contentDescription = "خروج") }
        },
    ) { padding ->
        Column(
            Modifier.fillMaxSize().padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(me.fullName, style = MaterialTheme.typography.titleLarge)
            me.unitName?.let { Text(it, style = MaterialTheme.typography.bodyMedium) }
            if (me.can("incident.create")) {
                MenuTile("ثبت گزارش خطا، حادثه یا شبه‌خطا", "امکان ارسال ناشناس", Icons.Filled.ReportProblem, onNewIncident)
                MenuTile(
                    "گزارش‌های من",
                    if (pending.isNotEmpty()) toPersianDigits("${pending.size} گزارش در انتظار ارسال") else "پیگیری وضعیت",
                    Icons.Filled.ListAlt,
                    onMyIncidents,
                )
            }
            if (me.can("announcement.read")) {
                MenuTile(
                    "اخبار و بخشنامه‌ها",
                    if (pendingAck > 0) "بخشنامه‌هایی که باید مطالعه کنید" else null,
                    Icons.Filled.Campaign,
                    onAnnouncements,
                    badge = pendingAck,
                )
            }
            MenuTile("خدمات عمومی بیمارستان", "راهنمای بخش‌ها، پرسش‌ها و شکایات", Icons.Filled.Public, onPublic)
            Text(
                "بخش‌های آموزش، پژوهش، گفتگو و درخواست‌های پشتیبانی در مراحل بعدی اضافه می‌شوند.",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}
