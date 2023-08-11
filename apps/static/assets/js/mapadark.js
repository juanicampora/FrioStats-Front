var customIcon = L.icon({
    iconUrl: 'static/assets/images/pinpersonalizado.png',
    iconSize: [31, 46], // Tamaño del icono
    iconAnchor: [16, 32], // Punto de anclaje del icono
    popupAnchor: [0, -32] // Punto de anclaje del popup si lo usas
});
var map = L.map('map', {zoomControl: false,}, {attributionControl: false,}).setView([-32.958313059583254, -60.670903263595605], 13);
if (localStorage.getItem("theme") === "dark") {    
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        className: 'map-tiles'
    }).addTo(map);
} else {
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}
map.options.update({
    'attributionControl': False
})