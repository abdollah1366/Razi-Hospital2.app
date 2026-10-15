package com.barati.razi

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.lifecycle.lifecycleScope
import com.barati.razi.ui.navigation.RaziNavHost
import com.barati.razi.ui.theme.RaziTheme
import com.barati.razi.work.IncidentUploadWorker
import com.barati.razi.work.RequestUploadWorker
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val container = (application as RaziApp).container
        lifecycleScope.launch {
            container.loadServerOrigin()
            container.authRepository.restore()
            // اگر گزارش یا درخواستی از قبل در صف مانده باشد، ارسال آن دوباره تلاش می‌شود.
            IncidentUploadWorker.schedule(applicationContext)
            RequestUploadWorker.schedule(applicationContext)
        }
        setContent {
            RaziTheme {
                Surface(Modifier.fillMaxSize()) { RaziNavHost(container) }
            }
        }
    }
}
