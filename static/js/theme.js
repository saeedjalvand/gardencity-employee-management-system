function applyTheme(themeName) {
    document.body.classList.remove('theme-dark', 'theme-forest', 'theme-sunset', 'theme-ocean');

    if (themeName && themeName !== 'default') {
        document.body.classList.add(themeName);
    }

    localStorage.setItem('siteTheme', themeName || 'default');

    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.value = themeName || 'default';
    }
}

function initTheme() {
    const savedTheme = localStorage.getItem('siteTheme') || 'default';
    applyTheme(savedTheme);
}

window.addEventListener('DOMContentLoaded', function () {
    initTheme();
});