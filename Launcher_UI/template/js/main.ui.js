// Файл для управления интерфейсом (модалки, вкладки, выпадашки)

// Функция для показа toast-уведомлений
function showToast(title, message, type = "success") {
    const toastContainer = document.getElementById("toast-container") || createToastContainer();
    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");
    toast.setAttribute("aria-atomic", "true");
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong><br>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    toast.addEventListener("hidden.bs.toast", () => {
        toast.remove();
    });
}

// Функция для создания контейнера toast-уведомлений
function createToastContainer() {
    const container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container position-fixed bottom-0 end-0 p-3";
    container.style.zIndex = "1090";
    document.body.appendChild(container);
    return container;
}

// Функция для отображения модального окна изменения категории
function showCategoryModal(path, currentCategory, event) {
    console.log("Открываем модальное окно категорий для программы:", path);
    console.log("Текущая категория:", currentCategory);
    
    // Остановка всплытия события
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Декодируем путь перед сохранением (для случаев, когда путь уже закодирован)
    try {
        path = decodeURIComponent(path);
    } catch (e) {
        // Если декодирование не удалось, используем путь как есть
        console.warn("Ошибка декодирования пути:", e);
    }
    
    // Заполняем скрытые поля
    document.getElementById("programPath").value = path;
    document.getElementById("currentCategory").value = currentCategory;
    
    // Устанавливаем текущую категорию в выпадающем списке если она существует
    const select = document.getElementById("categorySelect");
    let categoryFound = false;
    
    for (let i = 0; i < select.options.length; i++) {
        if (select.options[i].value === currentCategory) {
            select.selectedIndex = i;
            categoryFound = true;
            break;
        }
    }
    
    // Если категория не найдена в списке, добавляем её
    if (!categoryFound && currentCategory) {
        const option = document.createElement("option");
        option.value = currentCategory;
        option.text = currentCategory;
        select.add(option);
        select.value = currentCategory;
    }
    
    // Очищаем поле для новой категории
    document.getElementById("newCategoryInput").value = "";
    
    // Показываем модальное окно
    try {
        const modalElement = document.getElementById("categoryModal");
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        console.log("Модальное окно категорий открыто успешно");
    } catch (error) {
        console.error("Ошибка при открытии модального окна:", error);
        alert("Не удалось открыть окно изменения категории. Попробуйте перезагрузить страницу.");
    }
}

// Функция для отображения модального окна описания
function showDescriptionModal(path, event) {
    console.log("Открываем модальное окно изменения описания для программы:", path);
    
    // Получаем кнопку, на которую нажали
    const btn = event.target.closest(".btn");
    
    // Получаем описание из атрибута data-description
    const description = btn.getAttribute("data-description");
    
    // Заполняем скрытые поля
    document.getElementById("programPathDescription").value = decodeURIComponent(path);
    
    // Устанавливаем текущее описание в поле редактирования
    document.getElementById("descriptionInput").value = description;
    
    // Сбрасываем состояние кнопки получения информации - всегда делаем её активной
    const getInfoButton = document.getElementById("getAIDescriptionBtn");
    getInfoButton.disabled = false;
    getInfoButton.innerHTML = '<i class="bi bi-info-circle"></i> Получить информацию из файла';
    
    // Скрываем спиннер, если он был активен
    document.getElementById("aiDescriptionSpinner").style.display = "none";
    
    // Удаляем все классы с подсветкой границы, если они остались
    document.getElementById("descriptionInput").classList.remove("border-success", "border-info");
    
    // Показываем модальное окно
    const modal = new bootstrap.Modal(document.getElementById("descriptionModal"));
    modal.show();
}

// Функция для отображения модального окна переименования категории
function showRenameCategoryModal(categoryName) {
    // Заполняем скрытое поле с оригинальным именем категории
    document.getElementById("originalCategoryName").value = categoryName;
    
    // Устанавливаем текущее название категории в поле ввода
    document.getElementById("newCategoryName").value = categoryName;
    
    // Показываем модальное окно
    const modal = new bootstrap.Modal(document.getElementById("renameCategoryModal"));
    modal.show();
}

