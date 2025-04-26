// Функции для работы с универсальным модальным окном программ

// Глобальные переменные для хранения данных о программах
let allPrograms = [];
let filteredPrograms = [];

// Функция для открытия модального окна со списком программ
function showProgramListModal(operationType, target = null) {
    console.log("Открываем модальное окно списка программ:", operationType, target);
    
    // Устанавливаем тип операции и цель
    document.getElementById("listOperationType").value = operationType;
    if (target) {
        document.getElementById("listOperationTarget").value = target;
    } else {
        document.getElementById("listOperationTarget").value = "";
    }
    
    // Очищаем поиск и сбрасываем выбор всех программ
    document.getElementById("programListSearchInput").value = "";
    
    // Устанавливаем состояние чекбокса "Выбрать все" в зависимости от типа операции
    // Для удаления категории отмечаем все по умолчанию
    if (operationType === OPERATION_TYPES.REMOVE_CATEGORY) {
        document.getElementById("selectAllPrograms").checked = true;
    } else {
        document.getElementById("selectAllPrograms").checked = false;
    }
    
    // Настраиваем заголовок и информационное сообщение в зависимости от типа операции
    setupModalAppearance(operationType, target);
    
    // Загружаем список программ
    loadProgramList(operationType, target);
    
    // Показываем модальное окно
    const modal = new bootstrap.Modal(document.getElementById("programListModal"));
    modal.show();
}

// Функция для настройки внешнего вида модального окна в зависимости от типа операции
function setupModalAppearance(operationType, target) {
    const modalTitle = document.getElementById("programListModalLabel");
    const modalInfo = document.getElementById("programListModalInfo");
    const confirmButton = document.getElementById("confirmProgramListAction");
    
    // Настраиваем заголовок, информационное сообщение и кнопку подтверждения
    switch(operationType) {
        case OPERATION_TYPES.REMOVE_PROGRAM:
            modalTitle.textContent = "Удаление программы";
            modalInfo.textContent = "Выберите программы, которые нужно удалить из списка";
            confirmButton.textContent = "Удалить выбранные";
            confirmButton.classList.remove("btn-warning", "btn-success");
            confirmButton.classList.add("btn-danger");
            break;
            
        case OPERATION_TYPES.REMOVE_CATEGORY:
            modalTitle.textContent = "Удаление категории";
            modalInfo.textContent = `Программы из категории "${target}" будут удалены из списка`;
            confirmButton.textContent = "Удалить все";
            confirmButton.classList.remove("btn-danger", "btn-success");
            confirmButton.classList.add("btn-warning");
            break;
            
        case OPERATION_TYPES.REMOVE_FAVORITES:
            modalTitle.textContent = "Удаление из избранного";
            modalInfo.textContent = "Выберите программы, которые нужно удалить из избранного";
            confirmButton.textContent = "Удалить из избранного";
            confirmButton.classList.remove("btn-danger", "btn-warning");
            confirmButton.classList.add("btn-success");
            break;
            
        default:
            modalTitle.textContent = "Список программ";
            modalInfo.textContent = "Выберите программы из списка";
            confirmButton.textContent = "Подтвердить";
            confirmButton.classList.remove("btn-warning", "btn-success");
            confirmButton.classList.add("btn-danger");
    }
}

