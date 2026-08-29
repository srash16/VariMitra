package com.example.varimitra

import android.content.Context
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
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker


// ============================================================
// MAP FACILITY DATA
// ============================================================

data class MapFacility(
    val name: String,
    val type: FacilityType,
    val latitude: Double,
    val longitude: Double,
    val distance: String
)


// ============================================================
// MAP SCREEN
// ============================================================

@Composable
fun MapScreen(
    onBack: () -> Unit
) {

    val context = LocalContext.current

    // --------------------------------------------------------
    // DEMO FACILITIES
    // --------------------------------------------------------

    val mapFacilities = remember {

        listOf(

            // WATER
            MapFacility(
                name = "Water Point 1",
                type = FacilityType.WATER,
                latitude = 17.6750,
                longitude = 75.9060,
                distance = "0.3 km"
            ),

            MapFacility(
                name = "Water Point 2",
                type = FacilityType.WATER,
                latitude = 17.6780,
                longitude = 75.9100,
                distance = "0.7 km"
            ),

            MapFacility(
                name = "Water Point 3",
                type = FacilityType.WATER,
                latitude = 17.6745,
                longitude = 75.9125,
                distance = "1.1 km"
            ),

            // MEDICAL
            MapFacility(
                name = "Medical Camp",
                type = FacilityType.MEDICAL,
                latitude = 17.6810,
                longitude = 75.9040,
                distance = "0.5 km"
            ),

            MapFacility(
                name = "First Aid Centre",
                type = FacilityType.MEDICAL,
                latitude = 17.6795,
                longitude = 75.9075,
                distance = "0.9 km"
            ),

            // FOOD
            MapFacility(
                name = "Community Food Point",
                type = FacilityType.FOOD,
                latitude = 17.6730,
                longitude = 75.9120,
                distance = "0.8 km"
            ),

            MapFacility(
                name = "Community Kitchen",
                type = FacilityType.FOOD,
                latitude = 17.6760,
                longitude = 75.9140,
                distance = "1.0 km"
            ),

            // TOILETS
            MapFacility(
                name = "Public Toilet",
                type = FacilityType.TOILET,
                latitude = 17.6790,
                longitude = 75.9150,
                distance = "0.6 km"
            ),

            MapFacility(
                name = "Toilet Point 2",
                type = FacilityType.TOILET,
                latitude = 17.6740,
                longitude = 75.9090,
                distance = "1.2 km"
            )
        )
    }

    // --------------------------------------------------------
    // SELECTED FILTER
    // --------------------------------------------------------

    var selectedType by remember {
        mutableStateOf<FacilityType?>(null)
    }

    // --------------------------------------------------------
    // FILTERED FACILITIES
    // --------------------------------------------------------

    val filteredFacilities = if (selectedType == null) {

        mapFacilities

    } else {

        mapFacilities.filter {
            it.type == selectedType
        }
    }

    // --------------------------------------------------------
    // SCREEN
    // --------------------------------------------------------

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Color(0xFFF8F7F3)
            )
    ) {

        // ====================================================
        // TOP BAR
        // ====================================================

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 8.dp,
                    vertical = 10.dp
                ),
            verticalAlignment = Alignment.CenterVertically
        ) {

            Button(
                onClick = onBack
            ) {

                Text(
                    text = "← Back"
                )
            }

            Spacer(
                modifier = Modifier.width(10.dp)
            )

            Text(
                text = "🗺️ Wari Route",
                fontSize = 21.sp,
                color = Color(0xFF4B2E83)
            )
        }


        // ====================================================
        // WATER + MEDICAL FILTERS
        // ====================================================

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 10.dp,
                    vertical = 6.dp
                ),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {

            FilterChip(
                selected = selectedType == FacilityType.WATER,

                onClick = {

                    selectedType =
                        if (selectedType == FacilityType.WATER) {

                            null

                        } else {

                            FacilityType.WATER
                        }
                },

                label = {
                    Text(
                        text = "💧 Water"
                    )
                }
            )


            FilterChip(
                selected = selectedType == FacilityType.MEDICAL,

                onClick = {

                    selectedType =
                        if (selectedType == FacilityType.MEDICAL) {

                            null

                        } else {

                            FacilityType.MEDICAL
                        }
                },

                label = {
                    Text(
                        text = "🏥 Medical"
                    )
                }
            )
        }


        // ====================================================
        // FOOD + TOILET FILTERS
        // ====================================================

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 10.dp,
                    vertical = 4.dp
                ),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {

            FilterChip(
                selected = selectedType == FacilityType.FOOD,

                onClick = {

                    selectedType =
                        if (selectedType == FacilityType.FOOD) {

                            null

                        } else {

                            FacilityType.FOOD
                        }
                },

                label = {
                    Text(
                        text = "🍛 Food"
                    )
                }
            )


            FilterChip(
                selected = selectedType == FacilityType.TOILET,

                onClick = {

                    selectedType =
                        if (selectedType == FacilityType.TOILET) {

                            null

                        } else {

                            FacilityType.TOILET
                        }
                },

                label = {
                    Text(
                        text = "🚻 Toilet"
                    )
                }
            )
        }


        Spacer(
            modifier = Modifier.height(4.dp)
        )


        // ====================================================
        // MAP
        // ====================================================

        AndroidView(

            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),

            factory = { ctx ->

                createMapView(
                    context = ctx,
                    facilities = mapFacilities
                )
            },

            update = { mapView ->

                updateMapMarkers(
                    mapView = mapView,
                    facilities = mapFacilities,
                    selectedType = selectedType
                )
            }
        )


        // ====================================================
        // OPENSTREETMAP ATTRIBUTION
        // ====================================================

        Text(
            text = "© OpenStreetMap contributors",
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 12.dp,
                    vertical = 3.dp
                ),
            color = Color.Gray,
            fontSize = 10.sp
        )


        // ====================================================
        // RESULT COUNT
        // ====================================================

        Text(
            text = "${filteredFacilities.size} facilities shown on map",

            modifier = Modifier.padding(
                horizontal = 16.dp,
                vertical = 7.dp
            ),

            color = Color.Gray,
            fontSize = 13.sp
        )
    }
}


