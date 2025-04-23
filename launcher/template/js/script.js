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

function filterPrograms() {
    const searchValue = document.getElementById("searchInput").value.toLowerCase().trim();
    const cards = document.querySelectorAll(".program-card");
    const categoryContainers = document.querySelectorAll(".category-container");
    
    // Объект для отслеживания видимых программ по категориям
    let hasVisiblePrograms = {};
    
    // Добавляем отладочную информацию
    console.log("Поиск по тексту:", searchValue, "Длина:", searchValue.length);
    
    // Перебираем все карточки программ
    cards.forEach(card => {
        const name = card.getAttribute("data-name") || "";
        const category = card.getAttribute("data-category") || "";
        const description = card.getAttribute("data-description") || "";
        
        // Если поиск пустой, показываем все карточки
        if (searchValue === "") {
            card.style.display = "";
            // Извлекаем категорию из атрибута и добавляем в список видимых
            const cardCategory = card.getAttribute("data-category");
            if (cardCategory) {
                hasVisiblePrograms[cardCategory.toLowerCase()] = true;
            }
        } 
        // Иначе проверяем, содержит ли карточка поисковый текст
        else if (name.includes(searchValue) || category.includes(searchValue) || description.includes(searchValue)) {
            card.style.display = "";
            // Добавляем категорию в список видимых
            hasVisiblePrograms[category.toLowerCase()] = true;
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
        
        console.log(`Категория '${categoryId}', оригинал: '${categoryOriginal}'`);
        
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

function launchProgram(path, event) {
    const btn = event.target.closest(".btn");
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Запуск...';
    btn.disabled = true;
    
    // Проверяем, не является ли путь уже закодированным
    try {
        // Если путь содержит %, вероятно, он уже закодирован
        if (path.includes('%')) {
            // Пытаемся декодировать и затем кодировать снова, чтобы избежать двойного кодирования
            path = decodeURIComponent(path);
        }
    } catch (e) {
        console.warn("Ошибка декодирования пути:", e);
        // Если ошибка декодирования, используем путь как есть
    }
    
    // Корректно кодируем путь и логируем
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса launch для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    fetch("/launch?path=" + encodedPath)
        .then(response => response.text())
        .then(data => {
            console.log(data);
            showToast("Программа запущена", data);
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 1000);
        })
        .catch(error => {
            console.error("Error:", error);
            btn.innerHTML = originalText;
            btn.disabled = false;
            showToast("Ошибка запуска", "Не удалось запустить программу: " + error, "danger");
        });
}

function openFolder(path, event) {
    const btn = event.target.closest(".btn");
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    btn.disabled = true;
    
    // Проверяем, не является ли путь уже закодированным
    try {
        // Если путь содержит %, вероятно, он уже закодирован
        if (path.includes('%')) {
            // Пытаемся декодировать и затем кодировать снова, чтобы избежать двойного кодирования
            path = decodeURIComponent(path);
        }
    } catch (e) {
        console.warn("Ошибка декодирования пути:", e);
        // Если ошибка декодирования, используем путь как есть
    }
    
    // Корректно кодируем путь и логируем
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса open_folder для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    fetch("/open_folder?path=" + encodedPath)
        .then(response => response.text())
        .then(data => {
            console.log(data);
            showToast("Папка открыта", data);
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            }, 1000);
        })
        .catch(error => {
            console.error("Error:", error);
            btn.innerHTML = originalHTML;
            btn.disabled = false;
            showToast("Ошибка", "Не удалось открыть папку: " + error, "danger");
        });
}

function toggleFavorite(path, event) {
    const btn = event.currentTarget;  // Используем currentTarget вместо closest
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    btn.disabled = true;
    
    // Проверяем, не является ли путь уже закодированным
    try {
        // Если путь содержит %5C или %25, вероятно, он уже закодирован
        if (path.includes('%')) {
            // Пытаемся декодировать и затем кодировать снова, чтобы избежать двойного кодирования
            path = decodeURIComponent(path);
        }
    } catch (e) {
        console.warn("Ошибка декодирования пути:", e);
        // Если ошибка декодирования, используем путь как есть
    }
    
    // Сохраняем текущий поисковый запрос
    const searchValue = document.getElementById("searchInput").value;
    
    // Корректно кодируем путь и логируем
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса toggle_favorite для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    fetch("/toggle_favorite?path=" + encodedPath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            showToast("Статус избранного изменен", data);
            
            // Сохраняем поисковый запрос в sessionStorage перед перезагрузкой
            if (searchValue) {
                sessionStorage.setItem('lastSearchQuery', searchValue);
            }
            
            // Перезагрузить страницу после изменения статуса
            window.location.reload();
        })
        .catch(error => {
            console.error("Error:", error);
            btn.innerHTML = originalHTML;
            btn.disabled = false;
            showToast("Ошибка", "Не удалось изменить статус избранного: " + error, "danger");
        });
}

