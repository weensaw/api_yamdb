import random
import string


def generate_confirmation_code(length=6):
    """
    Генерирует случайный код подтверждения
    """
    return ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=length))
