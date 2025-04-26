// Файл с утилитарными функциями (форматирование, проверки и т.п.)

// Функция для безопасного экранирования HTML
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
        '`': '&#096;'
    };
    return text.toString().replace(/[&<>"'`]/g, function(m) { return map[m]; });
}

// Функция для автоматического сохранения текста поиска перед перезагрузкой страницы
function saveSearchBeforeUnload() {
    const searchInput = document.getElementById("searchInput");
    if (searchInput && searchInput.value.trim()) {
        sessionStorage.setItem('lastSearchQuery', searchInput.value);
        console.log('Сохранен поисковый запрос перед перезагрузкой:', searchInput.value);
    }
}

// Утилитарная функция для безопасной обработки путей
function processPath(path) {
    try {
        // Если путь содержит %, вероятно, он уже закодирован
        if (path.includes('%')) {
            // Пытаемся декодировать, чтобы избежать двойного кодирования
            path = decodeURIComponent(path);
        }
    } catch (e) {
        console.warn("Ошибка декодирования пути:", e);
        // Если ошибка декодирования, используем путь как есть
    }
    
    return path;
}

// Утилитарная функция для подготовки кнопки к асинхронной операции
function prepareButton(btn, loadingText = null) {
    const originalHTML = btn.innerHTML;
    if (loadingText) {
        btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${loadingText}`;
    } else {
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    }
    btn.disabled = true;
    
    // Возвращаем функцию для восстановления кнопки
    return function restoreButton(delay = 0) {
        if (delay > 0) {
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            }, delay);
        } else {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        }
    };
}