function removeProgram(path, event) {
    if (!confirm("Вы уверены, что хотите удалить эту программу из списка?")) {
        return;
    }
    const btn = event.target.closest(".btn-remove");
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    btn.disabled = true;
    
    // Проверяем, не является ли путь уже закодированным
    try {
        // Если путь содержит %, вероятно, он уже закодирован
        if (path.includes('%')) {
            // Пытаемся декодировать и затем кодировать снова, чтобы избежать двойного кодирования
            path = decodeURIComponent(path);
        }
    } catch (e) {
        console.warn("Ошибка декодирования пути:", e);
        // Если ошибка декодирования, используем путь как есть
    }
    
    // Сохраняем текущий поисковый запрос
    const searchValue = document.getElementById("searchInput").value;
    
    // Корректно кодируем путь и логируем
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса remove_program для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    fetch("/remove_program?path=" + encodedPath)
        .then(response => response.text())
        .then(data => {
            console.log(data);
            showToast("Программа удалена", data);
            // Сохраняем поисковый запрос в sessionStorage перед перезагрузкой
            if (searchValue) {
                sessionStorage.setItem('lastSearchQuery', searchValue);
            }
            // Перезагрузить страницу после удаления
            window.location.reload();
        })
        .catch(error => {
            console.error("Error:", error);
            btn.innerHTML = originalHTML;
            btn.disabled = false;
            showToast("Ошибка", "Не удалось удалить программу: " + error, "danger");
        });
}

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

function getAIDescription(path, event) {
    const btn = event.target.closest(".btn");
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    btn.disabled = true;
    
    // Получаем карточку программы, где находится кнопка
    const card = btn.closest('.program-card');
    const descTextElement = card.querySelector('.card-text');
    const descriptionText = descTextElement.childNodes[0]; // Текстовый узел с описанием
    
    // Сохраняем текущий поисковый запрос
    const searchValue = document.getElementById("searchInput").value;
    
    // Показываем уведомление о начале процесса
    showToast("Запрос описания", "Получаем автоматическое описание программы...", "info");
    
    // Проверяем, не является ли путь уже закодированным
    try {
        // Если путь содержит %, вероятно, он уже закодирован
        if (path.includes('%')) {
            // Пытаемся декодировать и затем кодировать снова, чтобы избежать двойного кодирования
            path = decodeURIComponent(path);
        }
    } catch (e) {
        console.warn("Ошибка декодирования пути:", e);
        // Если ошибка декодирования, используем путь как есть
    }
    
    // Корректно кодируем путь и логируем
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса get_ai_description для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    fetch("/get_ai_description?path=" + encodedPath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Получено описание:", data);
            
            // Обновляем текст описания прямо в карточке без перезагрузки страницы
            if (data && descriptionText) {
                // Обновляем видимый текст описания 
                descriptionText.textContent = data;
                
                // Обновляем атрибуты данных для поиска
                card.setAttribute('data-description', data.toLowerCase());
                
                showToast("Описание обновлено", "Получено новое описание для программы.", "success");
                
                // Сохраняем поисковый запрос в sessionStorage перед перезагрузкой
                if (searchValue) {
                    sessionStorage.setItem('lastSearchQuery', searchValue);
                }
                
                // Перезагружаем страницу, чтобы обновление сохранилось
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showToast("Предупреждение", "Получено пустое описание или не удалось найти элемент для обновления", "warning");
            }
            
            // Восстанавливаем состояние кнопки
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        })
        .catch(error => {
            console.error("Ошибка:", error);
            btn.innerHTML = originalHTML;
            btn.disabled = false;
            showToast("Ошибка", "Не удалось получить описание: " + error, "danger");
        });
}

