def neg_lit(lit: int) -> int:
    """
    Returns a negation of literal.
    :param lit: literal
    :return: negation of literal
    """
    return lit * (-1)


def tseytin(operand: str, output: int, input_a: int, input_b=None) -> list[list[int]]:
    """
    Returns a cnf representation of a gate.
    :param operand: gate operation
    :param output: name of output gate
    :param input_a: name of 1st input gate
    :param input_b: name of 2nd input gate
    :return: list of clausles (cnf)
    """
    cnf = []
    if operand == 'and':
        cnf.append([neg_lit(input_a), neg_lit(input_b), output])
        cnf.append([input_a, neg_lit(output)])
        cnf.append([input_b, neg_lit(output)])
    elif operand == 'nand':
        cnf.append([neg_lit(input_a), neg_lit(input_b), neg_lit(output)])
        cnf.append([input_a, output])
        cnf.append([input_b, output])
    elif operand == 'or':
        cnf.append([input_a, input_b, neg_lit(output)])
        cnf.append([neg_lit(input_a), output])
        cnf.append([neg_lit(input_b), output])
    elif operand == 'nor':
        cnf.append([input_a, input_b, output])
        cnf.append([neg_lit(input_a), neg_lit(output)])
        cnf.append([neg_lit(input_b), neg_lit(output)])
    elif operand == 'not':
        cnf.append([neg_lit(input_a), neg_lit(output)])
        cnf.append([input_a, output])
    elif operand == 'buf':
        cnf.append([neg_lit(input_a), output])
        cnf.append([input_a, neg_lit(output)])
    elif operand == 'xor':
        cnf.append([neg_lit(input_a), neg_lit(input_b), neg_lit(output)])
        cnf.append([input_a, input_b, neg_lit(output)])
        cnf.append([input_a, neg_lit(input_b), output])
        cnf.append([neg_lit(input_a), input_b, output])
    elif operand == 'xnor':
        cnf.append([neg_lit(input_a), neg_lit(input_b), output])
        cnf.append([input_a, input_b, output])
        cnf.append([input_a, neg_lit(input_b), neg_lit(output)])
        cnf.append([neg_lit(input_a), input_b, neg_lit(output)])
    else:
        print(f'Gate {operand} has no cnf conversion.')
    return cnf


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
    success = 0
    for i, j in enumerate(estimated_key):
        if j == correct_key[i]:
            success += 1
    return success / len(correct_key) * 100
