// Файл для обработки событий пользовательского интерфейса

// Функция для обработки запуска программы
function launchProgram(path, event) {
    const btn = event.target.closest(".btn");
    const restoreBtn = prepareButton(btn, "Запуск...");
    
    // Обрабатываем путь через общую функцию
    path = processPath(path);
    
    // Отправляем запрос
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса launch для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    sendRequest(
        `/launch?path=${encodedPath}`, 
        (data) => {
            showToast("Программа запущена", data);
            restoreBtn(1000);
        },
        (error) => {
            restoreBtn();
            showToast("Ошибка запуска", "Не удалось запустить программу: " + error, "danger");
        },
        false, // не перезагружать страницу
        false  // не сохранять поисковый запрос
    );
}

// Функция для открытия папки
function openFolder(path, event) {
    const btn = event.target.closest(".btn");
    const restoreBtn = prepareButton(btn);
    
    // Обрабатываем путь через общую функцию
    path = processPath(path);
    
    // Отправляем запрос
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса open_folder для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    sendRequest(
        `/open_folder?path=${encodedPath}`, 
        (data) => {
            showToast("Папка открыта", data);
            restoreBtn(1000);
        },
        (error) => {
            restoreBtn();
            showToast("Ошибка", "Не удалось открыть папку: " + error, "danger");
        },
        false, // не перезагружать страницу
        false  // не сохранять поисковый запрос
    );
}

// Функция для переключения избранного
function toggleFavorite(path, event) {
    const btn = event.currentTarget;  // Используем currentTarget вместо closest
    const restoreBtn = prepareButton(btn);
    
    // Обрабатываем путь через общую функцию
    path = processPath(path);
    
    // Отправляем запрос
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса toggle_favorite для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    sendRequest(
        `/toggle_favorite?path=${encodedPath}`, 
        (data) => {
            showToast("Статус избранного изменен", data);
            // Перезагрузить страницу после изменения статуса
            window.location.reload();
        },
        (error) => {
            restoreBtn();
            showToast("Ошибка", "Не удалось изменить статус избранного: " + error, "danger");
        },
        false // не перезагружать страницу - мы сами вызываем reload
    );
}

// Функция для удаления программы
function removeProgram(path, event) {
    if (!confirm("Вы уверены, что хотите удалить эту программу из списка?")) {
        return;
    }
    
    const btn = event.target.closest(".btn-remove");
    const restoreBtn = prepareButton(btn);
    
    // Обрабатываем путь через общую функцию
    path = processPath(path);
    
    // Отправляем запрос
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса remove_program для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    sendRequest(
        `/remove_program?path=${encodedPath}`, 
        (data) => {
            showToast("Программа удалена", data);
            // Перезагружаем страницу после удаления
            window.location.reload();
        },
        (error) => {
            restoreBtn();
            showToast("Ошибка", "Не удалось удалить программу: " + error, "danger");
        },
        false // не перезагружать страницу - мы сами вызываем reload
    );
}

// Функция для получения AI-описания
function getAIDescription(path, event) {
    const btn = event.target.closest(".btn");
    const restoreBtn = prepareButton(btn);
    
    // Получаем карточку программы, где находится кнопка
    const card = btn.closest('.program-card');
    const descTextElement = card.querySelector('.card-text');
    const descriptionText = descTextElement.childNodes[0]; // Текстовый узел с описанием
    
    // Показываем уведомление о начале процесса
    showToast("Запрос описания", "Получаем автоматическое описание программы...", "info");
    
    // Обрабатываем путь через общую функцию
    path = processPath(path);
    
    // Отправляем запрос
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
                
                // Перезагружаем страницу, чтобы обновление сохранилось
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showToast("Предупреждение", "Получено пустое описание или не удалось найти элемент для обновления", "warning");
            }
            
            // Восстанавливаем состояние кнопки
            restoreBtn();
        })
        .catch(error => {
            console.error("Ошибка:", error);
            restoreBtn();
            showToast("Ошибка", "Не удалось получить описание: " + error, "danger");
        });
}

// Функция для сканирования программ
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

