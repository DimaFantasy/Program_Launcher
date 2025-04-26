import webbrowser

def open_browser(port):
    """Открывает браузер с URL приложения"""
    try:
        webbrowser.open(f'http://localhost:{port}')
        return True
    except Exception as e:
        print(f"Не удалось открыть браузер: {str(e)}")
        print(f"Перейдите по адресу http://localhost:{port} вручную.")
        return False