// ============================================================
// CREATE MAP VIEW
// ============================================================

private fun createMapView(
    context: Context,
    facilities: List<MapFacility>
): MapView {

    // --------------------------------------------------------
    // OSM CONFIGURATION
    // --------------------------------------------------------

    Configuration.getInstance().load(
        context,
        context.getSharedPreferences(
            "osmdroid",
            Context.MODE_PRIVATE
        )
    )

    // Important:
    // Identify the application to the tile server.

    Configuration.getInstance().userAgentValue =
        "VariMitra/1.0 (Android; com.example.varimitra)"


    // --------------------------------------------------------
    // CREATE MAP
    // --------------------------------------------------------

    val mapView = MapView(context)


    // --------------------------------------------------------
    // MAP TILE SOURCE
    // --------------------------------------------------------

    mapView.setTileSource(
        TileSourceFactory.MAPNIK
    )


    // --------------------------------------------------------
    // MAP CONTROLS
    // --------------------------------------------------------

    mapView.setMultiTouchControls(
        true
    )

    mapView.isTilesScaledToDpi =
        true


    // --------------------------------------------------------
    // INITIAL ZOOM
    // --------------------------------------------------------

    mapView.controller.setZoom(
        14.0
    )


    // --------------------------------------------------------
    // DEMO CENTER
    // --------------------------------------------------------
    // Pandharpur area

    val center = GeoPoint(
        17.6770,
        75.9080
    )

    mapView.controller.setCenter(
        center
    )


    // --------------------------------------------------------
    // ADD FACILITY MARKERS
    // --------------------------------------------------------

    updateMapMarkers(
        mapView = mapView,
        facilities = facilities,
        selectedType = null
    )


    return mapView
}


// ============================================================
// UPDATE MAP MARKERS
// ============================================================

private fun updateMapMarkers(
    mapView: MapView,
    facilities: List<MapFacility>,
    selectedType: FacilityType?
) {

    // --------------------------------------------------------
    // REMOVE OLD MARKERS
    // --------------------------------------------------------

    mapView.overlays.clear()


    // --------------------------------------------------------
    // FILTER FACILITIES
    // --------------------------------------------------------

    val visibleFacilities =

        if (selectedType == null) {

            facilities

        } else {

            facilities.filter {
                it.type == selectedType
            }
        }


    // --------------------------------------------------------
    // ADD MARKERS
    // --------------------------------------------------------

    for (facility in visibleFacilities) {

        val marker = Marker(
            mapView
        )


        // Position
        marker.position = GeoPoint(
            facility.latitude,
            facility.longitude
        )


        // Marker title
        marker.title =
            "${facilityIcon(facility.type)} ${facility.name}"


        // Marker information
        marker.snippet =
            "${facility.distance} away"


        // Marker anchor
        marker.setAnchor(
            Marker.ANCHOR_CENTER,
            Marker.ANCHOR_BOTTOM
        )


        // Add marker
        mapView.overlays.add(
            marker
        )
    }


    // --------------------------------------------------------
    // REFRESH MAP
    // --------------------------------------------------------

    mapView.invalidate()
}


// ============================================================
// FACILITY ICON
// ============================================================

private fun facilityIcon(
    type: FacilityType
): String {

    return when (type) {

        FacilityType.WATER ->
            "💧"

        FacilityType.MEDICAL ->
            "🏥"

        FacilityType.FOOD ->
            "🍛"

        FacilityType.TOILET ->
            "🚻"
    }
}