// Функция для переключения скрытости программы
function toggleHidden(path, event) {
    const btn = event.currentTarget;
    const restoreBtn = prepareButton(btn);
    
    // Определяем, находится ли программа в избранном
    const card = btn.closest('.program-card');
    const isFavorite = card && card.getAttribute('data-category') && 
                      card.getAttribute('data-category').toLowerCase() === "избранное";
    
    console.log("Переключение статуса скрытия для программы:", path);
    console.log("Программа в избранном:", isFavorite ? "Да" : "Нет");
    
    // Обрабатываем путь через общую функцию
    path = processPath(path);
    
    // Отправляем запрос
    const encodedPath = encodeURIComponent(path);
    console.log("Отправка запроса toggle_hidden для пути:", path);
    console.log("Закодированный путь:", encodedPath);
    
    // Создаем URL с дополнительным параметром для избранного
    const url = `/toggle_hidden?path=${encodedPath}${isFavorite ? '&favorite=true' : ''}`;
    
    // Если программа в избранном, принудительно выполняем дополнительный запрос
    // для гарантированного сохранения статуса скрытия
    if (isFavorite) {
        // Сначала отправляем запрос на изменение статуса скрытия
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(data => {
                console.log("Первый ответ сервера:", data);
                
                // Делаем дополнительный запрос для гарантированного сохранения статуса
                return fetch(`/save_changes?force=true`);
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(data => {
                console.log("Результат принудительного сохранения:", data);
                showToast("Статус скрытия изменен", "Изменения сохранены принудительно для избранного");
                // Перезагрузить страницу после изменения статуса
                window.location.reload();
            })
            .catch(error => {
                restoreBtn();
                console.error("Ошибка:", error);
                showToast("Ошибка", "Не удалось изменить статус скрытия: " + error, "danger");
            });
    } else {
        // Для обычных программ используем стандартный подход
        sendRequest(
            url, 
            (data) => {
                showToast("Статус скрытия изменен", data);
                // Перезагрузить страницу после изменения статуса
                window.location.reload();
            },
            (error) => {
                restoreBtn();
                showToast("Ошибка", "Не удалось изменить статус скрытия: " + error, "danger");
            },
            false // не перезагружать страницу - мы сами вызываем reload
        );
    }
}

// Функция для закрытия приложения
function closeApplication() {
    // Показываем уведомление пользователю
    showToast("Завершение работы", "Приложение закрывается...", "info");
    
    // Делаем запрос на сервер для завершения работы
    fetch('/shutdown')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Сервер вернул ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            // Дополнительно закрываем вкладку браузера
            window.close();
            
            // Если окно не закрылось через window.close(), показываем сообщение
            setTimeout(() => {
                showToast("Информация", "Сервер остановлен. Можете закрыть это окно браузера.", "warning");
                // Меняем текст кнопки закрытия
                const closeBtn = document.getElementById("btnClose");
                if (closeBtn) {
                    closeBtn.innerHTML = '<i class="bi bi-check-circle"></i> Сервер остановлен';
                    closeBtn.disabled = true;
                    closeBtn.classList.remove("btn-danger");
                    closeBtn.classList.add("btn-secondary");
                }
            }, 2000);
        })
        .catch(error => {
            console.error("Ошибка при закрытии приложения:", error);
            showToast("Ошибка", "Не удалось закрыть приложение: " + error, "danger");
        });
}

// Функция для вызова модального окна изменения цвета категории
function showCategoryColorModal(categoryName, currentColor, event) {
    // Вызываем универсальную функцию showColorModal с типом 'category'
    showColorModal(categoryName, currentColor, event, 'category');
}

// Функция для обработки событий, связанных с выбором цвета
document.addEventListener('DOMContentLoaded', function() {
    // Обработчик изменения цвета в colorPicker
    const colorPicker = document.getElementById('colorPicker');
    if (colorPicker) {
        colorPicker.addEventListener('input', function() {
            // Обновляем предпросмотр при изменении цвета
            updateColorPreview();
        });
    }
    
    // Обработчик для кнопки сохранения цвета
    const saveColorBtn = document.getElementById('saveColor');
    if (saveColorBtn) {
        saveColorBtn.addEventListener('click', saveHeaderColor);
    }
});