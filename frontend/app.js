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
        tab_general: "General",
        general_hint: "Ajustes globales del sistema para gestionar archivos duplicados e integraciones.",
        duplicate_action_label: "Acción al encontrar archivos idénticos en destino",
        dup_opt_suffix: "Añadir sufijo numérico, ej. archivo (1).pdf",
        dup_opt_skip: "Omitir movimiento (dejar en Descargas)",
        dup_opt_delete_source: "Eliminar archivo original (ya guardado)",
        save_settings_btn: "Guardar ajustes",
        topic_rename_label: "Patrón de renombrado (opcional)",
        topic_rename_placeholder: "ej. {YYYY}-{MM} - {OriginalName}.{ext}",
        rule_rename_label: "Patrón de renombrado (opcional)",
        rule_rename_placeholder: "ej. {Category}/{OriginalName}.{ext}",
        rule_conditions_label: "Condiciones de activación (opcional)",
        btn_add_condition: "+ Añadir condición",
        cond_field_name: "Nombre de archivo",
        cond_field_stem: "Nombre (sin extensión)",
        cond_field_ext: "Extensión",
        cond_field_size: "Tamaño (KB)",
        cond_field_content: "Contenido de texto",
        cond_op_contains: "Contiene",
        cond_op_not_contains: "No contiene",
        cond_op_equals: "Es igual a",
        cond_op_starts_with: "Empieza con",
        cond_op_ends_with: "Termina con",
        cond_op_gt: "Mayor que",
        cond_op_lt: "Menor que",
        cond_value_placeholder: "Valor",
        status_settings_saved: "Ajustes del sistema guardados.",
        status_settings_save_error: "No se pudo guardar la configuración.",
        
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
        
        welcome_message: "Bienvenido: define tus primeros Temas (banco, gimnasio, apps...) y listo, Sortix se encarga solo a partir de ahora.",
        
        tab_history: "Historial",
        history_hint: "Últimos movimientos de Sortix. Si un archivo acabó donde no debía, pulsa «Deshacer» y volverá a su carpeta de origen.",
        history_empty: "Sortix aún no ha movido ningún archivo.",
        history_load_error: "No se pudo cargar el historial.",
        undo_title: "Deshacer: devolver el archivo a su carpeta de origen",
        status_undone_done: '"{filename}" devuelto a su carpeta de origen.',
        status_undo_error: "No se pudo deshacer el movimiento.",
        history_undone_label: "deshecho",
        
        tab_duplicates: "Deduplicar",
        duplicates_hint: "Escanea y elimina archivos duplicados para liberar espacio.",
        scan_duplicates_btn: "Buscar duplicados",
        auto_select_btn: "Seleccionar todos menos uno",
        clean_selected_btn: "Limpiar seleccionados",
        scanning_message: "Buscando archivos duplicados...",
        duplicates_empty: "No se han encontrado archivos duplicados.",
        status_cleaning_done: "Limpieza completada: se eliminaron {count} archivo(s).",
        status_cleaning_error: "No se pudieron eliminar algunos archivos.",
        status_scanning_error: "No se pudieron buscar archivos duplicados."
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
        tab_general: "General",
        general_hint: "Global system settings to manage duplicate files and integrations.",
        duplicate_action_label: "Action when identical files exist in destination",
        dup_opt_suffix: "Add numeric suffix, e.g. file (1).pdf",
        dup_opt_skip: "Skip movement (keep in Downloads)",
        dup_opt_delete_source: "Delete original file (already saved)",
        save_settings_btn: "Save settings",
        topic_rename_label: "Rename pattern (optional)",
        topic_rename_placeholder: "e.g. {YYYY}-{MM} - {OriginalName}.{ext}",
        rule_rename_label: "Rename pattern (optional)",
        rule_rename_placeholder: "e.g. {Category}/{OriginalName}.{ext}",
        rule_conditions_label: "Activation conditions (optional)",
        btn_add_condition: "+ Add condition",
        cond_field_name: "File name",
        cond_field_stem: "File name (no ext)",
        cond_field_ext: "Extension",
        cond_field_size: "Size (KB)",
        cond_field_content: "Text content",
        cond_op_contains: "Contains",
        cond_op_not_contains: "Does not contain",
        cond_op_equals: "Equals",
        cond_op_starts_with: "Starts with",
        cond_op_ends_with: "Ends with",
        cond_op_gt: "Greater than",
        cond_op_lt: "Less than",
        cond_value_placeholder: "Value",
        status_settings_saved: "System settings saved.",
        status_settings_save_error: "Could not save configuration.",
        
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
        
        welcome_message: "Welcome: define your first Topics (bank, gym, apps...) and that's it, Sortix takes care of the rest.",
        
        tab_history: "History",
        history_hint: "Recent Sortix movements. If a file ended up in the wrong place, click 'Undo' to return it to its source folder.",
        history_empty: "Sortix has not moved any files yet.",
        history_load_error: "Could not load history.",
        undo_title: "Undo: return the file to its source folder",
        status_undone_done: '"{filename}" returned to its source folder.',
        status_undo_error: "Could not undo the movement.",
        history_undone_label: "undone",
        
        tab_duplicates: "Deduplicate",
        duplicates_hint: "Scan and delete duplicate files to free up space.",
        scan_duplicates_btn: "Scan for duplicates",
        auto_select_btn: "Auto-select all but one",
        clean_selected_btn: "Clean Selected",
        scanning_message: "Scanning for duplicate files...",
        duplicates_empty: "No duplicate files found.",
        status_cleaning_done: "Cleaning completed: {count} file(s) deleted.",
        status_cleaning_error: "Could not delete some files.",
        status_scanning_error: "Could not scan for duplicate files."
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
    const rename_pattern = document.getElementById("topic-rename-pattern").value.trim();
    if (!name || !destination || !keywords) return;
    try {
        await fetchJSON("/api/topics", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, destination, keywords, rename_pattern }),
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

