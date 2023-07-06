if (localStorage.getItem("theme") === "dark") {
    var map = L.map('map').setView([-32.958313059583254, -60.670903263595605], 13);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        className: 'map-tiles'
    }).addTo(map);
} else {
    var map = L.map('map').setView([-32.958313059583254, -60.670903263595605], 13);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}