function createToastContainer() {
    const container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container position-fixed bottom-0 end-0 p-3";
    container.style.zIndex = "1090";
    document.body.appendChild(container);
    return container;
}

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

function scanPrograms(event) {
    const btn = event.target.closest(".btn");
    const originalText = btn.innerHTML;
    btn.disabled = true;
    
    // Очищаем лог и сбрасываем счетчики
    document.getElementById("scanLog").innerHTML = "Начало сканирования...\n";
    document.getElementById("scanStatus").textContent = "Поиск программ...";
    document.getElementById("foundFilesCount").textContent = "Найдено файлов: 0";
    document.getElementById("scanProgressBar").style.width = "10%";
    document.getElementById("scanProgressBar").setAttribute("aria-valuenow", "10");
    
    // Делаем кнопки недоступными
    document.getElementById("finishScanningBtn").disabled = true;
    document.getElementById("closeScanningModal").disabled = true;
    
    // Открываем модальное окно сканирования
    const scanningModal = new bootstrap.Modal(document.getElementById("scanningModal"));
    scanningModal.show();
    
    // Переменные для отслеживания состояния сканирования
    let foundFiles = 0;
    let missingFiles = 0;
    let removedFiles = 0;
    let scanFinished = false;
    let scanningTimer = null;
    
    // Запускаем опрос сервера для получения текущего состояния сканирования
    scanningTimer = setInterval(updateScanProgress, 1000);
    
    // Обработчик для кнопки "Завершить"
    document.getElementById("finishScanningBtn").addEventListener("click", function() {
        // Применяем изменения (удаляем отсутствующие файлы)
        fetch("/apply_scan_changes")
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }
                return response.text();
            })
            .then(data => {
                console.log("Результат применения изменений:", data);
                showToast("Изменения применены", data);
                
                // Закрываем модальное окно и перезагружаем страницу
                scanningModal.hide();
                window.location.reload();
            })
            .catch(error => {
                console.error("Ошибка при применении изменений:", error);
                showToast("Ошибка", "Не удалось применить изменения: " + error, "danger");
                
                // Всё равно закрываем модальное окно и перезагружаем страницу
                scanningModal.hide();
                window.location.reload();
            });
    }, { once: true });
    
    // Обработчик для кнопки "Отмена"
    document.getElementById("cancelScanningBtn").addEventListener("click", function() {
        if (scanningTimer) {
            clearInterval(scanningTimer);
        }
        btn.innerHTML = originalText;
        btn.disabled = false;
    }, { once: true });
    
    // Функция для обновления хода сканирования
    function updateScanProgress() {
        fetch("/scan_status")
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Обновляем данные в модальном окне
                document.getElementById("scanStatus").textContent = data.status || "Сканирование...";
                
                // Обновляем лог сканирования
                if (data.log && data.log.length > 0) {
                    const logElement = document.getElementById("scanLog");
                    // Используем <br> вместо \n для корректного отображения переводов строк в HTML
                    const logLines = data.log.join("<br>");
                    logElement.innerHTML = logLines;
                    // Прокручиваем к последним сообщениям
                    logElement.scrollTop = logElement.scrollHeight;
                }
                
                // Обновляем индикатор прогресса
                let progress = data.progress || 0;
                document.getElementById("scanProgressBar").style.width = `${progress}%`;
                document.getElementById("scanProgressBar").setAttribute("aria-valuenow", progress);
                
                // Обновляем счетчик найденных файлов
                if (data.found_files !== undefined) {
                    foundFiles = data.found_files;
                    let counterText = `Найдено файлов: ${foundFiles}`;
                    
                    // Добавляем информацию о проверенных файлах
                    if (data.missing_files !== undefined && data.missing_files > 0) {
                        missingFiles = data.missing_files;
                        counterText += `, отсутствующих: ${missingFiles}`;
                    }
                    
                    // Добавляем информацию об удаленных файлах
                    if (data.removed_files !== undefined && data.removed_files > 0) {
                        removedFiles = data.removed_files;
                        counterText += `, удалено: ${removedFiles}`;
                    }
                    
                    document.getElementById("foundFilesCount").textContent = counterText;
                }
                
                // Проверяем, завершено ли сканирование
                if (data.finished) {
                    scanFinished = true;
                    clearInterval(scanningTimer);
                    
                    // Формируем текст завершения сканирования с учетом новых счетчиков
                    let finishText = `Сканирование завершено. Добавлено ${foundFiles} программ`;
                    if (missingFiles > 0) {
                        finishText += `, отсутствующих: ${missingFiles}`;
                    }
                    if (removedFiles > 0) {
                        finishText += `, удалено: ${removedFiles}`;
                    }
                    
                    // Обновляем UI для завершения сканирования
                    document.getElementById("scanStatus").textContent = finishText;
                    document.getElementById("scanProgressBar").style.width = "100%";
                    document.getElementById("scanProgressBar").setAttribute("aria-valuenow", "100");
                    document.getElementById("scanProgressBar").classList.remove("progress-bar-animated");
                    
                    // Активируем кнопки
                    document.getElementById("finishScanningBtn").disabled = false;
                    document.getElementById("closeScanningModal").disabled = false;
                    
                    // Восстанавливаем состояние кнопки сканирования
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    
                    // Показываем уведомление
                    let toastMessage = `Найдено ${foundFiles} новых программ`;
                    if (missingFiles > 0) {
                        toastMessage += `. Обнаружено ${missingFiles} отсутствующих файлов`;
                    }
                    if (removedFiles > 0) {
                        toastMessage += `, ${removedFiles} файлов будет удалено`;
                    }
                    
                    // Если есть обнаруженные проблемы, добавляем подсказку о сохранении
                    if (missingFiles > 0 || removedFiles > 0) {
                        toastMessage += ". Нажмите Сохранить, чтобы применить изменения";
                    }
                    
                    showToast("Сканирование завершено", toastMessage);
                }
            })
            .catch(error => {
                console.error("Ошибка при получении статуса сканирования:", error);
                
                // В случае ошибки останавливаем опрос
                clearInterval(scanningTimer);
                
                // Обновляем UI для завершения сканирования с ошибкой
                document.getElementById("scanStatus").textContent = "Ошибка при сканировании.";
                document.getElementById("scanProgressBar").classList.remove("progress-bar-animated");
                document.getElementById("scanProgressBar").classList.add("bg-danger");
                
                // Восстанавливаем состояние кнопки
                btn.innerHTML = originalText;
                btn.disabled = false;
                
                // Активируем кнопки
                document.getElementById("finishScanningBtn").disabled = false;
                document.getElementById("closeScanningModal").disabled = false;
                
                // Добавляем сообщение об ошибке в лог
                const logElement = document.getElementById("scanLog");
                logElement.innerHTML += `\n\nОшибка: ${error.message}`;
                logElement.scrollTop = logElement.scrollHeight;
                
                // Показываем уведомление об ошибке
                showToast("Ошибка сканирования", error.message, "danger");
            });
    }
    
    // Начинаем сканирование на сервере
    fetch("/start_scan")
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Сканирование запущено:", data);
            // Первое обновление статуса сканирования
            updateScanProgress();
        })
        .catch(error => {
            console.error("Ошибка при запуске сканирования:", error);
            
            // Останавливаем опрос
            clearInterval(scanningTimer);
            
            // Обновляем UI для отображения ошибки
            document.getElementById("scanStatus").textContent = "Ошибка при запуске сканирования.";
            document.getElementById("scanProgressBar").classList.remove("progress-bar-animated");
            document.getElementById("scanProgressBar").classList.add("bg-danger");
            
            // Восстанавливаем состояние кнопки
            btn.innerHTML = originalText;
            btn.disabled = false;
            
            // Активируем кнопки
            document.getElementById("finishScanningBtn").disabled = false;
            document.getElementById("closeScanningModal").disabled = false;
            
            // Добавляем сообщение об ошибке в лог
            const logElement = document.getElementById("scanLog");
            logElement.innerHTML += `\n\nОшибка при запуске сканирования: ${error.message}`;
            logElement.scrollTop = logElement.scrollHeight;
            
            // Показываем уведомление об ошибке
            showToast("Ошибка сканирования", error.message, "danger");
        });
}

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

