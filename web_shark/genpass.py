
from os import urandom


def generate_temp_password(length):
    """ Генератор паролей

    """
    chars = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghjklmnopqrstuvwxyz23456789"
    len_pass = 15

    if not isinstance(length, int) or length < len_pass:
        raise ValueError("temp password must have positive length")

    return ''.join([chars[c % len(chars)] for c in urandom(length)])


if __name__ == '__main__':

    for b in range(0, 31, 1):
        print(generate_temp_password(15))