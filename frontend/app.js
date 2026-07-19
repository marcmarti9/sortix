/* Sortix - interfaz tipo explorador de archivos.
   Sidebar con Descargas + categorias + tus Temas; panel principal con el
   contenido real de la carpeta seleccionada; ajustes en un dialog aparte. */

const TRANSLATIONS = {
    es: {
        patrol_label: "Patrulla Activa",
        patrol_title: "Vigilar Descargas en tiempo real",
        organize_btn: "Organizar ahora",
        settings_title: "Ajustes",
        organized_count_prefix: "Archivos organizados",
        empty_state: "Esta carpeta está vacía (o aún no se ha creado).",
        settings_title_modal: "Ajustes de Sortix",
        close_title: "Cerrar",
        tab_topics: "Temas",
        tab_rules: "Reglas por extensión",
        topics_hint: "Un Tema es cualquier cosa que quieras agrupar: tu banco, el gimnasio, una app concreta, facturas de un proveedor... Sortix mira el nombre del archivo y, si hace falta, su contenido, buscando estas palabras clave.",
        topic_name_label: "Nombre del tema",
        topic_name_placeholder: "ej. Banco, Gimnasio, Netflix",
        topic_dest_label: "Carpeta destino",
        topic_dest_placeholder: "ej. Documents/Banco",
        topic_keywords_label: "Palabras clave (separadas por comas)",
        topic_keywords_placeholder: "ej. banco, extracto, iban",
        add_topic_btn: "Añadir tema",
        rules_hint: "Las reglas por extensión son más simples y siempre ganan a la clasificación automática: todo archivo con esa extensión va directo a la carpeta que indiques.",
        rule_ext_label: "Extensión",
        rule_ext_placeholder: "ej. pdf",
        rule_dest_label: "Carpeta destino",
        rule_dest_placeholder: "ej. Documents/Facturas",
        add_rule_btn: "Añadir regla",
        
        home: "Inicio",
        downloads: "Descargas",
        images: "Imágenes",
        videos: "Videos",
        music: "Música",
        compressed: "Comprimidos",
        installers: "Instaladores",
        documents: "Documentos",
        other: "Otros",
        
        status_conn_error: "No se pudo contactar con Sortix.",
        status_patrol_active: "Patrulla activa: vigilando Descargas.",
        status_patrol_inactive: "Patrulla desactivada.",
        status_patrol_error: "No se pudo cambiar la Patrulla Activa.",
        status_organizing: "Organizando...",
        status_organized_done: "Listo: {moved} archivo(s) organizado(s).",
        status_organize_error: "Fallo al organizar la carpeta de descargas.",
        status_folder_error: "No se pudo abrir esa carpeta.",
        
        topics_empty: "Aún no tienes ningún tema. Añade el primero abajo.",
        rules_empty: "No tienes reglas personalizadas todavía.",
        delete_topic_title: "Eliminar tema",
        delete_rule_title: "Eliminar regla",
        status_topic_saved: "Tema guardado.",
        status_topic_save_error: "No se pudo guardar el tema.",
        status_rule_saved: "Regla guardada.",
        status_rule_save_error: "No se pudo guardar la regla.",
        theme_title: "Cambiar tema",
        
        welcome_message: "Bienvenido: define tus primeros Temas (banco, gimnasio, apps...) y listo, Sortix se encarga solo a partir de ahora."
    },
    en: {
        patrol_label: "Active Patrol",
        patrol_title: "Watch Downloads in real time",
        organize_btn: "Organize now",
        settings_title: "Settings",
        organized_count_prefix: "Organized files",
        empty_state: "This folder is empty (or has not been created yet).",
        settings_title_modal: "Sortix Settings",
        close_title: "Close",
        tab_topics: "Topics",
        tab_rules: "Rules by Extension",
        topics_hint: "A Topic is anything you want to group: your bank, the gym, a specific app, invoices from a supplier... Sortix looks at the filename and, if needed, its content, searching for these keywords.",
        topic_name_label: "Topic name",
        topic_name_placeholder: "e.g. Bank, Gym, Netflix",
        topic_dest_label: "Destination folder",
        topic_dest_placeholder: "e.g. Documents/Bank",
        topic_keywords_label: "Keywords (comma-separated)",
        topic_keywords_placeholder: "e.g. bank, statement, iban",
        add_topic_btn: "Add topic",
        rules_hint: "Rules by extension are simpler and always override automatic classification: any file with that extension goes directly to the folder you specify.",
        rule_ext_label: "Extension",
        rule_ext_placeholder: "e.g. pdf",
        rule_dest_label: "Destination folder",
        rule_dest_placeholder: "e.g. Documents/Invoices",
        add_rule_btn: "Add rule",
        
        home: "Home",
        downloads: "Downloads",
        images: "Images",
        videos: "Videos",
        music: "Music",
        compressed: "Compressed",
        installers: "Installers",
        documents: "Documents",
        other: "Other",
        
        status_conn_error: "Could not connect to Sortix.",
        status_patrol_active: "Patrol active: watching Downloads.",
        status_patrol_inactive: "Patrol deactivated.",
        status_patrol_error: "Could not toggle Active Patrol.",
        status_organizing: "Organizing...",
        status_organized_done: "Done: {moved} file(s) organized.",
        status_organize_error: "Failed to organize downloads folder.",
        status_folder_error: "Could not open that folder.",
        
        topics_empty: "You don't have any topics yet. Add your first one below.",
        rules_empty: "You don't have any custom rules yet.",
        delete_topic_title: "Delete topic",
        delete_rule_title: "Delete rule",
        status_topic_saved: "Topic saved.",
        status_topic_save_error: "Could not save topic.",
        status_rule_saved: "Rule saved.",
        status_rule_save_error: "Could not save rule.",
        theme_title: "Toggle theme",
        
        welcome_message: "Welcome: define your first Topics (bank, gym, apps...) and that's it, Sortix takes care of the rest."
    }
};

