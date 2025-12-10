from django.core.exceptions import ValidationError


def title_without_dot(value: str) -> None:
    """Заголовок публикации не должден заканчиваться точкой."""
    if value[-1] == '.':
        raise ValidationError(
            'Заголовок публикации не должен заканчиваться точкой'
        )