// Функция для удаления категории
function deleteCategory(categoryName) {
    // Проверяем, не избранное ли это
    if (categoryName.toLowerCase() === "избранное") {
        showToast("Ошибка", "Категория 'Избранное' не может быть удалена", "danger");
        return;
    }
    
    if (!confirm(`Вы уверены, что хотите удалить категорию "${categoryName}" и все программы в ней?`)) {
        return;
    }
    
    console.log(`Отправка запроса на удаление категории: ${categoryName}`);
    
    // Показываем индикатор загрузки в виде Toast
    showToast("Информация", "Удаление категории...", "info");
    
    // Отправляем запрос на сервер
    fetch(`/remove_category?category=${encodeURIComponent(categoryName)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            showToast("Категория удалена", data);
            // Перезагружаем страницу
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error("Ошибка при удалении категории:", error);
            showToast("Ошибка", "Не удалось удалить категорию: " + error, "danger");
        });
}

// Функция для очистки всех избранных элементов
function clearAllFavorites() {
    if (!confirm("Вы уверены, что хотите удалить из списка все программы, находящиеся в избранном?")) {
        return;
    }
    
    console.log("Отправка запроса на удаление всех избранных программ");
    
    // Показываем индикатор загрузки в виде Toast
    showToast("Информация", "Удаление программ из избранного...", "info");
    
    // Отправляем запрос на сервер
    fetch('/clear_favorites')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            showToast("Программы удалены", data);
            // Перезагружаем страницу
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error("Ошибка при удалении программ:", error);
            showToast("Ошибка", "Не удалось удалить программы: " + error, "danger");
        });
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

// Добавляем обработчик события прокрутки для крупных категорий
let scrollTimer = null;
window.addEventListener('scroll', function() {
    // Используем debounce для оптимизации производительности
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(fixActiveCategoryOnScroll, 100);
});

// Обработчики событий DOM
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
    
    // Создаем контейнер для toast-уведомлений
    createToastContainer();
    
    // Инициализация переключателя темы
    initThemeSwitcher();
    
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

// Обработчик после загрузки DOM
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
    
    // Инициализируем ScrollSpy с улучшенными настройками
    const scrollSpy = new bootstrap.ScrollSpy(document.body, {
        target: '#category-nav',
        offset: 100,
        method: 'offset'
    });
    
    // Создаем контейнер для toast-уведомлений
    createToastContainer();
    
    // Инициализация переключателя темы
    initThemeSwitcher();
    
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
    
    // Инициализируем отслеживание категорий сразу после загрузки
    setTimeout(fixActiveCategoryOnScroll, 300);
    
    // Обработчик изменения активности в ScrollSpy
    document.body.addEventListener('activate.bs.scrollspy', function(e) {
        // При активации нового раздела через ScrollSpy
        const targetId = e.relatedTarget;
        console.log('ScrollSpy активировал:', targetId);
        
        // Проверяем через 200 мс, не исчезла ли активация для больших разделов
        setTimeout(() => {
            const activeLink = document.querySelector('#category-nav .nav-link.active');
            if (!activeLink) {
                // Если активная ссылка исчезла, восстанавливаем ее вручную
                fixActiveCategoryOnScroll();
            }
        }, 200);
    });
});