// Функция для загрузки списка программ в зависимости от типа операции
function loadProgramList(operationType, target) {
    console.log("Загружаем список программ:", operationType, target);
    
    // Очищаем текущий список
    const programListContainer = document.getElementById("programListContainer");
    programListContainer.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';
    
    // Формируем URL в зависимости от типа операции
    let url = '/api/programs';
    
    if (operationType === OPERATION_TYPES.REMOVE_CATEGORY && target) {
        url += `?category=${encodeURIComponent(target)}`;
    } else if (operationType === OPERATION_TYPES.REMOVE_FAVORITES) {
        url += '?favorites=true';
    }
    
    // Получаем список программ с сервера
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Сохраняем полученные данные
            allPrograms = data.programs || [];
            
            // Если это режим удаления программы и указан путь к программе,
            // то фильтруем список, чтобы включить только указанную программу
            if (operationType === OPERATION_TYPES.REMOVE_PROGRAM && target) {
                console.log("Фильтрация программ для удаления конкретной программы:", target);
                
                // Нормализуем путь для сравнения (заменяем обратные слеши на прямые и т.д.)
                let normalizedTarget = target.replace(/\\/g, '/');
                console.log("Нормализованный целевой путь:", normalizedTarget);
                
                // Выводим список всех доступных путей в консоль для диагностики
                console.log("Все доступные пути в списке:", allPrograms.map(p => p.path));
                
                // Фильтруем программы
                allPrograms = allPrograms.filter(program => {
                    // Нормализуем путь программы для сравнения
                    let normalizedPath = program.path.replace(/\\/g, '/');
                    
                    // Логируем для диагностики
                    console.log(`Сравниваем: "${normalizedPath}" с "${normalizedTarget}"`);
                    
                    // Попробуем несколько вариантов совпадения
                    // 1. Точное совпадение (case-insensitive)
                    const exactMatch = normalizedPath.toLowerCase() === normalizedTarget.toLowerCase();
                    
                    // 2. Совпадение по имени файла и родительской папке (для случаев с относительными путями)
                    const pathParts1 = normalizedPath.toLowerCase().split('/');
                    const pathParts2 = normalizedTarget.toLowerCase().split('/');
                    const fileNameMatch = pathParts1[pathParts1.length - 1] === pathParts2[pathParts2.length - 1];
                    
                    // 3. Проверяем, заканчивается ли один путь другим
                    const isSubstring = normalizedPath.toLowerCase().endsWith(normalizedTarget.toLowerCase()) || 
                                        normalizedTarget.toLowerCase().endsWith(normalizedPath.toLowerCase());
                    
                    // Используем комбинацию проверок
                    const isMatch = exactMatch || (fileNameMatch && isSubstring);
                    
                    if (isMatch) {
                        console.log("Найдено совпадение для программы:", program.path);
                    }
                    
                    return isMatch;
                });
                
                console.log(`Отфильтровано программ для пути ${target}: ${allPrograms.length}`);
                
                // Если после фильтрации список пуст, но путь указан,
                // добавляем сообщение об ошибке и логируем проблему
                if (allPrograms.length === 0) {
                    console.error("Не найдена программа с путем:", target);
                    console.error("Все доступные пути:", data.programs.map(p => p.path));
                    
                    // Более детальная информация о проблеме
                    programListContainer.innerHTML = `
                        <div class="alert alert-warning m-3">
                            <h5>Программа не найдена в списке</h5>
                            <p>Не удалось найти программу с путем: <code>${escapeHtml(target)}</code></p>
                            <p>Возможные причины:</p>
                            <ul>
                                <li>Программа была удалена из списка ранее</li>
                                <li>Различия в формате пути (абсолютный vs относительный)</li>
                                <li>Проблемы с кодировкой символов в пути</li>
                            </ul>
                            <p>Попробуйте обновить страницу и повторить операцию.</p>
                        </div>
                    `;
                    return;
                }
            }
            
            filteredPrograms = [...allPrograms];
            renderProgramList();
        })
        .catch(error => {
            console.error("Ошибка при загрузке списка программ:", error);
            programListContainer.innerHTML = `<div class="alert alert-danger m-3">Ошибка при загрузке списка программ: ${error.message}</div>`;
        });
}

// Функция для рендеринга списка программ
function renderProgramList() {
    const programListContainer = document.getElementById("programListContainer");
    programListContainer.innerHTML = '';
    
    if (filteredPrograms.length === 0) {
        programListContainer.innerHTML = '<div class="text-center p-3">Нет программ для отображения</div>';
        return;
    }
    
    // Получаем текущий тип операции для определения автоматического выбора программ
    const operationType = document.getElementById("listOperationType").value;
    const shouldSelectAll = operationType === OPERATION_TYPES.REMOVE_CATEGORY;
    
    // Создаем элементы списка для каждой программы
    filteredPrograms.forEach(program => {
        const programItem = document.createElement('div');
        programItem.className = 'list-group-item list-group-item-action d-flex align-items-center';
        
        // Создаем чекбокс
        const checkbox = document.createElement('div');
        checkbox.className = 'form-check me-3';
        checkbox.innerHTML = `<input class="form-check-input program-checkbox" type="checkbox" value="${escapeHtml(program.path)}" id="program_${escapeHtml(program.id)}" ${shouldSelectAll ? 'checked' : ''}>`;
        
        // Создаем информацию о программе
        const programInfo = document.createElement('div');
        programInfo.className = 'ms-2 me-auto';
        
        const nameElement = document.createElement('div');
        nameElement.className = 'fw-bold';
        nameElement.textContent = program.name || 'Без имени';
        
        const pathElement = document.createElement('div');
        pathElement.className = 'small text-muted';
        pathElement.textContent = program.path;
        
        const categoryElement = document.createElement('div');
        categoryElement.className = 'small';
        categoryElement.innerHTML = `Категория: <span class="badge bg-secondary">${escapeHtml(program.category)}</span>`;
        
        // Собираем элементы вместе
        programInfo.appendChild(nameElement);
        programInfo.appendChild(pathElement);
        programInfo.appendChild(categoryElement);
        
        // Если программа в избранном, добавляем соответствующий значок
        if (program.is_favorite) {
            const favoriteIcon = document.createElement('span');
            favoriteIcon.className = 'ms-2 text-warning';
            favoriteIcon.innerHTML = '<i class="bi bi-star-fill"></i>';
            programInfo.appendChild(favoriteIcon);
        }
        
        programItem.appendChild(checkbox);
        programItem.appendChild(programInfo);
        
        // Добавляем обработчик клика на элемент списка (для выбора чекбокса)
        programItem.addEventListener('click', function(event) {
            if (!event.target.classList.contains('form-check-input')) {
                const checkbox = this.querySelector('.form-check-input');
                checkbox.checked = !checkbox.checked;
            }
        });
        
        programListContainer.appendChild(programItem);
    });
}

