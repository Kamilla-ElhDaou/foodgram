from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфигурация приложения 'api' для Django."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API'