// Функция для отображения модального окна перемещения избранных программ
function showMoveFavoritesModal() {
    // Очищаем поле ввода имени новой категории
    document.getElementById("moveFavoritesCategoryName").value = "";
    
    // Копируем все опции из основного списка категорий в список категорий для избранного
    const sourceSelect = document.getElementById("categorySelect");
    const targetSelect = document.getElementById("favoritesCategorySelect");
    
    // Очищаем целевой список перед копированием
    targetSelect.innerHTML = "";
    
    // Копируем опции из исходного селекта, кроме категории "Избранное"
    for (let i = 0; i < sourceSelect.options.length; i++) {
        const option = sourceSelect.options[i];
        if (option.value.toLowerCase() !== "избранное") {
            targetSelect.add(new Option(option.text, option.value));
        }
    }
    
    // Показываем модальное окно
    const modal = new bootstrap.Modal(document.getElementById("moveFavoritesModal"));
    modal.show();
}

// Функция для перемещения избранных программ в новую категорию
function moveFavoritesToCategory() {
    const favoritesCategorySelect = document.getElementById("favoritesCategorySelect");
    const newCategoryInputValue = document.getElementById("moveFavoritesCategoryName").value.trim();
    
    // Определяем, какая категория выбрана - приоритет у ввода новой категории
    let newCategory = newCategoryInputValue || favoritesCategorySelect.value;
    
    if (!newCategory) {
        showToast("Ошибка", "Необходимо выбрать существующую категорию или ввести новую", "danger");
        return;
    }
    
    // Показываем индикатор загрузки в виде Toast
    showToast("Информация", "Перемещение избранных программ...", "info");
    
    // Находим кнопку и показываем индикатор загрузки
    const saveBtn = document.getElementById("saveMovedFavorites");
    const originalBtnHTML = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Перемещаем...';

    // Отправляем GET-запрос на сервер
    fetch(`/move_favorites?category=${encodeURIComponent(newCategory)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            showToast("Успешно", data, "success");
            // Скрываем модальное окно
            bootstrap.Modal.getInstance(document.getElementById("moveFavoritesModal")).hide();
            // Перезагружаем страницу
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error("Ошибка при перемещении избранных программ:", error);
            showToast("Ошибка", "Не удалось переместить программы: " + error, "danger");
        })
        .finally(() => {
            saveBtn.innerHTML = originalBtnHTML;
            saveBtn.disabled = false;
        });
}

// Функция для удаления категории
function deleteCategory(categoryName) {
    // Проверяем, не избранное ли это
    if (categoryName.toLowerCase() === "избранное") {
        showToast("Ошибка", "Категория 'Избранное' не может быть удалена", "danger");
        return;
    }
    
    // Открываем модальное окно со списком программ для категории
    showProgramListModal(OPERATION_TYPES.REMOVE_CATEGORY, categoryName);
}

// Функция для очистки всех избранных элементов
function clearAllFavorites() {
    // Открываем модальное окно со списком избранных программ
    showProgramListModal(OPERATION_TYPES.REMOVE_FAVORITES);
}

// Функция для показа модального окна изменения цвета заголовка
function showColorModal(path, currentColor, event, type = 'program') {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Получаем модальное окно
    const colorModal = new bootstrap.Modal(document.getElementById('colorModal'));
    
    // Устанавливаем путь программы или имя категории
    document.getElementById('colorItemPath').value = path;
    
    // Устанавливаем тип объекта (программа или категория)
    document.getElementById('colorItemType').value = type;
    
    // Обновляем заголовок модального окна в зависимости от типа
    const modalTitle = document.getElementById('colorModalTitle');
    if (modalTitle) {
        modalTitle.textContent = type === 'category' 
            ? 'Изменение цвета категории' 
            : 'Изменение цвета заголовка программы';
    }
    
    // Устанавливаем начальный цвет в color picker
    if (currentColor && currentColor !== '#') {
        document.getElementById('colorPicker').value = currentColor;
    } else {
        // По умолчанию - синий цвет, если цвет не задан
        document.getElementById('colorPicker').value = '#4d90fe';
    }
    
    // Устанавливаем текущий цвет для предпросмотра
    updateColorPreview();
    
    // Показываем модальное окно
    colorModal.show();
}

// Функция для обновления предпросмотра цвета
function updateColorPreview() {
    const colorPreview = document.getElementById('colorPreview');
    const colorPicker = document.getElementById('colorPicker');

    // Используем выбранный цвет для предпросмотра
    colorPreview.style.backgroundColor = colorPicker.value;
    colorPreview.style.backgroundImage = 'none';

    // Автоматически выбираем цвет текста в зависимости от яркости фона
    const color = colorPicker.value.substring(1); // убираем #
    const r = parseInt(color.substring(0,2), 16); // получаем красный канал
    const g = parseInt(color.substring(2,4), 16); // получаем зеленый канал
    const b = parseInt(color.substring(4,6), 16); // получаем синий канал

    // Формула для вычисления яркости цвета
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;

    // Если яркость меньше 128, используем белый текст, иначе - черный
    colorPreview.style.color = brightness < 128 ? 'white' : 'black';
}

// Функция для установки предустановленного цвета
function setPresetColor(color) {
    document.getElementById('colorPicker').value = color;
    updateColorPreview();
}

// Функция для установки цвета по умолчанию
function setDefaultColor() {
    // Устанавливаем символ '#' в качестве значения цвета (маркер цвета по умолчанию)
    document.getElementById('colorPicker').value = '#';
    
    // Обновляем предпросмотр со стандартным цветом для визуализации
    const colorPreview = document.getElementById('colorPreview');
    if (colorPreview) {
        // Устанавливаем стандартный цвет заголовка для предпросмотра
        colorPreview.style.backgroundColor = '#f0f0f0';
        colorPreview.style.color = 'black'; // Черный текст на светлом фоне
        // Добавляем пометку, что это цвет по умолчанию
        colorPreview.setAttribute('data-default', 'true');
    }
    
    // Добавляем информационное сообщение о выборе цвета по умолчанию
    showToast("Информация", "Выбран цвет по умолчанию. Цвет будет адаптироваться к текущей теме оформления.", "info");
}

// Функция для сохранения выбранного цвета
function saveHeaderColor() {
    const itemPath = document.getElementById('colorItemPath').value;
    const itemType = document.getElementById('colorItemType').value;
    const colorPicker = document.getElementById('colorPicker');
    const colorPreview = document.getElementById('colorPreview');
    
    // Получаем выбранный цвет
    const headerColor = colorPicker.value;
    
    // Проверяем, является ли это цветом по умолчанию
    const isDefaultColor = headerColor === '#' || colorPreview.getAttribute('data-default') === 'true';
    
    // Показываем индикатор загрузки
    const messageText = itemType === 'category' ? 'Сохранение цвета категории...' : 'Сохранение цвета заголовка...';
    showToast("Информация", messageText, "info");
    
    // Создаем URL с правильными параметрами
    // Для цвета по умолчанию отправляем только символ '#'
    let url = `/change_header_color?path=${encodeURIComponent(itemPath)}&color=${isDefaultColor ? '%23' : encodeURIComponent(headerColor)}`;
    
    // Добавляем параметр типа
    url += `&type=${encodeURIComponent(itemType)}`;
    
    console.log("Отправка запроса на изменение цвета:", url);
    console.log("Цвет по умолчанию:", isDefaultColor ? "Да" : "Нет");
    
    // Отправляем запрос на сервер
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            const successMessage = itemType === 'category' ? 'Цвет категории сохранен' : 'Цвет заголовка сохранен';
            showToast("Успешно", isDefaultColor ? `${successMessage} (по умолчанию)` : successMessage, "success");
            
            // Скрываем модальное окно
            bootstrap.Modal.getInstance(document.getElementById('colorModal')).hide();
            
            // Перезагружаем страницу для применения изменений
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error("Ошибка при сохранении цвета:", error);
            showToast("Ошибка", "Не удалось сохранить цвет: " + error, "danger");
        });
}

// Функция для инициализации переключателя темы
function initThemeSwitcher() {
    const themeSwitcher = document.getElementById('themeSwitcher');
    
    // Проверяем, есть ли сохраненная тема в localStorage
    const savedTheme = localStorage.getItem('theme');
    
    // Если есть сохраненная темная тема или предпочтения системы - тёмные
    if (savedTheme === 'dark' || 
        (savedTheme === null && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        // Включаем темную тему
        document.body.classList.add('dark-theme');
        themeSwitcher.checked = true;
    }
    
    // Обработчик события переключения
    themeSwitcher.addEventListener('change', function() {
        if (this.checked) {
            // Включаем темную тему
            document.body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
            console.log('Переключение на темную тему');
        } else {
            // Включаем светлую тему
            document.body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
            console.log('Переключение на светлую тему');
        }
    });
}

// Функция для улучшенного отслеживания видимости активной категории при прокрутке
function enhancedCategoryNavigation() {
    // Находим все ссылки категорий в навигации
    const categoryLinks = document.querySelectorAll('#category-nav .nav-link');
    
    // Находим текущую активную ссылку
    const activeLink = document.querySelector('#category-nav .nav-link.active');
    
    if (!activeLink) return;
    
    // Получаем контейнер для навигации
    const navContainer = document.querySelector('.nav-scroll-container');
    
    // Находим или создаем индикатор категории 
    let categoryIndicator = document.querySelector('.category-indicator');
    if (!categoryIndicator) {
        categoryIndicator = document.createElement('div');
        categoryIndicator.className = 'category-indicator';
        document.body.appendChild(categoryIndicator);
    }

    // Получаем размеры и положение активной ссылки
    const activeLinkRect = activeLink.getBoundingClientRect();
    
    // Устанавливаем высоту и позицию индикатора
    categoryIndicator.style.height = `${activeLinkRect.height}px`;
    categoryIndicator.style.top = `${activeLinkRect.top}px`;
    
    // Добавляем эффект просмотра для активной категории
    categoryLinks.forEach(link => link.classList.remove('viewed'));
    activeLink.classList.add('viewed');
    
    // Определяем, нужно ли прокрутить контейнер с навигацией
    const containerRect = navContainer.getBoundingClientRect();
    const isActiveLinkFullyVisible = (
        activeLinkRect.top >= containerRect.top &&
        activeLinkRect.bottom <= containerRect.bottom
    );
    
    // Если активная ссылка не полностью видна, прокручиваем к ней
    if (!isActiveLinkFullyVisible) {
        const scrollPosition = activeLink.offsetTop - containerRect.height / 2 + activeLinkRect.height / 2;
        navContainer.scrollTo({
            top: scrollPosition,
            behavior: 'smooth'
        });
    }
}

// Функция для фиксации активной категории при прокрутке
function fixActiveCategoryOnScroll() {
    // Находим все контейнеры категорий
    const categoryContainers = document.querySelectorAll('.category-container');
    if (!categoryContainers.length) return;
    
    // Получаем текущую позицию прокрутки
    const scrollPosition = window.scrollY;
    
    // Находим верхнюю границу каждой категории и определяем, какая сейчас видна
    let activeCategory = null;
    let minDistance = Infinity;
    
    categoryContainers.forEach(container => {
        const rect = container.getBoundingClientRect();
        const topDistance = Math.abs(rect.top);
        
        // Если верхняя граница категории ближе всего к верху окна или уже немного прокручена вверх
        if (topDistance < minDistance && rect.top <= 100) {
            minDistance = topDistance;
            activeCategory = container.id;
        }
    });
    
    // Если нашли активную категорию, делаем соответствующий пункт меню активным
    if (activeCategory) {
        // Находим соответствующую ссылку в меню навигации
        const navLinks = document.querySelectorAll('#category-nav .nav-link');
        
        // Сначала убираем класс active у всех
        navLinks.forEach(link => link.classList.remove('active'));
        
        // Находим и активируем правильную ссылку
        const targetLink = document.querySelector(`#category-nav .nav-link[href="#${activeCategory}"]`);
        if (targetLink) {
            targetLink.classList.add('active');
            
            // Делаем активную ссылку видимой в контейнере с прокруткой
            const navContainer = document.querySelector('.nav-scroll-container');
            if (navContainer) {
                const linkTop = targetLink.offsetTop;
                const containerHeight = navContainer.clientHeight;
                const scrollTop = navContainer.scrollTop;
                
                // Если ссылка не видна в контейнере, прокручиваем к ней
                if (linkTop < scrollTop || linkTop > scrollTop + containerHeight) {
                    navContainer.scrollTo({
                        top: linkTop - containerHeight / 2,
                        behavior: 'smooth'
                    });
                }
            }
        }
    }
}