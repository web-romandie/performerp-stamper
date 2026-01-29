from config import settings

# Import conditionnel selon le mode configuré
if settings.SIMPLE_MODE:
    from .main_window_old_backup import MainWindow
else:
    from .main_window import MainWindow

from .admin_panel import AdminPanel

__all__ = ['MainWindow', 'AdminPanel']




