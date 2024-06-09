const themeSwitch = document.getElementById("theme-switch"); //our switch element
const themeIndicator = document.getElementById("theme-indicator"); //our theme icon
const page = document.body; //our document body


//To avoid any confusion, all variables are placed inside arrays.
// We will later use indexes to access these values.
const themeStates = ["light", "dark"]
const indicators = ["icon-moon", "icon-sun"]

//Now we check our local storage and get the value of our theme.
let currentTheme = localStorage.getItem("theme");

//This is a helper function to set the theme.
//We will pass in the index of our array.
function setTheme(theme) {
    localStorage.setItem("theme", themeStates[theme])
}

//This is a helper function to set the icon.
//We will pass in the index of our array.
function setIndicator(theme) {
    //We remove all possible classes.
    themeIndicator.classList.remove(indicators[0])
    themeIndicator.classList.remove(indicators[1])
    //then we add our desired class name.
    themeIndicator.classList.add(indicators[theme])
}

//This is a helper function to set the page theme class.
//We will pass in the index of our array.
function setPage(theme) {
    //We will remove the existing classes,
    // and then we will add our current theme class.
    if (theme === 1) {
        page.classList.add("dark")
    } else {
        page.classList.remove("dark")
    }

}

// We'll check for the value and set our
if (currentTheme === null) {
    localStorage.setItem("theme", themeStates[0])
    setIndicator(0)
    setPage(0)
    themeSwitch.checked = true;
}
if (currentTheme === themeStates[0]) {
    setIndicator(0)
    setPage(0)
    themeSwitch.checked = true;
}
if (currentTheme === themeStates[1]) {
    setIndicator(1)
    setPage(1)
    themeSwitch.checked = false;
}

//We handle our user interaction here.
themeSwitch.addEventListener('change', function () {
    const currentPath = window.location.pathname;
    const desiredPathRegex = /^\/index\/?$/;
    const isMatchingPath = desiredPathRegex.test(currentPath);
    if (!(isMatchingPath)) {
        const desiredPathRegex2 = /^\/graficos\/.*/;
        const isMatchingPath2 = desiredPathRegex2.test(currentPath);
        const desiredPathRegex3 = /^\/reportes\/?$/;
        const isMatchingPath3 = desiredPathRegex3.test(currentPath);
        if (isMatchingPath2 || isMatchingPath3) {
            console.log('ENTROOOOOOOOOOOOOOOOO');
            location.reload();
        }
    }
    if (this.checked) {
        setTheme(0);
        setIndicator(0);
        setPage(0);
        if (isMatchingPath) {
            // Remueve la capa existente del mapa
            map.eachLayer(function (layer) {
                if (layer instanceof L.TileLayer) {
                    map.removeLayer(layer);
                }
            });
            // Agrega la nueva capa con el modo claro al mapa
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(map);
        }
    } else {
        setTheme(1);
        setIndicator(1);
        setPage(1);
        if (isMatchingPath) {
            // Remueve la capa existente del mapa
            map.eachLayer(function (layer) {
                if (layer instanceof L.TileLayer) {
                    map.removeLayer(layer);
                }
            });
            // Agrega la nueva capa con el modo oscuro al mapa
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                className: 'map-tiles'
            }).addTo(map);
        }
    }
});
