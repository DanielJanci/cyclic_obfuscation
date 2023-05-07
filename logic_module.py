def and_op(a: bool, b: bool) -> bool:
    return a and b


def nand_op(a: bool, b: bool) -> bool:
    return not and_op(a, b)


def or_op(a: bool, b: bool) -> bool:
    return a or b


def nor_op(a: bool, b: bool) -> bool:
    return not or_op(a, b)


def xor_op(a: bool, b: bool) -> bool:
    return a ^ b


def xnor_op(a: bool, b: bool) -> bool:
    return not xor_op(a, b)


def not_op(a: bool) -> bool:
    return not a


def mux_op(a: bool, b: bool, s: bool) -> bool:
    return b if s else a


def multi_or(a: list[bool]) -> bool:
    res = a[0]
    for i in range(1, len(a)):
        res = or_op(res, a[i])
    return res


def multi_nor(a: list[bool]) -> bool:
    res = a[0]
    for i in range(1, len(a)):
        res = nor_op(res, a[i])
    return res


def multi_and(a: list[bool]) -> bool:
    res = a[0]
    for i in range(1, len(a)):
        res = and_op(res, a[i])
    return res


def multi_nand(a: list[bool]) -> bool:
    return not multi_and(a)


def multi_xor(a: list[bool]) -> bool:
    res = a[0]
    for i in range(1, len(a)):
        res = xor_op(res, a[i])
    return res


def multi_xnor(a: list[bool]) -> bool:
    res = a[0]
    for i in range(1, len(a)):
        res = xnor_op(res, a[i])
    return res


def general_op(operation: str, inputs: list[bool]) -> bool:
    """
    Returns result values of boolean operation.
    :param operation: type of operation
    :param inputs: input values
    :return: result values of opereation
    """
    if operation == 'buf':
        return inputs[0]
    elif operation == 'not':
        return not_op(inputs[0])
    elif operation == 'or':
        return multi_or(inputs)
    elif operation == 'nor':
        return multi_nor(inputs)
    elif operation == 'and':
        return multi_and(inputs)
    elif operation == 'nand':
        return multi_nand(inputs)
    elif operation == 'xor':
        return multi_xor(inputs)
    elif operation == 'xnor':
        return multi_xnor(inputs)
    elif operation == 'mux':
        return mux_op(inputs[0], inputs[1], inputs[2])