const conditionsContainer = document.getElementById("rule-conditions-container");
const btnAddCondition = document.getElementById("btn-add-condition");

function createConditionRow(data = {}) {
    const row = document.createElement("div");
    row.className = "condition-row";
    row.style.display = "flex";
    row.style.gap = "6px";
    row.style.marginBottom = "6px";
    row.style.width = "100%";
    row.style.alignItems = "center";

    row.innerHTML = `
        <select class="cond-field lang-select" style="flex: 1.2; min-width: 80px; padding: 6px; background-color: var(--bg-input); border: 1px solid var(--border-input); color: var(--color-input-text); border-radius: 6px; font-size: 0.85rem;">
            <option value="name">${t("cond_field_name")}</option>
            <option value="stem">${t("cond_field_stem")}</option>
            <option value="extension">${t("cond_field_ext")}</option>
            <option value="size_kb">${t("cond_field_size")}</option>
            <option value="content">${t("cond_field_content")}</option>
        </select>
        <select class="cond-operator lang-select" style="flex: 1; min-width: 80px; padding: 6px; background-color: var(--bg-input); border: 1px solid var(--border-input); color: var(--color-input-text); border-radius: 6px; font-size: 0.85rem;">
            <option value="contains">${t("cond_op_contains")}</option>
            <option value="not_contains">${t("cond_op_not_contains")}</option>
            <option value="equals">${t("cond_op_equals")}</option>
            <option value="starts_with">${t("cond_op_starts_with")}</option>
            <option value="ends_with">${t("cond_op_ends_with")}</option>
            <option value="gt">${t("cond_op_gt")}</option>
            <option value="lt">${t("cond_op_lt")}</option>
        </select>
        <input type="text" class="cond-value" placeholder="${t("cond_value_placeholder")}" style="flex: 2; min-width: 100px; padding: 6px; background-color: var(--bg-input); border: 1px solid var(--border-input); color: var(--color-input-text); border-radius: 6px; font-size: 0.85rem;">
        <button type="button" class="btn-remove-cond icon-btn danger" style="padding: 6px 10px; font-size: 0.95rem; border-radius: 6px; cursor: pointer; border: 1px solid var(--border-input); background: var(--bg-item-hover); color: var(--color-danger);">&times;</button>
    `;

    const fieldSel = row.querySelector(".cond-field");
    const opSel = row.querySelector(".cond-operator");
    const valInput = row.querySelector(".cond-value");
    const removeBtn = row.querySelector(".btn-remove-cond");

    if (data.field) fieldSel.value = data.field;
    if (data.operator) opSel.value = data.operator;
    if (data.value !== undefined) valInput.value = data.value;

    removeBtn.addEventListener("click", () => {
        row.remove();
    });

    conditionsContainer.appendChild(row);
}

