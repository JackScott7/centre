const body = document.body;
const menuButton = document.querySelector(".menu-button");
const navigation = document.querySelector("#site-navigation");
const navigationScrim = document.querySelector(".nav-scrim");
const navigationLinks = [...document.querySelectorAll(".nav-link")];
const observedSections = [...document.querySelectorAll(".observed-section")];
const progressBar = document.querySelector(".reading-progress span");
const copyToast = document.querySelector(".copy-toast");
const themeToggle = document.querySelector(".theme-toggle");
const versionSpan = document.querySelector(".version-pill");

let toastTimer;
const PACKAGE_URL = "https://centre-api.syntaxly.xyz/version"

async function getPackageVersion() {
    try {
        const response = await fetch(PACKAGE_URL, {
            method: "GET",
            headers: {
                Accept: "application/json",
            },
            mode: "cors",
            redirect: "follow",
        });

        if (!response.ok) {
            throw new Error(`API returned HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.success && data.version) {
            versionSpan.textContent = `v${data.version}`;
        }
    } catch (error) {
        console.error("Failed to fetch Centre version:", error);
        versionSpan.textContent = "";
    }
}

getPackageVersion();

function setTheme(theme, persist = false) {
    const nextTheme = theme === "light" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;

    const nextLabel = nextTheme === "dark"
        ? "Switch to light theme"
        : "Switch to dark theme";

    themeToggle.setAttribute("aria-label", nextLabel);
    themeToggle.setAttribute("title", nextLabel);

    if (persist) {
        try {
            localStorage.setItem("centre-theme", nextTheme);
        } catch (error) {
            // The selected theme still applies for the current page session.
        }
    }
}

setTheme(document.documentElement.dataset.theme);

themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.dataset.theme;
    setTheme(currentTheme === "dark" ? "light" : "dark", true);
});

function setNavigationOpen(open) {
    body.classList.toggle("nav-open", open);
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute(
        "aria-label",
        open ? "Close documentation navigation" : "Open documentation navigation"
    );
}

function closeNavigation() {
    setNavigationOpen(false);
}

function showCopyFeedback(button) {
    const originalText = button.textContent;
    button.textContent = "Copied";
    copyToast.classList.add("is-visible");

    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => {
        button.textContent = originalText;
        copyToast.classList.remove("is-visible");
    }, 1600);
}

async function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
        return;
    }

    const temporaryInput = document.createElement("textarea");
    temporaryInput.value = value;
    temporaryInput.setAttribute("readonly", "");
    temporaryInput.style.position = "fixed";
    temporaryInput.style.opacity = "0";
    document.body.appendChild(temporaryInput);
    temporaryInput.select();
    document.execCommand("copy");
    temporaryInput.remove();
}

menuButton.addEventListener("click", () => {
    setNavigationOpen(!body.classList.contains("nav-open"));
});

navigationScrim.addEventListener("click", closeNavigation);

navigationLinks.forEach((link) => {
    link.addEventListener("click", closeNavigation);
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && body.classList.contains("nav-open")) {
        closeNavigation();
        menuButton.focus();
    }
});

document.querySelectorAll("[data-copy], [data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
        const targetSelector = button.dataset.copyTarget;
        const target = targetSelector ? document.querySelector(targetSelector) : null;
        const value = target ? target.textContent.trim() : button.dataset.copy;

        try {
            await copyText(value);
            showCopyFeedback(button);
        } catch (error) {
            copyToast.textContent = "Copy failed — select the command manually";
            copyToast.classList.add("is-visible");
            window.clearTimeout(toastTimer);
            toastTimer = window.setTimeout(() => {
                copyToast.classList.remove("is-visible");
                copyToast.textContent = "Copied to clipboard";
            }, 2200);
            console.error("Unable to copy text", error);
        }
    });
});

const sectionObserver = new IntersectionObserver(
    (entries) => {
        const visibleEntry = entries
            .filter((entry) => entry.isIntersecting)
            .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (!visibleEntry) {
            return;
        }

        navigationLinks.forEach((link) => {
            const active = link.getAttribute("href") === `#${visibleEntry.target.id}`;
            link.classList.toggle("is-active", active);
            if (active) {
                link.setAttribute("aria-current", "location");
            } else {
                link.removeAttribute("aria-current");
            }
        });
    },
    {
        rootMargin: "-18% 0px -68% 0px",
        threshold: [0, 0.1, 0.35]
    }
);

observedSections.forEach((section) => sectionObserver.observe(section));

function updateReadingProgress() {
    const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollableHeight > 0 ? window.scrollY / scrollableHeight : 0;
    progressBar.style.width = `${Math.min(1, Math.max(0, progress)) * 100}%`;
}

window.addEventListener("scroll", updateReadingProgress, {passive: true});
window.addEventListener("resize", () => {
    updateReadingProgress();
    if (window.innerWidth > 820) {
        closeNavigation();
    }
});

updateReadingProgress();
