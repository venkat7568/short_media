from django.apps import AppConfig


class DatingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dating"

    def ready(self):
        """Import signals when app is ready."""
        import dating.signals