if (btnAddCondition) {
    btnAddCondition.addEventListener("click", () => {
        createConditionRow();
    });
}

async function refreshRules() {
    const rules = await fetchJSON("/api/rules");
    rulesListEl.innerHTML = "";
    if (rules.length === 0) {
        rulesListEl.innerHTML = `<li class="empty">${t("rules_empty")}</li>`;
    }
    for (const rule of rules) {
        const li = document.createElement("li");
        
        let details = [];
        if (rule.rename_pattern) {
            details.push(`Renombrar: <code>${escapeHtml(rule.rename_pattern)}</code>`);
        }
        if (rule.conditions) {
            try {
                const conds = JSON.parse(rule.conditions);
                if (conds && conds.length > 0) {
                    const condStrs = conds.map(c => {
                        const fieldName = t(`cond_field_${c.field}`) || c.field;
                        const opName = t(`cond_op_${c.operator}`) || c.operator;
                        return `${fieldName} ${opName.toLowerCase()} "${escapeHtml(c.value)}"`;
                    });
                    details.push(`Condiciones: ${condStrs.join(" AND ")}`);
                }
            } catch(e) {}
        }
        
        const detailsStr = details.length > 0 
            ? `<div class="rule-details" style="font-size: 0.75rem; margin-top: 4px; color: var(--color-text-muted);">${details.join(" | ")}</div>`
            : "";
            
        li.innerHTML = `
            <div class="settings-item-main" style="display: flex; flex-direction: column;">
                <div><strong>.${escapeHtml(rule.extension)}</strong> <span class="muted">&rarr; ${escapeHtml(rule.destination)}</span></div>
                ${detailsStr}
            </div>
        `;

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
    const rename_pattern = document.getElementById("rule-rename-pattern").value.trim();
    
    // Compilar condiciones visuales
    const condRows = conditionsContainer.querySelectorAll(".condition-row");
    const conditions = [];
    for (const row of condRows) {
        const field = row.querySelector(".cond-field").value;
        const operator = row.querySelector(".cond-operator").value;
        const value = row.querySelector(".cond-value").value.trim();
        if (field && operator && value) {
            conditions.push({ field, operator, value });
        }
    }

    if (!extension || !destination) return;

    try {
        await fetchJSON("/api/rules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                extension,
                destination,
                rename_pattern,
                conditions: conditions.length > 0 ? conditions : null
            }),
        });
        ruleForm.reset();
        conditionsContainer.innerHTML = "";
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
        historyListEl.innerHTML = `<li class="empty">${t("history_load_error")}</li>`;
        return;
    }
    historyListEl.innerHTML = "";
    if (moves.length === 0) {
        historyListEl.innerHTML = `<li class="empty">${t("history_empty")}</li>`;
        return;
    }
    for (const move of moves) {
        const li = document.createElement("li");
        if (move.undone_at) li.classList.add("undone");
        const undoneText = move.undone_at ? ` &middot; ${t("history_undone_label")}` : "";
        li.innerHTML = `<div class="settings-item-main">
            <strong>${escapeHtml(move.filename)}</strong>
            <span class="muted">${escapeHtml(move.category)} &rarr; ${escapeHtml(move.destination)}</span>
            <span class="keywords">${escapeHtml(formatDate(move.moved_at))}${undoneText}</span>
        </div>`;
        if (!move.undone_at) {
            const undoBtn = document.createElement("button");
            undoBtn.className = "icon-btn";
            undoBtn.innerHTML = svgIcon("undo");
            undoBtn.title = t("undo_title");
            undoBtn.addEventListener("click", async () => {
                undoBtn.disabled = true;
                try {
                    const result = await fetchJSON(`/api/log/${move.id}/undo`, { method: "POST" });
                    showStatus(t("status_undone_done").replace("{filename}", result.filename));
                    await Promise.all([refreshHistory(), refreshStatus()]);
                    if (currentPath !== null) await renderContent();
                } catch (err) {
                    undoBtn.disabled = false;
                    showStatus(err.message || t("status_undo_error"), true);
                }
            });
            li.appendChild(undoBtn);
        }
        historyListEl.appendChild(li);
    }
}

