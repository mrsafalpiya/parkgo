const copy =
  "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>";
const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const layer = L.tileLayer(url, {
  attribution: copy,
});
const map = L.map("map", {
  layers: [layer],
});
const markerGroup = L.layerGroup().addTo(map);
const greenIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});
const markers = JSON.parse(document.getElementById("markers-data").textContent);

// Selected location variable and handler
let selectedLocationId = document.getElementById("selected-location-id");
function selectLocation(id, location) {
  selectedLocationId.value = String(id);
  document.getElementById("location-selected").innerHTML =
    "Location selected: <span style='font-weight: 600'>" + location + "</span>";
  renderMap();

  // Update information in the "Show parking spaces" modal
  const selectedLocationDetails = markers.features.find(
    (l) => l.properties.pk == id
  ).properties;
  document.getElementById("selected-place-image").src =
    "/media/" + selectedLocationDetails.photo;
  document.getElementById("selected-place-name").innerText =
    selectedLocationDetails.parking_name;
  document.getElementById("selected-place-location").innerText =
    selectedLocationDetails.location_name;
  document.getElementById(
    "selected-place-price"
  ).innerText = `Rs. ${selectedLocationDetails.price}`;
  document.getElementById("slots").max = String(place_spaces_count[id]);
}

// Here the `filter` argument if is undefined, no filter will be applied.
// Else the marker location will be filtered.
function renderMap(filter) {
  markerGroup.clearLayers();
  if (filter != undefined && filter.trim() != "") {
    markers.features = markers.features.filter((f) =>
      `${f.properties.location_name} ${f.properties.parking_name}`
        .toLowerCase()
        .includes(filter.toLowerCase())
    );
  }
  const feature = L.geoJSON(markers).bindPopup(function (layer) {
    const location = `${layer.feature.properties.parking_name}, ${layer.feature.properties.location_name}`;
    return `<div class="map-popup">
                <p>${location}</p>
                <button class="map-popup-button" type="button" onclick="selectLocation(${layer.feature.properties.pk}, '${location}')">Select</button>
              </div>`;
  });

  // Make the icon of the selected marker as green (if a location is selected)
  if (selectedLocationId.value != undefined) {
    for (const layer of Object.values(feature._layers)) {
      if (layer.feature.properties.pk == selectedLocationId.value) {
        layer.options.icon = greenIcon;
      }
    }
  }

  feature.addTo(markerGroup);
  map.fitBounds(feature.getBounds(), {
    padding: [100, 100],
  });
}
renderMap(); // Render the map on the first render of the webpage
