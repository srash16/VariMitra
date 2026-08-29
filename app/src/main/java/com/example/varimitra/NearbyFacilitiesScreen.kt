package com.example.varimitra

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

enum class FacilityType {
    WATER,
    MEDICAL,
    FOOD,
    TOILET
}

data class DemoFacility(
    val name: String,
    val description: String,
    val distance: String
)

@Composable
fun NearbyFacilitiesScreen(
    type: FacilityType,
    onBack: () -> Unit
) {

    /*
     * This makes the Android system back button work
     * even while this screen is displayed.
     */
    BackHandler {
        onBack()
    }

    val title = when (type) {

        FacilityType.WATER ->
            "Nearby Water"

        FacilityType.MEDICAL ->
            "Nearby Medical"

        FacilityType.FOOD ->
            "Nearby Food"

        FacilityType.TOILET ->
            "Nearby Toilets"
    }

    val icon = when (type) {

        FacilityType.WATER ->
            "💧"

        FacilityType.MEDICAL ->
            "🏥"

        FacilityType.FOOD ->
            "🍛"

        FacilityType.TOILET ->
            "🚻"
    }

    val facilities = when (type) {

        FacilityType.WATER -> listOf(

            DemoFacility(
                name = "Water Point 1",
                description = "Drinking water available",
                distance = "0.3 km"
            ),

            DemoFacility(
                name = "Water Point 2",
                description = "Clean drinking water",
                distance = "0.7 km"
            ),

            DemoFacility(
                name = "Water Point 3",
                description = "Water refill facility",
                distance = "1.1 km"
            ),

            DemoFacility(
                name = "Water Point 4",
                description = "Drinking water and refill",
                distance = "1.5 km"
            )
        )

        FacilityType.MEDICAL -> listOf(

            DemoFacility(
                name = "Medical Camp 1",
                description = "First aid and basic medical support",
                distance = "0.5 km"
            ),

            DemoFacility(
                name = "Medical Camp 2",
                description = "Doctor and first aid available",
                distance = "1.0 km"
            ),

            DemoFacility(
                name = "First Aid Point",
                description = "Emergency first aid",
                distance = "1.4 km"
            )
        )

        FacilityType.FOOD -> listOf(

            DemoFacility(
                name = "Community Meal 1",
                description = "Free community meal",
                distance = "0.4 km"
            ),

            DemoFacility(
                name = "Food Point 2",
                description = "Food and refreshments",
                distance = "0.9 km"
            ),

            DemoFacility(
                name = "Community Kitchen",
                description = "Community kitchen",
                distance = "1.3 km"
            )
        )

        FacilityType.TOILET -> listOf(

            DemoFacility(
                name = "Toilet Point 1",
                description = "Public toilet facility",
                distance = "0.2 km"
            ),

            DemoFacility(
                name = "Toilet Point 2",
                description = "Clean toilet facility",
                distance = "0.8 km"
            ),

            DemoFacility(
                name = "Toilet Point 3",
                description = "Public toilet facility",
                distance = "1.2 km"
            )
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8F7F3))
    ) {

        // ---------------------------------------------------------
        // TOP BAR
        // ---------------------------------------------------------

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 8.dp,
                    vertical = 10.dp
                ),
            verticalAlignment = Alignment.CenterVertically
        ) {

            TextButton(
                onClick = {
                    onBack()
                }
            ) {

                Text(
                    text = "← Back",
                    color = Color(0xFF4B2E83),
                    fontSize = 15.sp
                )
            }

            Text(
                text = "$icon  $title",
                fontSize = 21.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF4B2E83)
            )
        }

        // ---------------------------------------------------------
        // RESULT COUNT
        // ---------------------------------------------------------

        Text(
            text = "${facilities.size} facilities found nearby",
            modifier = Modifier.padding(
                horizontal = 18.dp,
                vertical = 4.dp
            ),
            color = Color.Gray,
            fontSize = 14.sp
        )

        Spacer(
            modifier = Modifier.height(8.dp)
        )

        // ---------------------------------------------------------
        // FACILITY LIST
        // ---------------------------------------------------------

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            items(
                items = facilities
            ) { facility ->

                FacilityResultCard(
                    facility = facility,
                    icon = icon
                )
            }

            item {

                Spacer(
                    modifier = Modifier.height(20.dp)
                )
            }
        }
    }
}

@Composable
fun FacilityResultCard(
    facility: DemoFacility,
    icon: String
) {

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 3.dp
        )
    ) {

        Column(
            modifier = Modifier.padding(18.dp)
        ) {

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {

                Text(
                    text = icon,
                    fontSize = 35.sp
                )

                Spacer(
                    modifier = Modifier.width(12.dp)
                )

                Column(
                    modifier = Modifier.weight(1f)
                ) {

                    Text(
                        text = facility.name,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF4B2E83)
                    )

                    Spacer(
                        modifier = Modifier.height(4.dp)
                    )

                    Text(
                        text = facility.description,
                        fontSize = 13.sp,
                        color = Color.Gray
                    )

                    Spacer(
                        modifier = Modifier.height(4.dp)
                    )

                    Text(
                        text = "📍 ${facility.distance} away",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            Spacer(
                modifier = Modifier.height(12.dp)
            )

            Button(
                onClick = {
                    // Details functionality will be added later
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(10.dp)
            ) {

                Text(
                    text = "View Details"
                )
            }
        }
    }
}