let currentLang = localStorage.getItem("sortix_lang");
if (!currentLang) {
    const navLang = navigator.language || navigator.userLanguage;
    currentLang = navLang && navLang.startsWith("en") ? "en" : "es";
}

function t(key, defaultVal) {
    const translations = TRANSLATIONS[currentLang];
    if (translations && translations[key] !== undefined) {
        return translations[key];
    }
    return defaultVal !== undefined ? defaultVal : key;
}

function applyLanguage() {
    document.documentElement.lang = currentLang;
    
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        el.textContent = t(key);
    });

    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        const key = el.getAttribute("data-i18n-title");
        el.setAttribute("title", t(key));
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        el.setAttribute("placeholder", t(key));
    });

    const langSelect = document.getElementById("lang-select");
    if (langSelect) {
        langSelect.value = currentLang;
    }
}

// ---- tema claro/oscuro (rdsx style) ---------------------------------------
let currentTheme = localStorage.getItem("sortix_theme") || "dark";

function updateThemeButton() {
    const btn = document.getElementById("btn-theme");
    if (btn) {
        btn.innerHTML = svgIcon(currentTheme === "dark" ? "sun" : "moon");
    }
}

function toggleTheme() {
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    
    const switchTheme = () => {
        currentTheme = nextTheme;
        localStorage.setItem("sortix_theme", currentTheme);
        if (currentTheme === "light") {
            document.documentElement.classList.add("light");
        } else {
            document.documentElement.classList.remove("light");
        }
        updateThemeButton();
    };

    if (!document.startViewTransition) {
        switchTheme();
    } else {
        document.startViewTransition(switchTheme);
    }
}

