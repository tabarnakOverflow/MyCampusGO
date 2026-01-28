package ca.tkacz.mycampusgo

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.appbar.AppBarLayout
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val toolbar = findViewById<MaterialToolbar>(R.id.topAppBar)
        setSupportActionBar(toolbar)

        val appBar = findViewById<AppBarLayout>(R.id.appBarLayout)
        ViewCompat.setOnApplyWindowInsetsListener(appBar) { v, insets ->
            val topInset = insets.getInsets(WindowInsetsCompat.Type.statusBars()).top
            v.updatePadding(top = topInset)
            insets
        }

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController

        navController.addOnDestinationChangedListener { _, destination, arguments ->
            when (destination.id) {
                R.id.eventsFragment -> {
                    supportActionBar?.title = getString(R.string.events)
                }
                R.id.announcementsFragment -> {
                    supportActionBar?.title = getString(R.string.announcements)
                }
                R.id.aboutFragment -> {
                    supportActionBar?.title = getString(R.string.about_top_bar)
                }
                R.id.eventDetailFragment -> {
                    supportActionBar?.title = getString(R.string.event_detail)
                }
            }

        }


        findViewById<BottomNavigationView>(R.id.bottomNav)
            .setupWithNavController(navController)
    }
}
