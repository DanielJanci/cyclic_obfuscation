def binlist(val: int, val_len: int) -> list[bool]:
    """
    Returns a list of bool values (as binary list) representing an integer.
    :param val: integer value
    :param val_len: length of bool list
    :return: bool list
    """
    return [bool(int(j)) for j in f'{val:0{val_len + 2}b}'[2:]]


def generate_binlist(val_len: int) -> list[list[bool]]:
    """
    Generator that yields binlists from value 0 to 2**"length of bool list"
    :param val_len: length of bool list
    :return: list of bool lists
    """
    for i in range(2**val_len):
        yield binlist(i, val_len)
