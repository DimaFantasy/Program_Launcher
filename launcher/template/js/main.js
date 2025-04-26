// Главный файл, точка входа, инициализация

// Загрузка всех модулей приложения
document.addEventListener("DOMContentLoaded", function() {
    // Восстанавливаем сохраненный поисковый запрос, если он есть
    const savedSearchQuery = sessionStorage.getItem('lastSearchQuery');
    if (savedSearchQuery) {
        // Устанавливаем значение в поле поиска
        const searchInput = document.getElementById("searchInput");
        searchInput.value = savedSearchQuery;
        
        // Применяем фильтрацию с небольшой задержкой для полной загрузки DOM
        setTimeout(() => {
            filterPrograms();
            // Чистим сохраненный запрос, чтобы он не восстанавливался при обычной перезагрузке страницы
            sessionStorage.removeItem('lastSearchQuery');
        }, 300);
    }
    
    // Инициализация ScrollSpy
    const scrollSpy = new bootstrap.ScrollSpy(document.body, {
        target: "#category-nav"
    });
    
    // Обработчик для автоматического сохранения поискового запроса
    window.addEventListener("beforeunload", saveSearchBeforeUnload);
    
    // Создаем контейнер для toast-уведомлений
    createToastContainer();
    
    // Инициализация переключателя темы
    initThemeSwitcher();
    
    // Обработчик для чекбокса "Скрытые"
    const showHiddenCheck = document.getElementById("showHiddenCheck");
    if (showHiddenCheck) {
        // Проверяем, есть ли сохраненный статус в localStorage
        const showHidden = localStorage.getItem('showHidden') === 'true';
        if (showHidden) {
            showHiddenCheck.checked = true;
            document.body.classList.add('show-hidden');
        }
        
        // Обработчик изменения состояния чекбокса
        showHiddenCheck.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('show-hidden');
                localStorage.setItem('showHidden', 'true');
                console.log('Скрытые программы: включено');
            } else {
                document.body.classList.remove('show-hidden');
                localStorage.setItem('showHidden', 'false');
                console.log('Скрытые программы: выключено');
            }
        });
    }
    
    // Инициализируем отслеживание категорий после небольшой задержки
    setTimeout(enhancedCategoryNavigation, 500);
    
    // Обработчик для категорий в меню навигации
    document.querySelectorAll('#category-nav .nav-link').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.classList.add('hovered');
        });
        
        link.addEventListener('mouseleave', function() {
            this.classList.remove('hovered');
        });
        
        link.addEventListener('click', function(e) {
            // При клике на категорию обновляем состояние навигации
            setTimeout(enhancedCategoryNavigation, 300);
        });
    });
    
    // Обработчик для кнопок переименования категории
    document.querySelectorAll(".rename-category-btn").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            const categoryName = this.getAttribute("data-category");
            showRenameCategoryModal(categoryName);
        });
    });
    
    // Обработчик для кнопок удаления категории
    document.querySelectorAll(".delete-category-btn").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            event.stopPropagation();
            const categoryName = this.getAttribute("data-category");
            deleteCategory(categoryName);
        });
    });

    // Обработчик для кнопки очистки избранного
    document.querySelectorAll(".clear-favorites-btn").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            event.stopPropagation();
            clearAllFavorites();
        });
    });
    
    // Обработчик для кнопки перемещения избранного
    document.querySelectorAll(".move-favorites-btn").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            event.stopPropagation();
            showMoveFavoritesModal();
        });
    });
    
    // Обработчик для кнопки сохранения перемещенных избранных
    document.getElementById("saveMovedFavorites").addEventListener("click", function() {
        moveFavoritesToCategory();
    });
    
    // Обработчик для очистки лога при закрытии модального окна описания
    document.getElementById("descriptionModal").addEventListener("hidden.bs.modal", function (event) {
        // Удаляем контейнер с логом
        const logContainer = document.getElementById("aiDescriptionLog");
        if (logContainer) {
            logContainer.remove();
        }
    });
    
    // Обработчик для кнопки сохранения категории
    document.getElementById("saveCategory").addEventListener("click", function() {
        const path = document.getElementById("programPath").value;
        const currentCategory = document.getElementById("currentCategory").value;
        const select = document.getElementById("categorySelect");
        const newCategoryInput = document.getElementById("newCategoryInput").value.trim();
        const saveBtn = this;
        
        // Сохраняем текущий поисковый запрос
        const searchValue = document.getElementById("searchInput").value;
        
        // Определяем, какая категория выбрана
        let newCategory = newCategoryInput !== "" ? newCategoryInput : select.value;
        
        // Если категория не изменилась, то ничего не делаем
        if (newCategory === currentCategory) {
            bootstrap.Modal.getInstance(document.getElementById("categoryModal")).hide();
            return;
        }
        
        // Показываем индикатор загрузки
        const originalText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Сохранение...';
        saveBtn.disabled = true;
        
        console.log(`Отправка запроса на изменение категории для пути "${path}" с "${currentCategory}" на "${newCategory}"`);
        
        // Отправляем запрос на сервер
        fetch(`/change_category?path=${encodeURIComponent(path)}&category=${encodeURIComponent(newCategory)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(data => {
                console.log("Ответ сервера:", data);
                showToast("Категория изменена", data);
                
                // Сохраняем поисковый запрос в sessionStorage перед перезагрузкой
                if (searchValue) {
                    sessionStorage.setItem('lastSearchQuery', searchValue);
                }
                
                // Скрываем модальное окно
                bootstrap.Modal.getInstance(document.getElementById("categoryModal")).hide();
                // Перезагружаем страницу
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            })
            .catch(error => {
                console.error("Ошибка при изменении категории:", error);
                saveBtn.innerHTML = originalText;
                saveBtn.disabled = false;
                showToast("Ошибка", "Не удалось изменить категорию: " + error, "danger");
            });
    });
    
    // Обработчик для кнопки сохранения нового имени категории
    document.getElementById("saveRenamedCategory").addEventListener("click", function() {
        const originalCategory = document.getElementById("originalCategoryName").value;
        const newCategoryName = document.getElementById("newCategoryName").value.trim();
        
        if (!newCategoryName) {
            showToast("Ошибка", "Название категории не может быть пустым", "danger");
            return;
        }
        
        if (newCategoryName === originalCategory) {
            bootstrap.Modal.getInstance(document.getElementById("renameCategoryModal")).hide();
            return;
        }
        
        // Отправляем запрос на сервер для переименования категории
        fetch(`/rename_category?old_category=${encodeURIComponent(originalCategory)}&new_category=${encodeURIComponent(newCategoryName)}`)
            .then(response => response.text())
            .then(data => {
                console.log(data);
                showToast("Категория переименована", data);
                // Скрываем модальное окно
                bootstrap.Modal.getInstance(document.getElementById("renameCategoryModal")).hide();
                // Перезагружаем страницу
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            })
            .catch(error => {
                console.error("Error:", error);
                showToast("Ошибка", "Не удалось переименовать категорию: " + error, "danger");
            });
    });
    
    // Обработчик для кнопки сохранения описания
    document.getElementById("saveDescription").addEventListener("click", function() {
        const path = document.getElementById("programPathDescription").value;
        // Используем пустую строку, если описание пустое
        const newDescription = document.getElementById("descriptionInput").value || "";
        
        // Сохраняем текущий поисковый запрос
        const searchValue = document.getElementById("searchInput").value;
        
        console.log("Сохраняем новое описание для программы:", path);
        console.log("Длина описания:", newDescription.length);
        
        // Отправляем запрос на сервер
        fetch(`/change_description?path=${encodeURIComponent(path)}&description=${encodeURIComponent(newDescription)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(data => {
                console.log("Ответ сервера:", data);
                showToast("Описание изменено", data);
                
                // Сохраняем поисковый запрос в sessionStorage перед перезагрузкой
                if (searchValue) {
                    sessionStorage.setItem('lastSearchQuery', searchValue);
                }
                
                // Скрываем модальное окно
                bootstrap.Modal.getInstance(document.getElementById("descriptionModal")).hide();
                // Перезагружаем страницу
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            })
            .catch(error => {
                console.error("Error:", error);
                showToast("Ошибка", "Не удалось изменить описание: " + error, "danger");
            });
    });

    // Обработчик для кнопки получения автоматического описания в модальном окне
    document.getElementById("getAIDescriptionBtn").addEventListener("click", function() {
        const path = document.getElementById("programPathDescription").value;
        const descriptionInput = document.getElementById("descriptionInput");
        const spinner = document.getElementById("aiDescriptionSpinner");
        
        // Показываем индикатор загрузки
        spinner.style.display = "inline-block";
        this.disabled = true;
        
        console.log("Запрашиваем информацию о файле:", path);
        
        // Проверяем, не является ли путь уже закодированным
        let processedPath = path;
        try {
            // Если путь содержит %, вероятно, он уже закодирован
            if (path.includes('%')) {
                // Пытаемся декодировать и затем кодировать снова, чтобы избежать двойного кодирования
                processedPath = decodeURIComponent(path);
            }
        } catch (e) {
            console.warn("Ошибка декодирования пути:", e);
            // Если ошибка декодирования, используем путь как есть
        }
        
        // Корректно кодируем путь и логируем
        const encodedPath = encodeURIComponent(processedPath);
        console.log("Исходный путь:", path);
        console.log("Обработанный путь:", processedPath);
        console.log("Закодированный путь:", encodedPath);
        
        // Отправляем запрос на сервер для получения информации о файле
        fetch(`/get_file_info?path=${encodedPath}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Получен ответ:", data);
                
                if (data.success && data.file_info) {
                    // Получаем текущее описание
                    const currentDescription = descriptionInput.value.trim();
                    
                    // Добавляем информацию о файле к текущему описанию с переносом строки после заголовка
                    const newDescription = currentDescription + 
                        (currentDescription ? "\n\n" : "") + 
                        "Информация о файле:\n" + data.file_info;
                    
                    // Обновляем текст в поле описания
                    descriptionInput.value = newDescription;
                    
                    // Анимируем выделение, чтобы пользователь заметил изменение
                    descriptionInput.classList.add("border-success");
                    setTimeout(() => {
                        descriptionInput.classList.remove("border-success");
                    }, 1500);
                    
                    showToast("Успех", "Информация о файле успешно добавлена к описанию", "success");
                } else {
                    showToast("Предупреждение", data.error || "Не удалось получить информацию о файле", "warning");
                }
            })
            .catch(error => {
                console.error("Ошибка:", error);
                showToast("Ошибка", "Не удалось получить информацию о файле: " + error, "danger");
            })
            .finally(() => {
                // Скрываем индикатор загрузки и разблокируем кнопку
                spinner.style.display = "none";
                this.disabled = false;
            });
    });

    // Обработчик изменения цвета в палитре
    const colorPicker = document.getElementById('colorPicker');
    if (colorPicker) {
        colorPicker.addEventListener('input', updateColorPreview);
    }
    
    // Обработчик изменения чекбокса использования цвета по умолчанию
    const useDefaultColor = document.getElementById('useDefaultColor');
    if (useDefaultColor) {
        useDefaultColor.addEventListener('change', updateColorPreview);
    }
    
    // Обработчик для кнопки сохранения цвета
    const saveColorBtn = document.getElementById('saveColor');
    if (saveColorBtn) {
        saveColorBtn.addEventListener('click', saveHeaderColor);
    }
    
    // Добавляем обработчик клика для кнопки "Использовать цвет по умолчанию"
    const useDefaultColorBtn = document.getElementById('useDefaultColor');
    if (useDefaultColorBtn) {
        useDefaultColorBtn.addEventListener('click', function() {
            // Переключаем класс активности
            this.classList.toggle('active');
            // Обновляем предпросмотр
            updateColorPreview();
        });
    }
});

// Обработчик события прокрутки
window.addEventListener('scroll', function() {
    // Вызываем функцию обновления с небольшой задержкой для производительности
    clearTimeout(window.scrollEndTimer);
    window.scrollEndTimer = setTimeout(enhancedCategoryNavigation, 50);
});

// Обработчик для активации элемента в ScrollSpy
document.body.addEventListener('activate.bs.scrollspy', function(e) {
    // Запускаем улучшенное отслеживание навигации
    enhancedCategoryNavigation();
    
    // Получаем ID активного элемента
    const activeID = e.relatedTarget;
    console.log('Активирован раздел:', activeID);
});

// Добавляем обработчик события прокрутки для крупных категорий
let scrollTimer = null;
window.addEventListener('scroll', function() {
    // Используем debounce для оптимизации производительности
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(fixActiveCategoryOnScroll, 100);
});