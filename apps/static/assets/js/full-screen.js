function toggleFullScreenJS() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => {
            localStorage.setItem('fullscreen', 'true');
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen().then(() => {
                localStorage.setItem('fullscreen', 'false');
            });
        }
    }
}