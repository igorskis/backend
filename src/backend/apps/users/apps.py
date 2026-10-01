from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'backend.apps.users'

    def ready(self):
        import backend.apps.users.models
