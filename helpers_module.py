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


def swap_dict(d: dict) -> dict:
    """
    Returns a dictionaty with swapped keys and values.
    :param d: dictionary
    :return: swapped dictionary
    """
    return {v: k for k, v in d.items()}


def get_success_rate(correct_key: list[bool], estimated_key: list[bool]) -> float:
    """
    Returns percentage of in how many bits are keys equivalent.
    :param correct_key: correct key to ciruit
    :param estimated_key: key estimated by SAT solver
    :return: percentage
    """
    success = 0
    for i, j in enumerate(estimated_key):
        if j == correct_key[i]:
            success += 1
    return success / len(correct_key) * 100
