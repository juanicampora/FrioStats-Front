function toggleFullScreenJS() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => {
            localStorage.setItem('fullscreen', 'true');
            console.log('Fullscreen SETEADA EN TRUEEEEEE');
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen().then(() => {
                localStorage.setItem('fullscreen', 'false');
            });
        }
    }
}