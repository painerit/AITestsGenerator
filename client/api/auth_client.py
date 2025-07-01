import requests
from config import Config

class AuthClient:
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.AUTH_API_URL

    def login(self, username, password):
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password}
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                server_error = error_data.get("error", "В ответе отсутствует сообщение об ошибке")
            except ValueError:
                server_error = response.text.strip() or "Ошибка в не-JSON формате"
            
            if response.status_code == 401:
                raise AuthError(f"Неверные учетные данные: {server_error}") from e
            elif response.status_code == 403:
                raise AuthError(f"Доступ запрещен: {server_error}") from e
            elif 400 <= response.status_code < 500:
                raise AuthError(f"Ошибка клиента ({response.status_code}): {server_error}") from e
            else:
                raise AuthError(f"Ошибка сервера ({response.status_code}): {server_error}") from e
        
        except requests.exceptions.ConnectionError:
            raise AuthError("Проблемы с сетью: Не удалось подключиться к серверу")
        
        except requests.exceptions.Timeout:
            raise AuthError("Таймаут соединения: Сервер не отвечает")
        
        except requests.exceptions.RequestException as e:
            raise AuthError(f"Ошибка запроса: {str(e)}") from e
        
        except ValueError as e:
            raise AuthError(f"Неверный формат JSON в ответе: {str(e)}") from e

    def register(self, username, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json={"username": username, "email": email, "password": password}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = response.json().get("error", "Registration failed")
            raise AuthError(f"{error_msg}: {str(e)}")

class AuthError(Exception):
    pass