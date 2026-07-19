/* Sortix - interfaz tipo explorador de archivos.
   Sidebar con Descargas + categorias + tus Temas; panel principal con el
   contenido real de la carpeta seleccionada; ajustes en un dialog aparte. */

const ICONS = {
    downloads: '<path d="M12 3v11m0 0-4-4m4 4 4-4M5 15v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-3"/>',
    image: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9.5" r="1.5"/><path d="m21 16-5-5-9 9"/>',
    video: '<rect x="3" y="5" width="14" height="14" rx="2"/><path d="m17 9 4-3v12l-4-3"/>',
    audio: '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    archive: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 4v5M9 13h2"/>',
    installer: '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    document: '<path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5"/>',
    pdf: '<path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5"/><text x="8" y="17" font-size="6" fill="currentColor" stroke="none">PDF</text>',
    other: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M3 7l3-4h5l2 3h8"/>',
    folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    topic: '<path d="m12 2 2.5 7.5H22l-6 4.5 2.3 7L12 16.8 5.7 21l2.3-7-6-4.5h7.5z"/>',
    home: '<path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.2a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.2a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.2a1.7 1.7 0 0 0-1.5 1z"/>',
    close: '<path d="M18 6 6 18M6 6l12 12"/>',
    trash: '<path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2m2 0-1 14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1L5 6"/>',
    chevron: '<path d="m9 18 6-6-6-6"/>',
};

