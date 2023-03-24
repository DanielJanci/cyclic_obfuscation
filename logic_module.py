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


# def general_op(op: str, a: int, b=None, s=None) -> int:
#     if op == 'not':
#         return not_op(a)
#     elif op == 'buf':
#         return a
#     elif op == 'input':
#         return a
#     elif op == 'or':
#         return or_op(a, b)
#     elif op == 'nor':
#         return nor_op(a, b)
#     elif op == 'and':
#         return and_op(a, b)
#     elif op == 'nand':
#         return nand_op(a, b)
#     elif op == 'xor':
#         return xor_op(a, b)
#     elif op == 'xnor':
#         return xnor_op(a, b)
#     elif op == 'mux':
#         return mux_op(a, b, s)