// ---- ajustes generales (duplicados) -------------------------------------------

const generalSettingsForm = document.getElementById("general-settings-form");
const duplicateActionSelect = document.getElementById("duplicate-action-select");

async function refreshGeneralSettings() {
    try {
        const settings = await fetchJSON("/api/settings");
        duplicateActionSelect.value = settings.duplicate_action || "suffix";
    } catch (err) {
        console.error("Error loading general settings:", err);
    }
}

if (generalSettingsForm) {
    generalSettingsForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const duplicate_action = duplicateActionSelect.value;
        try {
            await fetchJSON("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ duplicate_action })
            });
            showStatus(t("status_settings_saved"));
        } catch (err) {
            showStatus(err.message || t("status_settings_save_error"), true);
        }
    });
}

// ---- deduplicación (buscar y limpiar duplicados) ----------------------------

let duplicateGroups = [];

async function scanDuplicates() {
    const spinner = document.getElementById("duplicates-loading");
    const container = document.getElementById("duplicates-container");
    const listEl = document.getElementById("duplicates-list");
    const emptyMsg = document.getElementById("duplicates-empty-msg");
    const btnAutoSelect = document.getElementById("btn-auto-select-duplicates");
    const btnClean = document.getElementById("btn-clean-duplicates");

    if (!spinner || !container || !listEl || !emptyMsg) return;

    spinner.style.display = "block";
    listEl.style.display = "none";
    emptyMsg.style.display = "none";
    if (btnAutoSelect) btnAutoSelect.disabled = true;
    if (btnClean) btnClean.disabled = true;

    try {
        duplicateGroups = await fetchJSON("/api/duplicates");
        listEl.innerHTML = "";

        if (duplicateGroups.length === 0) {
            emptyMsg.style.display = "block";
        } else {
            duplicateGroups.forEach((groupObj, groupIdx) => {
                let files = [];
                let sizeBytes = 0;
                if (groupObj && Array.isArray(groupObj)) {
                    files = groupObj;
                    sizeBytes = files[0]?.size || 0;
                } else if (groupObj && groupObj.files && Array.isArray(groupObj.files)) {
                    files = groupObj.files;
                    sizeBytes = groupObj.size_bytes || files[0]?.size || 0;
                }

                if (files.length === 0) return;

                const groupDiv = document.createElement("div");
                groupDiv.className = "duplicates-group";

                const header = document.createElement("div");
                header.className = "duplicates-group-header";
                
                const groupSizeStr = formatSize(sizeBytes);
                const groupTitle = currentLang === "es" 
                    ? `Grupo ${groupIdx + 1} (${groupSizeStr} cada uno)` 
                    : `Group ${groupIdx + 1} (${groupSizeStr} each)`;
                
                header.innerHTML = `<strong>${groupTitle}</strong>`;
                groupDiv.appendChild(header);

                const itemsList = document.createElement("div");
                itemsList.className = "duplicates-group-list";

                files.forEach((file) => {
                    const item = document.createElement("div");
                    item.className = "duplicates-item";

                    const cb = document.createElement("input");
                    cb.type = "checkbox";
                    cb.className = "duplicates-item-checkbox";
                    cb.dataset.path = file.path;
                    cb.addEventListener("change", updateCleanButtonState);

                    const details = document.createElement("div");
                    details.className = "duplicates-item-details";
                    
                    let formattedTime = file.mtime;
                    if (formattedTime) {
                        try {
                            const date = new Date(formattedTime);
                            formattedTime = date.toLocaleString(undefined, { dateStyle: "short", timeStyle: "short" });
                        } catch (e) {}
                    }

                    details.innerHTML = `
                        <span class="duplicates-item-name">${escapeHtml(file.name)}</span>
                        <span class="duplicates-item-path">${escapeHtml(file.path)}</span>
                        <span class="duplicates-item-meta">${formatSize(sizeBytes)} &middot; ${escapeHtml(formattedTime)}</span>
                    `;

                    item.appendChild(cb);
                    item.appendChild(details);
                    itemsList.appendChild(item);
                });

                groupDiv.appendChild(itemsList);
                listEl.appendChild(groupDiv);
            });
            listEl.style.display = "flex";
            if (btnAutoSelect) btnAutoSelect.disabled = false;
        }
    } catch (err) {
        showStatus(t("status_scanning_error"), true);
        emptyMsg.textContent = t("status_scanning_error");
        emptyMsg.style.display = "block";
    } finally {
        spinner.style.display = "none";
    }
}

