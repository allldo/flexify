import random


def generate_code() -> str:
    code = [str(random.randint(0, 9)) for x in range(4)]
    return ''.join(code)
