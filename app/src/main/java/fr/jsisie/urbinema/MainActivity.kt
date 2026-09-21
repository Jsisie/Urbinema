package fr.jsisie.urbinema

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import fr.jsisie.urbinema.app.MainViewModel
import fr.jsisie.urbinema.ui.UrbinemaApp
import org.koin.androidx.viewmodel.ext.android.viewModel

/** Single-activity host for the Compose navigation graph. */
class MainActivity : ComponentActivity() {
    private val mainViewModel: MainViewModel by viewModel()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            UrbinemaApp(mainViewModel)
        }
    }
}