const ICONS = {
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
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
    undo: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 6 6v1a4 4 0 0 1-4 4h-5"/>',
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

// Si Sortix esta configurado con SORTIX_TOKEN (p.ej. expuesto en la LAN),
// la API responde 401 hasta que el navegador presente el token. Se pide una
// vez y se guarda en localStorage.
function withToken(options) {
    const token = localStorage.getItem("sortix_token");
    if (!token) return options;
    return { ...(options || {}), headers: { ...((options || {}).headers || {}), "X-Sortix-Token": token } };
}

async function fetchJSON(url, options) {
    let res = await fetch(url, withToken(options));
    if (res.status === 401) {
        const token = prompt("Esta instancia de Sortix esta protegida.\nIntroduce el token de acceso (SORTIX_TOKEN):");
        if (token) {
            localStorage.setItem("sortix_token", token.trim());
            res = await fetch(url, withToken(options));
        }
    }
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
    homeItem.innerHTML = `${svgIcon("home")}<span>${t("home", "Inicio")}</span>`;
    homeItem.addEventListener("click", () => navigateTo(null));
    folderTreeEl.appendChild(homeItem);

    for (const item of tree) {
        const li = document.createElement("li");
        li.className = "tree-item" + (currentPath === item.path ? " active" : "");
        li.innerHTML = `${svgIcon(item.icon)}<span>${escapeHtml(t(item.key, item.label))}</span>`;
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
    if (match) return t(match.key, match.label);
    const segments = path.split("/");
    return segments[segments.length - 1];
}

function renderBreadcrumbs() {
    breadcrumbsEl.innerHTML = "";

    const homeCrumb = document.createElement("button");
    homeCrumb.className = "crumb";
    homeCrumb.innerHTML = `${svgIcon("home")}<span>${t("home", "Inicio")}</span>`;
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
        showStatus(t("status_folder_error"), true);
    }
}

function renderRootTiles() {
    for (const item of tree) {
        const tile = document.createElement("div");
        tile.className = "tile folder-tile";
        tile.innerHTML = `${svgIcon(item.icon, "tile-icon")}<span class="tile-name">${escapeHtml(t(item.key, item.label))}</span>`;
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
        showStatus(t("status_conn_error"), true);
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
        showStatus(data.active ? t("status_patrol_active") : t("status_patrol_inactive"));
    } catch (err) {
        patrolToggle.checked = !desired;
        showStatus(t("status_patrol_error"), true);
    }
});

organizeBtn.addEventListener("click", async () => {
    organizeBtn.disabled = true;
    showStatus(t("status_organizing"));
    try {
        const data = await fetchJSON("/api/organize-now", { method: "POST" });
        showStatus(t("status_organized_done").replace("{moved}", data.moved));
        await refreshStatus();
        await loadTree();
        if (currentPath !== null) await renderContent();
    } catch (err) {
        showStatus(t("status_organize_error"), true);
    } finally {
        organizeBtn.disabled = false;
    }
});

// ---- ajustes: temas --------------------------------------------------------

async function refreshTopics() {
    const topics = await fetchJSON("/api/topics");
    topicsListEl.innerHTML = "";
    if (topics.length === 0) {
        topicsListEl.innerHTML = `<li class="empty">${t("topics_empty")}</li>`;
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
        delBtn.title = t("delete_topic_title");
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
        showStatus(t("status_topic_saved"));
    } catch (err) {
        showStatus(err.message || t("status_topic_save_error"), true);
    }
});

// ---- ajustes: reglas por extension ------------------------------------------

async function refreshRules() {
    const rules = await fetchJSON("/api/rules");
    rulesListEl.innerHTML = "";
    if (rules.length === 0) {
        rulesListEl.innerHTML = `<li class="empty">${t("rules_empty")}</li>`;
    }
    for (const rule of rules) {
        const li = document.createElement("li");
        li.innerHTML = `<div class="settings-item-main"><strong>.${escapeHtml(rule.extension)}</strong> <span class="muted">&rarr; ${escapeHtml(rule.destination)}</span></div>`;
        const delBtn = document.createElement("button");
        delBtn.className = "icon-btn danger";
        delBtn.innerHTML = svgIcon("trash");
        delBtn.title = t("delete_rule_title");
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
        showStatus(t("status_rule_saved"));
    } catch (err) {
        showStatus(err.message || t("status_rule_save_error"), true);
    }
});

