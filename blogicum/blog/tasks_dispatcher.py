from celery import shared_task
import importlib
import time


REGISTERED_FUNCTIONS = {}
"""Регистрируемые функции."""

ALLOWED_FUNCTIONS = {
    'run_rag_process',
    'blog.tasks.run_rag_process',

    'run_statistical_analysis',
    'blog.tasks.run_statistical_analysis',

    'get_completion',
    'blog.tasks.get_completion',
}
"""Разрешенные функции. Задавать имена без полного пути."""


def register_task(name):
    """Декоратор регистрирует функцию как доступную для удаленного вызова."""
    def decorator(func):
        REGISTERED_FUNCTIONS[name] = func
        return func
    return decorator


def get_function(name):
    """Возвращает функцию по имени."""
    if name not in ALLOWED_FUNCTIONS:
        raise PermissionError(f"Function {name} is not in whitelist")

    if name in REGISTERED_FUNCTIONS:
        return REGISTERED_FUNCTIONS[name]
    else:
        try:
            module_path, func_name = name.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        except (ValueError, ImportError, AttributeError) as e:
            raise ValueError(f'Function {name} not found: {e}')


@shared_task(bind=True)
def run_task(self, func_name, args=None, kwargs=None):
    """Выполняет зарегистрированную функцию."""
    args = args or []
    kwargs = kwargs or {}

    try:
        func = get_function(func_name)
        result = func(*args, **kwargs)
        return {
            'status': 'success',
            'result': result,
            'function': func_name
        }
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
