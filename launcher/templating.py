import os
import urllib.parse
from markupsafe import escape

class TemplateEngine:
    """Класс для работы с шаблонами HTML страниц"""
    
    def __init__(self, template_directory, default_icon='<i class="bi bi-app"></i>'):
        """
        Инициализация движка шаблонов
        
        :param template_directory: Директория с шаблонами
        :param default_icon: Иконка по умолчанию для программ и категорий
        """
        self.template_directory = template_directory
        self.default_icon = default_icon
    
    def make_id_safe(self, input_str):
        """
        Преобразует строку в безопасный ID для HTML
        
        :param input_str: Исходная строка
        :return: Безопасный ID
        """
        replacements = {
            ' ': '_', '/': '_', '\\': '_', '(': '', ')': '', '&': 'and',
            '.': '_', ',': '_', ':': '_', ';': '_', '!': '_', '?': '_',
            '"': '', "'": '', '+': 'plus', '-': '_', '=': 'eq'
        }
        result = input_str
        for old, new in replacements.items():
            result = result.replace(old, new)
            
        # Добавляем префикс 'id_' если строка начинается с цифры
        if result and result[0].isdigit():
            result = 'id_' + result
            
        return result
    
    def load_template(self, template_name):
        """
        Загружает шаблон из файла
        
        :param template_name: Имя файла шаблона
        :return: Содержимое шаблона
        """
        template_path = os.path.join(self.template_directory, "template", template_name)

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Ошибка при чтении шаблона {template_name}: {str(e)}")
            return ""
    
    def render_template(self, template_content, **kwargs):
        """
        Заменяет плейсхолдеры в шаблоне на значения
        
        :param template_content: Содержимое шаблона
        :param kwargs: Словарь с заменами
        :return: Обработанный шаблон
        """
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            template_content = template_content.replace(placeholder, str(value))
        return template_content
    
    def generate_main_page(self, app_name, programs, category_icons):
        """
        Генерирует HTML страницу на основе шаблонов
        
        :param app_name: Название приложения
        :param programs: Список программ
        :param category_icons: Словарь с иконками категорий
        :return: HTML-код главной страницы
        """
        try:
            # Загружаем шаблоны
            main_template = self.load_template('main.html')
            program_card_template = self.load_template('program_card.html')
            category_template = self.load_template('category.html')
            nav_item_template = self.load_template('nav_item.html')
            
            # Загружаем CSS и JavaScript из поддиректорий
            css_template = self.load_template('css/style.css')
            
            # Загрузка модульных JavaScript файлов в нужном порядке
            js_utils = self.load_template('js/main.utils.js')
            js_api = self.load_template('js/main.api.js')
            js_ui = self.load_template('js/main.ui.js')
            js_events = self.load_template('js/main.events.js')
            js_main = self.load_template('js/main.js')
            
            if not all([main_template, program_card_template, category_template, nav_item_template, css_template, 
                       js_utils, js_api, js_ui, js_events, js_main]):
                return "<h1>Ошибка: один или несколько шаблонов не найдены</h1>"
            
            # Заменяем название приложения
            main_template = main_template.replace('Programs-2k10 Launcher', app_name)
            
            # Встраиваем CSS в HTML
            css_style_tag = f'<style>\n{css_template}\n</style>'
            
            # Объединяем JavaScript модули в правильном порядке и встраиваем
            # Порядок важен: сначала утилиты, затем API, UI, события и наконец главный модуль
            combined_js = f"{js_utils}\n\n{js_api}\n\n{js_ui}\n\n{js_events}\n\n{js_main}"
            javascript_tag = f'<script>\n{combined_js}\n</script>'
            
            main_template = main_template.replace('<!-- CSS_PLACEHOLDER -->', css_style_tag)
            main_template = main_template.replace('<!-- JAVASCRIPT_PLACEHOLDER -->', javascript_tag)
            
            # Группируем программы по категориям
            grouped_programs = {}
            favorite_programs = []
            
            for program in sorted(programs, key=lambda x: (x.category, os.path.basename(x.path))):
                if program.is_favorite:
                    favorite_programs.append(program)
                
                if program.category not in grouped_programs:
                    grouped_programs[program.category] = []
                grouped_programs[program.category].append(program)
            
            # Генерируем меню навигации
            category_nav_items = []
            category_select_items=[]
            
            # Добавляем категорию "Избранное" если есть избранные программы
            if favorite_programs:
                favorites_nav = self.render_template(nav_item_template,
                    category_id="favorites",
                    category_icon='<i class="bi bi-star-fill text-warning"></i>',
                    category_name="Избранное",
                    badge_class="bg-warning text-dark",
                    count=str(len(favorite_programs))
                )
                category_nav_items.append(favorites_nav)
            
            # Добавляем остальные категории
            for category in sorted(grouped_programs.keys()):
                category_id = self.make_id_safe(category)
                nav_item = self.render_template(nav_item_template,
                    category_id=category_id,
                    category_icon=category_icons.get(category.lower(), self.default_icon),
                    category_name=escape(category),
                    badge_class="bg-secondary",
                    count=str(len(grouped_programs[category]))
                )
                category_nav_items.append(nav_item)
                category_select_items.append(f'<option value="{escape(category)}">{escape(category)}</option>')
            
            # Генерируем содержимое (карточки программ)
            content_categories = []
            
            # Добавляем раздел "Избранное"
            if favorite_programs:
                favorite_programs_html = []
                
                for program in favorite_programs:
                    program_name = os.path.splitext(os.path.basename(program.path))[0]
                    encoded_path = urllib.parse.quote(program.path)
                    
                    # Настройки для избранных программ
                    favorite_class = "active"
                    favorite_icon = "-fill"
                    favorite_title = "Удалить из избранного"
                    
                    # Настройки для скрытых программ
                    hide_class = "active" if program.is_hidden else ""
                    hide_icon = "-slash" if program.is_hidden else ""
                    hide_title = "Отобразить программу" if program.is_hidden else "Скрыть программу"
                    
                    # Настройки для индикации существования файла
                    file_exists = getattr(program, 'file_exists', True)  # По умолчанию True, если атрибут не существует
                    file_exists_class = "" if file_exists else "file-not-exists"
                    file_exists_indicator = "" if file_exists else '<span class="file-not-exists-indicator"><i class="bi bi-exclamation-triangle-fill"></i> Файл не существует</span>'
                    
                    # Формируем стиль заголовка карточки на основе заданного цвета
                    header_style = ""
                    header_color = getattr(program, 'header_color', '#')
                    if header_color and header_color != '#':
                        # Если цвет указан (не '#'), используем его
                        header_style = f"background-color: {header_color}; color: white;"
                    
                    program_card = self.render_template(program_card_template,
                        program_name_lower=program_name.lower(),
                        category_lower=program.category.lower(),
                        description_lower=program.description.lower(),
                        is_hidden=str(program.is_hidden).lower(),
                        favorite_class=favorite_class,
                        hide_class=hide_class,
                        encoded_path=encoded_path,
                        favorite_title=favorite_title,
                        hide_title=hide_title,
                        favorite_icon=favorite_icon,
                        hide_icon=hide_icon,
                        program_icon=self.default_icon,
                        program_name=escape(program_name),
                        description=escape(program.description),
                        description_attr=escape(program.description),
                        program_path=escape(program.path),
                        category_attr=escape(program.category),
                        file_exists_class=file_exists_class,
                        file_exists_indicator=file_exists_indicator,
                        header_style=header_style
                    )
                    favorite_programs_html.append(program_card)
                
                # Не добавляем кнопку переименования для избранного
                favorites_category = self.render_template(category_template,
                    category_id="favorites",
                    category_header_class="favorites-category",
                    category_icon='<i class="bi bi-star-fill"></i>',
                    category_name="Избранное",
                    category_id_original="Избранное",
                    rename_button="",  # Пустая строка вместо кнопки
                    delete_category_button=f'<button class="btn btn-sm btn-danger clear-favorites-btn" title="Удалить все программы из избранного в списке"><i class="bi bi-trash"></i></button>',
                    move_favorites_button=f'<button class="btn btn-sm btn-outline-light move-favorites-btn" title="Переместить все избранные программы в другую категорию"><i class="bi bi-folder-symlink"></i></button>'
                )
                favorites_category = favorites_category.replace("<!-- EXECUTABLE_PLACEHOLDER -->", "\n".join(favorite_programs_html))
                content_categories.append(favorites_category)
            
            # Добавляем остальные категории
            for category, programs in sorted(grouped_programs.items()):
                category_id = self.make_id_safe(category)
                programs_html = []
                
                for program in programs:
                    program_name = os.path.splitext(os.path.basename(program.path))[0]
                    encoded_path = urllib.parse.quote(program.path)
                    
                    # Настройки для избранного
                    favorite_class = 'active' if program.is_favorite else ''
                    favorite_icon = "-fill" if program.is_favorite else ""
                    favorite_title = "Удалить из избранного" if program.is_favorite else "Добавить в избранное"
                    
                    # Настройки для скрытых программ
                    hide_class = "active" if program.is_hidden else ""
                    hide_icon = "-slash" if program.is_hidden else ""
                    hide_title = "Отобразить программу" if program.is_hidden else "Скрыть программу"
                    
                    # Настройки для индикации существования файла
                    file_exists = getattr(program, 'file_exists', True)  # По умолчанию True, если атрибут не существует
                    file_exists_class = "" if file_exists else "file-not-exists"
                    file_exists_indicator = "" if file_exists else '<span class="file-not-exists-indicator"><i class="bi bi-exclamation-triangle-fill"></i> Файл не существует</span>'
                    
                    # Формируем стиль заголовка карточки на основе заданного цвета
                    header_style = ""
                    header_color = getattr(program, 'header_color', '#')
                    if header_color and header_color != '#':
                        # Если цвет указан (не '#'), используем его
                        header_style = f"background-color: {header_color}; color: white;"
                    
                    program_card = self.render_template(program_card_template,
                        program_name_lower=program_name.lower(),
                        category_lower=program.category.lower(),
                        description_lower=program.description.lower(),
                        is_hidden=str(program.is_hidden).lower(),
                        favorite_class=favorite_class,
                        hide_class=hide_class,
                        encoded_path=encoded_path,
                        favorite_title=favorite_title,
                        hide_title=hide_title,
                        favorite_icon=favorite_icon,
                        hide_icon=hide_icon,
                        program_icon=self.default_icon,
                        program_name=escape(program_name),
                        description=escape(program.description),
                        description_attr=escape(program.description),
                        program_path=escape(program.path),
                        category_attr=escape(category),
                        file_exists_class=file_exists_class,
                        file_exists_indicator=file_exists_indicator,
                        header_style=header_style
                    )
                    programs_html.append(program_card)
                
                # Формируем стиль заголовка категории
                category_header_style = ""
                category_color = ""
                
                # Проверяем, есть ли программы в этой категории с установленным цветом
                for program in programs:
                    header_color = getattr(program, 'header_color', '#')
                    if header_color and header_color != '#':
                        category_color = header_color
                        category_header_style = f"background-color: {header_color}; color: white;"
                        break
                
                # Добавляем кнопку переименования для обычных категорий
                rename_button = f'<button class="btn btn-sm btn-outline-light rename-category-btn" data-category="{escape(category)}" title="Переименовать категорию"><i class="bi bi-pencil"></i></button>'
                
                # Добавляем кнопку удаления категории, но не для категории "Избранное"
                delete_category_button = ""
                if category.lower() != "избранное":
                    delete_category_button = f'<button class="btn btn-sm btn-danger delete-category-btn" data-category="{escape(category)}" title="Удалить категорию из списка"><i class="bi bi-trash"></i></button>'
                
                category_html = self.render_template(category_template,
                    category_id=category_id,
                    category_header_class="",
                    category_header_style=category_header_style,
                    category_color=category_color,
                    category_icon=category_icons.get(category.lower(), self.default_icon),
                    category_name=escape(category),
                    category_id_original=escape(category),
                    delete_category_button=delete_category_button,
                    rename_button=rename_button,
                    move_favorites_button=""  # Пустая строка для обычных категорий
                )
                category_html = category_html.replace("<!-- EXECUTABLE_PLACEHOLDER -->", "\n".join(programs_html))
                content_categories.append(category_html)
            
            # Заменяем плейсхолдеры в основном шаблоне
            main_template = main_template.replace('<!-- CATEGORY_NAV_PLACEHOLDER -->', '\n'.join(category_nav_items))
            main_template = main_template.replace('<!-- CONTENT_PLACEHOLDER -->', '\n'.join(content_categories))
            main_template = main_template.replace('<!-- CATEGORY_SELECT_PLACEHOLDER -->', '\n'.join(category_select_items))
            
            return main_template
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"<h1>Ошибка при генерации страницы</h1><p>{str(e)}</p>"