// Функция для фильтрации списка программ
function filterProgramList(searchText) {
    if (!searchText || searchText.trim() === '') {
        filteredPrograms = [...allPrograms];
    } else {
        searchText = searchText.toLowerCase().trim();
        filteredPrograms = allPrograms.filter(program => {
            return (program.name && program.name.toLowerCase().includes(searchText)) ||
                   (program.path && program.path.toLowerCase().includes(searchText)) ||
                   (program.category && program.category.toLowerCase().includes(searchText));
        });
    }
    renderProgramList();
}

// Функция для выбора/отмены выбора всех программ
function toggleSelectAllPrograms(checked) {
    const checkboxes = document.querySelectorAll('.program-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = checked;
    });
}

// Функция для получения списка выбранных программ
function getSelectedPrograms() {
    const checkboxes = document.querySelectorAll('.program-checkbox:checked');
    return Array.from(checkboxes).map(checkbox => checkbox.value);
}

// Функция для выполнения действия с выбранными программами
function processProgramListAction() {
    const operationType = document.getElementById("listOperationType").value;
    const operationTarget = document.getElementById("listOperationTarget").value;
    const selectedPrograms = getSelectedPrograms();
    
    if (selectedPrograms.length === 0 && operationType !== OPERATION_TYPES.REMOVE_CATEGORY) {
        showToast("Внимание", "Не выбрано ни одной программы", "warning");
        return;
    }
    
    console.log("Выполняем действие:", operationType, "для программ:", selectedPrograms);
    
    // Показываем индикатор загрузки
    const confirmButton = document.getElementById("confirmProgramListAction");
    const originalBtnHTML = confirmButton.innerHTML;
    confirmButton.disabled = true;
    confirmButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Обработка...';
    
    // Формируем URL и параметры запроса в зависимости от типа операции
    let url, successMessage;
    
    switch(operationType) {
        case OPERATION_TYPES.REMOVE_PROGRAM:
            url = '/remove_programs';
            successMessage = "Программы успешно удалены";
            break;
            
        case OPERATION_TYPES.REMOVE_CATEGORY:
            url = `/remove_category?category=${encodeURIComponent(operationTarget)}`;
            successMessage = `Категория "${operationTarget}" успешно удалена`;
            break;
            
        case OPERATION_TYPES.REMOVE_FAVORITES:
            url = '/remove_from_favorites';
            successMessage = "Программы удалены из избранного";
            break;
            
        default:
            showToast("Ошибка", "Неизвестный тип операции", "danger");
            confirmButton.disabled = false;
            confirmButton.innerHTML = originalBtnHTML;
            return;
    }
    
    // Подготавливаем данные для отправки
    const requestData = {
        paths: selectedPrograms
    };
    
    // Отправляем запрос
    const fetchOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    };
    
    // Для операций, которые не требуют тела запроса, используем метод GET
    if (operationType === OPERATION_TYPES.REMOVE_CATEGORY) {
        delete fetchOptions.headers;
        delete fetchOptions.body;
        fetchOptions.method = 'GET';
    }
    
    fetch(url, fetchOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Ответ сервера:", data);
            showToast("Успешно", successMessage, "success");
            
            // Закрываем модальное окно
            bootstrap.Modal.getInstance(document.getElementById("programListModal")).hide();
            
            // Перезагружаем страницу
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error("Ошибка при выполнении операции:", error);
            showToast("Ошибка", `Не удалось выполнить операцию: ${error.message}`, "danger");
            confirmButton.disabled = false;
            confirmButton.innerHTML = originalBtnHTML;
        });
}

// Инициализация обработчиков событий
document.addEventListener('DOMContentLoaded', function() {
    // Обработчик для кнопки поиска
    const searchInput = document.getElementById('programListSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterProgramList(this.value);
        });
    }
    
    // Обработчик для кнопки очистки поиска
    const searchClearBtn = document.getElementById('programListSearchClear');
    if (searchClearBtn) {
        searchClearBtn.addEventListener('click', function() {
            searchInput.value = '';
            filterProgramList('');
        });
    }
    
    // Обработчик для чекбокса "Выбрать все"
    const selectAllCheckbox = document.getElementById('selectAllPrograms');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            toggleSelectAllPrograms(this.checked);
        });
    }
    
    // Обработчик для кнопки подтверждения действия
    const confirmButton = document.getElementById('confirmProgramListAction');
    if (confirmButton) {
        confirmButton.addEventListener('click', processProgramListAction);
    }
});

// Функции для открытия модального окна в разных режимах
function showRemoveProgramModal() {
    showProgramListModal(OPERATION_TYPES.REMOVE_PROGRAM);
}

function showRemoveCategoryModal(categoryName) {
    showProgramListModal(OPERATION_TYPES.REMOVE_CATEGORY, categoryName);
}

function showRemoveFavoritesModal() {
    showProgramListModal(OPERATION_TYPES.REMOVE_FAVORITES);
}