// ---- historial de movimientos + deshacer -----------------------------------

const historyListEl = document.getElementById("history-list");

function formatDate(sqlDate) {
    if (!sqlDate) return "";
    // SQLite guarda "YYYY-MM-DD HH:MM:SS" en UTC
    const date = new Date(sqlDate.replace(" ", "T") + "Z");
    if (Number.isNaN(date.getTime())) return sqlDate;
    return date.toLocaleString(undefined, { dateStyle: "short", timeStyle: "short" });
}

async function refreshHistory() {
    let moves;
    try {
        moves = await fetchJSON("/api/log?limit=50");
    } catch (err) {
        historyListEl.innerHTML = '<li class="empty">No se pudo cargar el historial.</li>';
        return;
    }
    historyListEl.innerHTML = "";
    if (moves.length === 0) {
        historyListEl.innerHTML = '<li class="empty">Sortix aun no ha movido ningun archivo.</li>';
        return;
    }
    for (const move of moves) {
        const li = document.createElement("li");
        if (move.undone_at) li.classList.add("undone");
        li.innerHTML = `<div class="settings-item-main">
            <strong>${escapeHtml(move.filename)}</strong>
            <span class="muted">${escapeHtml(move.category)} &rarr; ${escapeHtml(move.destination)}</span>
            <span class="keywords">${escapeHtml(formatDate(move.moved_at))}${move.undone_at ? " &middot; deshecho" : ""}</span>
        </div>`;
        if (!move.undone_at) {
            const undoBtn = document.createElement("button");
            undoBtn.className = "icon-btn";
            undoBtn.innerHTML = svgIcon("undo");
            undoBtn.title = "Deshacer: devolver el archivo a su carpeta de origen";
            undoBtn.addEventListener("click", async () => {
                undoBtn.disabled = true;
                try {
                    const result = await fetchJSON(`/api/log/${move.id}/undo`, { method: "POST" });
                    showStatus(`"${result.filename}" devuelto a su carpeta de origen.`);
                    await Promise.all([refreshHistory(), refreshStatus()]);
                    if (currentPath !== null) await renderContent();
                } catch (err) {
                    undoBtn.disabled = false;
                    showStatus(err.message || "No se pudo deshacer el movimiento.", true);
                }
            });
            li.appendChild(undoBtn);
        }
        historyListEl.appendChild(li);
    }
}

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
        if (tabBtn.dataset.tab === "history") refreshHistory();
    });
}

function openSettings(tab) {
    if (tab) {
        document.querySelector(`.tab-btn[data-tab="${tab}"]`)?.click();
    }
    settingsModal.showModal();
}

// ---- arranque ------------------------------------------------------------

const langSelect = document.getElementById("lang-select");
if (langSelect) {
    langSelect.addEventListener("change", async (e) => {
        currentLang = e.target.value;
        localStorage.setItem("sortix_lang", currentLang);
        applyLanguage();
        await Promise.all([refreshTopics(), refreshRules(), loadTree()]);
        renderBreadcrumbs();
        await renderContent();
    });
}

const themeBtn = document.getElementById("btn-theme");
if (themeBtn) {
    themeBtn.addEventListener("click", toggleTheme);
}

async function init() {
    applyLanguage();
    updateThemeButton();
    await Promise.all([refreshStatus(), loadTree(), refreshTopics(), refreshRules()]);
    renderBreadcrumbs();
    await renderContent();
    setInterval(refreshStatus, 5000);

    const onboarded = localStorage.getItem("sortix_onboarded");
    const topicsEmpty = topicsListEl.querySelector(".empty");
    const rulesEmpty = rulesListEl.querySelector(".empty");
    if (!onboarded && topicsEmpty && rulesEmpty) {
        openSettings("topics");
        showStatus(t("welcome_message"));
    }
    settingsModal.addEventListener("close", () => localStorage.setItem("sortix_onboarded", "1"));
}

init();
