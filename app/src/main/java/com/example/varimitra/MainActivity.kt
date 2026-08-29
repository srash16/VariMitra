package com.example.varimitra

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MaterialTheme {
                VariMitraApp()
            }
        }
    }
}

@Composable
fun VariMitraApp() {

    var selectedFacility by remember {
        mutableStateOf<FacilityType?>(null)
    }

    var showMap by remember {
        mutableStateOf(false)
    }

    // Android system back button
    BackHandler(
        enabled = selectedFacility != null || showMap
    ) {
        if (selectedFacility != null) {
            selectedFacility = null
        } else if (showMap) {
            showMap = false
        }
    }

    // ---------------------------------------------------------
    // MAP SCREEN
    // ---------------------------------------------------------

    if (showMap) {

        MapScreen(
            onBack = {
                showMap = false
            }
        )

        return
    }

    // ---------------------------------------------------------
    // FACILITY SCREEN
    // ---------------------------------------------------------

    if (selectedFacility != null) {

        NearbyFacilitiesScreen(
            type = selectedFacility!!,
            onBack = {
                selectedFacility = null
            }
        )

        return
    }

    // ---------------------------------------------------------
    // HOME SCREEN
    // ---------------------------------------------------------

    HomeScreen(
        onFacilityClick = { type ->
            selectedFacility = type
        },
        onRouteClick = {
            showMap = true
        }
    )
}


// ============================================================
// HOME SCREEN
// ============================================================

@Composable
fun HomeScreen(
    onFacilityClick: (FacilityType) -> Unit,
    onRouteClick: () -> Unit
) {

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8F7F3))
            .padding(16.dp)
    ) {

        // -----------------------------------------------------
        // HEADER
        // -----------------------------------------------------

        Text(
            text = "VariMitra",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF4B2E83)
        )

        Text(
            text = "Your companion on the Wari",
            fontSize = 14.sp,
            color = Color.Gray
        )

        Spacer(
            modifier = Modifier.height(20.dp)
        )

        // -----------------------------------------------------
        // LOCATION CARD
        // -----------------------------------------------------

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(18.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFEDE4F7)
            )
        ) {

            Column(
                modifier = Modifier.padding(18.dp)
            ) {

                Text(
                    text = "📍 Your Location",
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF4B2E83)
                )

                Spacer(
                    modifier = Modifier.height(6.dp)
                )

                Text(
                    text = "Location will be detected"
                )

                Text(
                    text = "Find nearby facilities around you",
                    color = Color.Gray,
                    fontSize = 13.sp
                )
            }
        }

        Spacer(
            modifier = Modifier.height(24.dp)
        )

        // -----------------------------------------------------
        // FIND NEARBY
        // -----------------------------------------------------

        Text(
            text = "Find Nearby",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(
            modifier = Modifier.height(12.dp)
        )

        // WATER + MEDICAL

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            FacilityCard(
                emoji = "💧",
                title = "Water",
                subtitle = "Nearby water points",
                modifier = Modifier.weight(1f),
                onClick = {
                    onFacilityClick(FacilityType.WATER)
                }
            )

            FacilityCard(
                emoji = "🏥",
                title = "Medical",
                subtitle = "Medical help",
                modifier = Modifier.weight(1f),
                onClick = {
                    onFacilityClick(FacilityType.MEDICAL)
                }
            )
        }

        Spacer(
            modifier = Modifier.height(10.dp)
        )

        // FOOD + TOILETS

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            FacilityCard(
                emoji = "🍛",
                title = "Food",
                subtitle = "Food points",
                modifier = Modifier.weight(1f),
                onClick = {
                    onFacilityClick(FacilityType.FOOD)
                }
            )

            FacilityCard(
                emoji = "🚻",
                title = "Toilets",
                subtitle = "Nearby toilets",
                modifier = Modifier.weight(1f),
                onClick = {
                    onFacilityClick(FacilityType.TOILET)
                }
            )
        }

        Spacer(
            modifier = Modifier.height(18.dp)
        )

        // -----------------------------------------------------
        // WARI ROUTE
        // -----------------------------------------------------

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable {
                    onRouteClick()
                },
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White
            ),
            elevation = CardDefaults.cardElevation(
                defaultElevation = 3.dp
            )
        ) {

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(18.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {

                Text(
                    text = "🗺️",
                    fontSize = 28.sp
                )

                Spacer(
                    modifier = Modifier.width(10.dp)
                )

                Column(
                    modifier = Modifier.weight(1f)
                ) {

                    Text(
                        text = "Wari Route",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Text(
                        text = "View route, villages & important stops",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }

                Text(
                    text = "›",
                    fontSize = 28.sp,
                    color = Color(0xFF4B2E83)
                )
            }
        }

        Spacer(
            modifier = Modifier.height(12.dp)
        )

        // -----------------------------------------------------
        // EMERGENCY
        // -----------------------------------------------------

        Button(
            onClick = {
                // Emergency functionality will be added later
            },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp)
        ) {

            Text(
                text = "🚨 EMERGENCY",
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(
            modifier = Modifier.weight(1f)
        )

        // -----------------------------------------------------
        // BOTTOM NAVIGATION
        // -----------------------------------------------------

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {

            Text(
                text = "⌂\nHome",
                fontSize = 12.sp
            )

            Text(
                text = "🗺\nRoute",
                fontSize = 12.sp,
                modifier = Modifier.clickable {
                    onRouteClick()
                }
            )

            Text(
                text = "ⓘ\nInfo",
                fontSize = 12.sp
            )
        }
    }
}


// ============================================================
// FACILITY CARD
// ============================================================

@Composable
fun FacilityCard(
    emoji: String,
    title: String,
    subtitle: String,
    modifier: Modifier,
    onClick: () -> Unit
) {

    Card(
        modifier = modifier.clickable {
            onClick()
        },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 3.dp
        )
    ) {

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            Text(
                text = emoji,
                fontSize = 30.sp
            )

            Spacer(
                modifier = Modifier.height(6.dp)
            )

            Text(
                text = title,
                fontWeight = FontWeight.Bold,
                fontSize = 15.sp
            )

            Text(
                text = subtitle,
                fontSize = 10.sp,
                color = Color.Gray
            )
        }
    }
}