function updateCleanButtonState() {
    const btnClean = document.getElementById("btn-clean-duplicates");
    if (!btnClean) return;
    const checkedBoxes = document.querySelectorAll(".duplicates-item-checkbox:checked");
    btnClean.disabled = checkedBoxes.length === 0;
}

function autoSelectDuplicates() {
    const groups = document.querySelectorAll(".duplicates-group");
    groups.forEach((group) => {
        const checkboxes = group.querySelectorAll(".duplicates-item-checkbox");
        checkboxes.forEach((cb, idx) => {
            cb.checked = idx > 0;
        });
    });
    updateCleanButtonState();
}

async function cleanSelectedDuplicates() {
    const btnClean = document.getElementById("btn-clean-duplicates");
    const checkedBoxes = document.querySelectorAll(".duplicates-item-checkbox:checked");
    if (checkedBoxes.length === 0) return;

    const filesToDelete = Array.from(checkedBoxes).map(cb => cb.dataset.path);
    
    if (btnClean) btnClean.disabled = true;
    showStatus(currentLang === "es" ? "Eliminando duplicados..." : "Deleting duplicates...");

    try {
        const res = await fetchJSON("/api/duplicates/clean", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ files: filesToDelete }),
        });
        
        const count = res.deleted !== undefined ? res.deleted : (res.cleaned !== undefined ? res.cleaned : filesToDelete.length);
        showStatus(t("status_cleaning_done").replace("{count}", count));
        await scanDuplicates();
    } catch (err) {
        showStatus(t("status_cleaning_error"), true);
        if (btnClean) btnClean.disabled = false;
    }
}

// ---- modal de ajustes --------------------------------------------------------

document.getElementById("btn-settings").innerHTML = svgIcon("settings");
document.getElementById("btn-close-settings").innerHTML = svgIcon("close");

document.getElementById("btn-settings").addEventListener("click", () => openSettings());
document.getElementById("btn-close-settings").addEventListener("click", () => settingsModal.close());

const btnScan = document.getElementById("btn-scan-duplicates");
if (btnScan) btnScan.addEventListener("click", scanDuplicates);

const btnAutoSelect = document.getElementById("btn-auto-select-duplicates");
if (btnAutoSelect) btnAutoSelect.addEventListener("click", autoSelectDuplicates);

const btnClean = document.getElementById("btn-clean-duplicates");
if (btnClean) btnClean.addEventListener("click", cleanSelectedDuplicates);

for (const tabBtn of document.querySelectorAll(".tab-btn")) {
    tabBtn.addEventListener("click", () => {
        for (const b of document.querySelectorAll(".tab-btn")) b.classList.remove("active");
        for (const p of document.querySelectorAll(".tab-panel")) p.hidden = true;
        tabBtn.classList.add("active");
        document.getElementById(`tab-${tabBtn.dataset.tab}`).hidden = false;
        if (tabBtn.dataset.tab === "history") refreshHistory();
        if (tabBtn.dataset.tab === "general") refreshGeneralSettings();
        if (tabBtn.dataset.tab === "duplicates") scanDuplicates();
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
    await Promise.all([refreshStatus(), loadTree(), refreshTopics(), refreshRules(), refreshGeneralSettings()]);
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
