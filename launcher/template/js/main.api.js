// Файл для работы с API (запросы к серверу)

// Утилитарная функция для отправки запросов и обработки ошибок
function sendRequest(url, onSuccess, onError, reloadPage = false, saveSearch = true) {
    // Сохраняем поисковый запрос, если требуется
    if (saveSearch) {
        const searchValue = document.getElementById("searchInput")?.value;
        if (searchValue) {
            sessionStorage.setItem('lastSearchQuery', searchValue);
        }
    }
    
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            if (onSuccess) {
                onSuccess(data);
            }
            
            // Перезагружаем страницу, если нужно
            if (reloadPage) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
            
            return data;
        })
        .catch(error => {
            console.error("Ошибка:", error);
            if (onError) {
                onError(error);
            }
            throw error;
        });
}

// Функция для фильтрации программ
function filterPrograms() {
    const searchValue = document.getElementById("searchInput").value.toLowerCase().trim();
    const cards = document.querySelectorAll(".program-card");
    const categoryContainers = document.querySelectorAll(".category-container");
    
    // Объект для отслеживания видимых программ по категориям
    let hasVisiblePrograms = {};
    
    // Добавляем отладочную информацию
    console.log("Поиск по тексту:", searchValue, "Длина:", searchValue.length);
    console.log("Доступные категории:", Array.from(categoryContainers).map(c => c.id));
    
    // Перебираем все карточки программ
    cards.forEach(card => {
        const name = card.getAttribute("data-name") || "";
        const category = card.getAttribute("data-category") || "";
        const description = card.getAttribute("data-description") || "";
        const isHidden = card.getAttribute("data-hidden") === "true";
        
        // Отладочная информация о программе
        console.log(`Программа: ${name}, Категория: ${category}, Скрыта: ${isHidden}`);
        
        // Если поиск пустой, показываем все карточки
        if (searchValue === "") {
            card.style.display = "";
            // Используем категорию программы для определения видимых категорий 
            if (category) {
                hasVisiblePrograms[category.toLowerCase()] = true;
            }
        } 
        // Иначе проверяем, содержит ли карточка поисковый текст
        else if (name.includes(searchValue) || category.includes(searchValue) || description.includes(searchValue)) {
            card.style.display = "";
            // Используем категорию программы для определения видимых категорий
            if (category) {
                hasVisiblePrograms[category.toLowerCase()] = true;
            }
        } else {
            card.style.display = "none";
        }
    });
    
    // Если поиск пустой, показываем все категории
    if (searchValue === "") {
        categoryContainers.forEach(container => {
            container.style.display = "";
        });
        console.log("Поиск пустой - показываем все категории");
        return;
    }
    
    // Перебираем все контейнеры категорий и показываем только те, в которых есть видимые программы
    categoryContainers.forEach(container => {
        const categoryId = container.id;
        // ID может быть с префиксом id_, поэтому берем только часть после последнего _
        const originalId = categoryId.toLowerCase();
        
        // Проверяем по оригинальному ID и атрибуту data-category-original
        const categoryOriginal = container.getAttribute("data-category-original");
        const categoryOriginalLower = categoryOriginal ? categoryOriginal.toLowerCase() : "";
        
        console.log(`Проверка видимости для категории '${categoryId}', оригинал: '${categoryOriginal}'`);
        console.log(`Наличие программ: ${hasVisiblePrograms[originalId] ? 'Да' : 'Нет'} или ${hasVisiblePrograms[categoryOriginalLower] ? 'Да' : 'Нет'}`);
        
        // Проверяем видимость по всем возможным вариантам ключа категории
        if (hasVisiblePrograms[originalId] || 
            (categoryOriginalLower && hasVisiblePrograms[categoryOriginalLower])) {
            container.style.display = "";
            console.log(`  Категория ${categoryId} видима`);
        } else {
            container.style.display = "none";
            console.log(`  Категория ${categoryId} скрыта`);
        }
    });
}