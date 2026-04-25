(function () {
    const storageKey = "garden-city-theme";
    const validThemes = ["theme-light", "theme-spring", "theme-summer", "theme-autumn", "theme-winter", "theme-dark"];
    const mobileBreakpoint = 1024;

    function getStoredTheme() {
        const savedTheme = window.localStorage.getItem(storageKey);
        return validThemes.includes(savedTheme) ? savedTheme : "theme-spring";
    }

    function setSidebarState(isOpen) {
        document.body.classList.toggle("sidebar-open", isOpen);
    }

    function hydrateResponsiveTables() {
        document.querySelectorAll(".app-table").forEach(function (table) {
            const labels = Array.from(table.querySelectorAll("thead th")).map(function (cell) {
                return cell.textContent.trim();
            });

            table.querySelectorAll("tbody tr").forEach(function (row) {
                const cells = Array.from(row.children);

                if (cells.length === 1 && cells[0].hasAttribute("colspan")) {
                    cells[0].setAttribute("data-label", "");
                    return;
                }

                cells.forEach(function (cell, index) {
                    if (cell.tagName === "TD") {
                        cell.setAttribute("data-label", labels[index] || "");
                    }
                });
            });
        });
    }

    function applyTheme(themeName, options) {
        const settings = Object.assign(
            {
                persist: true
            },
            options || {}
        );

        validThemes.forEach(function (theme) {
            document.body.classList.remove(theme);
        });
        document.body.classList.add(themeName);

        document.querySelectorAll(".theme-swatch").forEach(function (button) {
            button.classList.toggle("is-active", button.dataset.theme === themeName);
        });

        if (settings.persist) {
            window.localStorage.setItem(storageKey, themeName);
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        applyTheme(getStoredTheme(), { persist: false });
        hydrateResponsiveTables();

        document.querySelectorAll(".theme-swatch").forEach(function (button) {
            button.addEventListener("click", function () {
                applyTheme(button.dataset.theme, { persist: true });
            });
        });

        document.querySelectorAll("[data-sidebar-open]").forEach(function (button) {
            button.addEventListener("click", function () {
                setSidebarState(true);
            });
        });

        document.querySelectorAll("[data-sidebar-close]").forEach(function (button) {
            button.addEventListener("click", function () {
                setSidebarState(false);
            });
        });

        document.querySelectorAll(".sidebar-nav a").forEach(function (link) {
            link.addEventListener("click", function () {
                if (window.innerWidth <= mobileBreakpoint) {
                    setSidebarState(false);
                }
            });
        });

        window.addEventListener("resize", function () {
            if (window.innerWidth > mobileBreakpoint) {
                setSidebarState(false);
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                setSidebarState(false);
            }
        });
    });
})();
