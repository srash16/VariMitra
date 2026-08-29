package com.example.varimitra

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.varimitra.ui.theme.VarimitraTheme

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            VarimitraTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color(0xFFF8F7F3)
                ) {
                    VariMitraApp()
                }
            }
        }
    }
}

data class Facility(
    val emoji: String,
    val title: String,
    val subtitle: String
)

@Composable
fun VariMitraApp() {

    var selectedTab by remember { mutableIntStateOf(0) }

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = Color.White
            ) {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Text("⌂", fontSize = 24.sp) },
                    label = { Text("Home") }
                )

                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Text("🗺", fontSize = 20.sp) },
                    label = { Text("Route") }
                )

                NavigationBarItem(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    icon = { Text("ℹ", fontSize = 22.sp) },
                    label = { Text("Info") }
                )
            }
        }
    ) { paddingValues ->

        when (selectedTab) {

            0 -> HomeScreen(paddingValues)

            1 -> SimpleScreen(
                title = "Wari Route",
                description = "Your Wari route and important locations will appear here.",
                paddingValues = paddingValues
            )

            2 -> SimpleScreen(
                title = "Wari Information",
                description = "Important information about the Pandharpur Wari.",
                paddingValues = paddingValues
            )
        }
    }
}

@Composable
fun HomeScreen(paddingValues: PaddingValues) {

    val facilities = listOf(
        Facility("💧", "Water", "Nearby water points"),
        Facility("🏥", "Medical", "Hospitals & first aid"),
        Facility("🍛", "Food", "Food & community meals"),
        Facility("🚻", "Toilets", "Nearby toilet facilities")
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8F7F3))
            .padding(paddingValues)
    ) {

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp)
        ) {

            Spacer(modifier = Modifier.height(20.dp))

            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {

                Column(
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "VariMitra",
                        fontSize = 30.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF4B2E83)
                    )

                    Text(
                        text = "Your companion on the Wari",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }

                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(Color(0xFFE9DDF7)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "🙏",
                        fontSize = 23.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            // Location card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFEEE7F7)
                )
            ) {

                Column(
                    modifier = Modifier.padding(18.dp)
                ) {

                    Text(
                        text = "📍 Your Location",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF4B2E83)
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Locating you...",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Text(
                        text = "GPS location will be used to find nearby facilities",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
            }

            Spacer(modifier = Modifier.height(22.dp))

            Text(
                text = "Find Nearby",
                fontSize = 21.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Facility grid
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier.height(235.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                userScrollEnabled = false
            ) {

                items(facilities) { facility ->

                    FacilityCard(facility)
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            // Route card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White
                ),
                elevation = CardDefaults.cardElevation(2.dp)
            ) {

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(17.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {

                    Text(
                        text = "🗺",
                        fontSize = 30.sp
                    )

                    Spacer(modifier = Modifier.width(14.dp))

                    Column(
                        modifier = Modifier.weight(1f)
                    ) {

                        Text(
                            text = "Wari Route",
                            fontWeight = FontWeight.Bold,
                            fontSize = 17.sp
                        )

                        Text(
                            text = "View route, villages & important stops",
                            color = Color.Gray,
                            fontSize = 12.sp
                        )
                    }

                    Text(
                        text = "›",
                        fontSize = 28.sp,
                        color = Color(0xFF4B2E83)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Emergency
            Button(
                onClick = { },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(58.dp),
                shape = RoundedCornerShape(16.dp),
                colors = androidx.compose.material3.ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFB3261E)
                )
            ) {

                Text(
                    text = "🚨  EMERGENCY",
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        // Voice button
        FloatingActionButton(
            onClick = { },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(
                    end = 20.dp,
                    bottom = 85.dp
                )
                .size(68.dp),
            containerColor = Color(0xFF4B2E83),
            contentColor = Color.White
        ) {

            Text(
                text = "🎙",
                fontSize = 28.sp
            )
        }
    }
}

@Composable
fun FacilityCard(facility: Facility) {

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(15.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            Text(
                text = facility.emoji,
                fontSize = 32.sp
            )

            Spacer(modifier = Modifier.height(5.dp))

            Text(
                text = facility.title,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold
            )

            Text(
                text = facility.subtitle,
                fontSize = 10.sp,
                color = Color.Gray,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun SimpleScreen(
    title: String,
    description: String,
    paddingValues: PaddingValues
) {

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(paddingValues)
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Text(
            text = title,
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF4B2E83)
        )

        Spacer(modifier = Modifier.height(12.dp))

        Text(
            text = description,
            textAlign = TextAlign.Center,
            color = Color.Gray
        )
    }
}