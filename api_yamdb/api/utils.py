import uuid


def generate_confirmation_code():
    """Генерирует случайный UUID объект"""
    return str(uuid.uuid4())