function svgIcon(name, extraClass) {
    const body = ICONS[name] || ICONS.other;
    return `<svg class="icon ${extraClass || ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
}

const EXT_TO_ICON = {
    jpg: "image", jpeg: "image", png: "image", gif: "image", webp: "image", heic: "image",
    heif: "image", bmp: "image", tiff: "image", svg: "image", raw: "image",
    mp4: "video", mkv: "video", mov: "video", avi: "video", webm: "video", flv: "video", wmv: "video", m4v: "video",
    mp3: "audio", wav: "audio", flac: "audio", ogg: "audio", m4a: "audio", aac: "audio", wma: "audio",
    zip: "archive", rar: "archive", "7z": "archive", tar: "archive", gz: "archive", tgz: "archive", bz2: "archive", xz: "archive",
    exe: "installer", msi: "installer", deb: "installer", rpm: "installer", appimage: "installer", dmg: "installer", pkg: "installer", apk: "installer",
    pdf: "pdf",
    doc: "document", docx: "document", odt: "document", txt: "document", ppt: "document", pptx: "document", xls: "document", xlsx: "document", csv: "document", rtf: "document",
};

function iconForFile(ext) {
    return EXT_TO_ICON[ext] || "other";
}

function formatSize(bytes) {
    if (bytes == null) return "";
    if (bytes < 1024) return `${bytes} B`;
    const units = ["KB", "MB", "GB", "TB"];
    let value = bytes / 1024;
    let i = 0;
    while (value >= 1024 && i < units.length - 1) {
        value /= 1024;
        i++;
    }
    return `${value.toFixed(1)} ${units[i]}`;
}

// ---- estado ------------------------------------------------------------

let tree = [];
let currentPath = null; // null => vista raiz (tiles de categorias/temas)

const patrolToggle = document.getElementById("patrol-toggle");
const organizeBtn = document.getElementById("btn-organize");
const filesOrganizedEl = document.getElementById("files-organized-count");
const statusMessageEl = document.getElementById("status-message");
const breadcrumbsEl = document.getElementById("breadcrumbs");
const folderTreeEl = document.getElementById("folder-tree");
const fileGridEl = document.getElementById("file-grid");
const emptyStateEl = document.getElementById("empty-state");

const settingsModal = document.getElementById("settings-modal");
const topicsListEl = document.getElementById("topics-list");
const rulesListEl = document.getElementById("rules-list");
const topicForm = document.getElementById("topic-form");
const ruleForm = document.getElementById("rule-form");

let statusTimer = null;
function showStatus(message, isError = false) {
    statusMessageEl.textContent = message;
    statusMessageEl.classList.toggle("error", isError);
    clearTimeout(statusTimer);
    statusTimer = setTimeout(() => { statusMessageEl.textContent = ""; }, 6000);
}

async function fetchJSON(url, options) {
    const res = await fetch(url, options);
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || `Error ${res.status}`);
    }
    if (res.status === 204) return null;
    return res.json();
}

// ---- barra lateral / arbol ----------------------------------------------

async function loadTree() {
    tree = await fetchJSON("/api/tree");
    renderSidebar();
}

function renderSidebar() {
    folderTreeEl.innerHTML = "";

    const homeItem = document.createElement("li");
    homeItem.className = "tree-item" + (currentPath === null ? " active" : "");
    homeItem.innerHTML = `${svgIcon("home")}<span>Inicio</span>`;
    homeItem.addEventListener("click", () => navigateTo(null));
    folderTreeEl.appendChild(homeItem);

    for (const item of tree) {
        const li = document.createElement("li");
        li.className = "tree-item" + (currentPath === item.path ? " active" : "");
        li.innerHTML = `${svgIcon(item.icon)}<span>${escapeHtml(item.label)}</span>`;
        li.addEventListener("click", () => navigateTo(item.path));
        folderTreeEl.appendChild(li);
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ---- navegacion / breadcrumbs --------------------------------------------

function labelForPath(path) {
    const match = tree.find((item) => item.path === path);
    if (match) return match.label;
    const segments = path.split("/");
    return segments[segments.length - 1];
}

function renderBreadcrumbs() {
    breadcrumbsEl.innerHTML = "";

    const homeCrumb = document.createElement("button");
    homeCrumb.className = "crumb";
    homeCrumb.innerHTML = `${svgIcon("home")}<span>Inicio</span>`;
    homeCrumb.addEventListener("click", () => navigateTo(null));
    breadcrumbsEl.appendChild(homeCrumb);

    if (currentPath === null) return;

    const segments = currentPath.split("/");
    let accumulated = "";
    segments.forEach((segment, index) => {
        accumulated = accumulated ? `${accumulated}/${segment}` : segment;
        const sep = document.createElement("span");
        sep.className = "crumb-sep";
        sep.innerHTML = svgIcon("chevron");
        breadcrumbsEl.appendChild(sep);

        const crumb = document.createElement("button");
        crumb.className = "crumb";
        const isLast = index === segments.length - 1;
        crumb.textContent = labelForPath(accumulated);
        const target = accumulated;
        crumb.addEventListener("click", () => navigateTo(target));
        if (isLast) crumb.classList.add("current");
        breadcrumbsEl.appendChild(crumb);
    });
}

async function navigateTo(path) {
    currentPath = path;
    renderSidebar();
    renderBreadcrumbs();
    await renderContent();
}

// ---- contenido principal --------------------------------------------------

async function renderContent() {
    fileGridEl.innerHTML = "";
    emptyStateEl.hidden = true;

    if (currentPath === null) {
        renderRootTiles();
        return;
    }

    try {
        const data = await fetchJSON(`/api/browse?path=${encodeURIComponent(currentPath)}`);
        if (!data.exists || data.entries.length === 0) {
            emptyStateEl.hidden = false;
            return;
        }
        for (const entry of data.entries) {
            fileGridEl.appendChild(buildTile(entry));
        }
    } catch (err) {
        showStatus("No se pudo abrir esa carpeta.", true);
    }
}

function renderRootTiles() {
    for (const item of tree) {
        const tile = document.createElement("div");
        tile.className = "tile folder-tile";
        tile.innerHTML = `${svgIcon(item.icon, "tile-icon")}<span class="tile-name">${escapeHtml(item.label)}</span>`;
        tile.addEventListener("click", () => navigateTo(item.path));
        fileGridEl.appendChild(tile);
    }
}

function buildTile(entry) {
    const tile = document.createElement("div");
    if (entry.is_dir) {
        tile.className = "tile folder-tile";
        tile.innerHTML = `${svgIcon("folder", "tile-icon")}<span class="tile-name">${escapeHtml(entry.name)}</span>`;
        tile.addEventListener("click", () => navigateTo(entry.path));
    } else {
        tile.className = "tile file-tile";
        tile.title = `${entry.name} - ${formatSize(entry.size)} - ${entry.modified}`;
        tile.innerHTML = `${svgIcon(iconForFile(entry.ext), "tile-icon")}<span class="tile-name">${escapeHtml(entry.name)}</span><span class="tile-meta">${formatSize(entry.size)}</span>`;
    }
    return tile;
}

// ---- estado global: patrulla / stats --------------------------------------

async function refreshStatus() {
    try {
        const data = await fetchJSON("/api/status");
        patrolToggle.checked = data.active;
        filesOrganizedEl.textContent = data.files_organized;
    } catch (err) {
        showStatus("No se pudo contactar con Sortix.", true);
    }
}

patrolToggle.addEventListener("change", async () => {
    const desired = patrolToggle.checked;
    try {
        const data = await fetchJSON("/api/patrol/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ active: desired }),
        });
        patrolToggle.checked = data.active;
        showStatus(data.active ? "Patrulla activa: vigilando Descargas." : "Patrulla desactivada.");
    } catch (err) {
        patrolToggle.checked = !desired;
        showStatus("No se pudo cambiar la Patrulla Activa.", true);
    }
});

organizeBtn.addEventListener("click", async () => {
    organizeBtn.disabled = true;
    showStatus("Organizando...");
    try {
        const data = await fetchJSON("/api/organize-now", { method: "POST" });
        showStatus(`Listo: ${data.moved} archivo(s) organizado(s).`);
        await refreshStatus();
        await loadTree();
        if (currentPath !== null) await renderContent();
    } catch (err) {
        showStatus("Fallo al organizar la carpeta de descargas.", true);
    } finally {
        organizeBtn.disabled = false;
    }
});

// ---- ajustes: temas --------------------------------------------------------

async function refreshTopics() {
    const topics = await fetchJSON("/api/topics");
    topicsListEl.innerHTML = "";
    if (topics.length === 0) {
        topicsListEl.innerHTML = '<li class="empty">Aun no tienes ningun tema. Anade el primero abajo.</li>';
    }
    for (const topic of topics) {
        const li = document.createElement("li");
        li.innerHTML = `<div class="settings-item-main">
            <strong>${escapeHtml(topic.name)}</strong>
            <span class="muted">&rarr; ${escapeHtml(topic.destination)}</span>
            <span class="keywords">${topic.keywords.map(escapeHtml).join(", ")}</span>
        </div>`;
        const delBtn = document.createElement("button");
        delBtn.className = "icon-btn danger";
        delBtn.innerHTML = svgIcon("trash");
        delBtn.title = "Eliminar tema";
        delBtn.addEventListener("click", async () => {
            await fetchJSON(`/api/topics/${topic.id}`, { method: "DELETE" });
            await refreshTopics();
            await loadTree();
        });
        li.appendChild(delBtn);
        topicsListEl.appendChild(li);
    }
}

topicForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("topic-name").value.trim();
    const destination = document.getElementById("topic-destination").value.trim();
    const keywords = document.getElementById("topic-keywords").value.trim();
    if (!name || !destination || !keywords) return;
    try {
        await fetchJSON("/api/topics", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, destination, keywords }),
        });
        topicForm.reset();
        await refreshTopics();
        await loadTree();
        showStatus("Tema guardado.");
    } catch (err) {
        showStatus(err.message || "No se pudo guardar el tema.", true);
    }
});

// ---- ajustes: reglas por extension ------------------------------------------

async function refreshRules() {
    const rules = await fetchJSON("/api/rules");
    rulesListEl.innerHTML = "";
    if (rules.length === 0) {
        rulesListEl.innerHTML = '<li class="empty">No tienes reglas personalizadas todavia.</li>';
    }
    for (const rule of rules) {
        const li = document.createElement("li");
        li.innerHTML = `<div class="settings-item-main"><strong>.${escapeHtml(rule.extension)}</strong> <span class="muted">&rarr; ${escapeHtml(rule.destination)}</span></div>`;
        const delBtn = document.createElement("button");
        delBtn.className = "icon-btn danger";
        delBtn.innerHTML = svgIcon("trash");
        delBtn.title = "Eliminar regla";
        delBtn.addEventListener("click", async () => {
            await fetchJSON(`/api/rules/${rule.id}`, { method: "DELETE" });
            await refreshRules();
        });
        li.appendChild(delBtn);
        rulesListEl.appendChild(li);
    }
}

ruleForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const extension = document.getElementById("rule-extension").value.trim();
    const destination = document.getElementById("rule-destination").value.trim();
    if (!extension || !destination) return;
    try {
        await fetchJSON("/api/rules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ extension, destination }),
        });
        ruleForm.reset();
        await refreshRules();
        showStatus("Regla guardada.");
    } catch (err) {
        showStatus(err.message || "No se pudo guardar la regla.", true);
    }
});

// ---- modal de ajustes --------------------------------------------------------

document.getElementById("btn-settings").innerHTML = svgIcon("settings");
document.getElementById("btn-close-settings").innerHTML = svgIcon("close");

document.getElementById("btn-settings").addEventListener("click", () => openSettings());
document.getElementById("btn-close-settings").addEventListener("click", () => settingsModal.close());

for (const tabBtn of document.querySelectorAll(".tab-btn")) {
    tabBtn.addEventListener("click", () => {
        for (const b of document.querySelectorAll(".tab-btn")) b.classList.remove("active");
        for (const p of document.querySelectorAll(".tab-panel")) p.hidden = true;
        tabBtn.classList.add("active");
        document.getElementById(`tab-${tabBtn.dataset.tab}`).hidden = false;
    });
}

function openSettings(tab) {
    if (tab) {
        document.querySelector(`.tab-btn[data-tab="${tab}"]`)?.click();
    }
    settingsModal.showModal();
}

// ---- arranque ------------------------------------------------------------

async function init() {
    await Promise.all([refreshStatus(), loadTree(), refreshTopics(), refreshRules()]);
    renderBreadcrumbs();
    await renderContent();
    setInterval(refreshStatus, 5000);

    const onboarded = localStorage.getItem("sortix_onboarded");
    const topicsEmpty = topicsListEl.querySelector(".empty");
    const rulesEmpty = rulesListEl.querySelector(".empty");
    if (!onboarded && topicsEmpty && rulesEmpty) {
        openSettings("topics");
        showStatus("Bienvenido: define tus primeros Temas (banco, gimnasio, apps...) y listo, Sortix se encarga solo a partir de ahora.");
    }
    settingsModal.addEventListener("close", () => localStorage.setItem("sortix_onboarded", "1"));
}

init();
