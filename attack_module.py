from pysat.solvers import Solver
from copy import deepcopy
from collections import OrderedDict
from circuit import Circuit


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


def circuit_to_cnf(c: Circuit) -> list[list[int]]:
    """
    Creates cnf formula representing circuit.
    :param c: Circuit
    :return: cnf formula representing circuit
    """
    cnf = []
    for name in c.gates:
        if c.gates[name].operation != 'input':
            if len(c.gates[name].inputs) == 1:
                cnf.extend(tseytin(c.gates[name].operation,
                                   c.literals[name],
                                   c.literals[c.gates[name].inputs[0]]))
            else:
                cnf.extend(tseytin(c.gates[name].operation,
                                   c.literals[name],
                                   c.literals[c.gates[name].inputs[0]],
                                   c.literals[c.gates[name].inputs[1]]))
    return cnf


def solve_cnf(cnf: list[list[int]], solver_name='m22') -> (bool, list[int]):
    """
    Creates an instance of SAT Slover and solves cnf. Returns bool (sat) and model (value assignment).
    :param cnf: cnf
    :param solver_name: name of sat solver
    :return: sat, value assignment
    """
    solver = Solver(name=solver_name, bootstrap_with=cnf)
    is_sat = solver.solve()
    model = solver.get_model()
    solver.delete()
    return is_sat, model


def model_to_result(c: Circuit, model: list[int]) -> dict:
    """
    Returns assigned values to circuit.
    :param c: Circuit
    :param model: value assignment
    :return: assigned values
    """
    res = OrderedDict()
    tmp = swap_dict(c.literals)
    for lit in model:
        if lit in tmp or neg_lit(lit) in tmp:
            if lit > 0:
                res[tmp[lit]] = True
            else:
                res[tmp[neg_lit(lit)]] = False
    return res


def diff_out_cnf(lits1: dict, lits2: dict, counter: int) -> list[list[int]]:
    """
    Returns cnf for [Y1 != Y2].
    :param lits1: outputs of 1st circuit
    :param lits2: outputs of 2nd circuit
    :param counter: coutner for where to start new literals
    :return: cnf
    """
    cnf = []
    new_lit = counter
    last_clause = []
    for name in lits1:
        new_lit += 1
        last_clause.append(new_lit)
        cnf.append([neg_lit(new_lit), lits1[name]])
        cnf.append([neg_lit(new_lit), neg_lit(lits2[name])])
        new_lit += 1
        last_clause.append(new_lit)
        cnf.append([neg_lit(new_lit), neg_lit(lits1[name])])
        cnf.append([neg_lit(new_lit), lits2[name]])
    cnf.append(last_clause)
    return cnf


def dip_cnf(c: Circuit, dip_x: list[int], dip_y: list[int]) -> list[list[int]]:
    """
    Returns value assignements from DIP to cnf.
    :param c: Circuit
    :param dip_x: differentiating input pattern
    :param dip_y: differentiating output pattern
    :return: cnf with assigned values
    """
    cnf = []
    for i, name in enumerate(c.input_gates):
        if dip_x[i] == 0:
            cnf.append([neg_lit(c.literals[name])])
        else:
            cnf.append([c.literals[name]])

    for i, name in enumerate(c.output_gates):
        if dip_y[i] == 0:
            cnf.append([neg_lit(c.literals[name])])
        else:
            cnf.append([c.literals[name]])
    return cnf


def copy_circuit_for_init(c: Circuit) -> Circuit:
    """
    Returns a copy of circuit with new literals (except for input literals).
    :param c: Circuit
    :return: Circuit with new literals
    """
    c_copy = deepcopy(c)
    new_lit = len(c.literals) + 1
    for name in c.literals:
        if name not in c.input_gates:
            c_copy.literals[name] = new_lit
            new_lit += 1
    return c_copy


def copy_circuit_for_dip(c: Circuit, counter: int) -> Circuit:
    """
    Returns a copy of circuit with new literals (except for key literals).
    :param c: Circuit
    :param counter: coutner for where to start new literals
    :return: Circuit with new literals
    """
    c_copy = deepcopy(c)
    new_lit = counter + 1
    for name in c.literals:
        if name not in c.key_gates:
            c_copy.literals[name] = new_lit
            new_lit += 1
    return c_copy


def sat_attack(c1: Circuit, oracle: Circuit, solver_name='m22', limit=100, details=True):
    """
    Performs a classic SAT attack on locked circuit.
    :param c1: locked Circuit
    :param oracle: unlocked Circuit
    :param solver_name: name of SAT solver
    :param limit: max iterations
    :param details: print details of attack
    :return: iterations, estimated key
    """
    if details:
        print(f'Performing SAT attack on {c1.file_name} ...')
    c1.simplify_gates()
    last_lit_key = list(c1.literals)[-1]
    c2 = copy_circuit_for_init(c1)
    counter = c2.literals[last_lit_key]
    cnf_i = circuit_to_cnf(c1) + circuit_to_cnf(c2)
    diff_out = diff_out_cnf(c1.output_literals(), c2.output_literals(), counter)
    is_sat, model = solve_cnf(cnf_i + diff_out, solver_name)
    i = 1
    while is_sat and i < limit:
        assign1 = model_to_result(c1, model)
        dip_x = [v for k, v in assign1.items() if k in c1.input_gates]
        dip_y = oracle.simulate(dip_x)

        c1_copy = copy_circuit_for_dip(c1, counter)
        counter = c1_copy.literals[last_lit_key]
        c2_copy = copy_circuit_for_dip(c2, counter)
        counter = c2_copy.literals[last_lit_key]

        cnf1 = circuit_to_cnf(c1_copy)
        cnf2 = circuit_to_cnf(c2_copy)
        dip1 = dip_cnf(c1_copy, dip_x, dip_y)
        dip2 = dip_cnf(c2_copy, dip_x, dip_y)
        cnf_i += (cnf1 + cnf2 + dip1 + dip2)

        diff_out = diff_out_cnf(c1.output_literals(), c2.output_literals(), counter)
        is_sat, model = solve_cnf(cnf_i + diff_out, solver_name)
        i += 1

    is_sat, model = solve_cnf(cnf_i, solver_name)
    assign = model_to_result(c1, model)
    estimated_key = [v for k, v in assign.items() if k in c1.key_gates]
    success = get_success_rate(c1.correct_key, estimated_key)
    if details:
        print(f'    iterations: {i}')
        print(f'    estimated key: {"".join([str(int(b)) for b in estimated_key])}')
        print(f'    correct key:   {"".join([str(int(b)) for b in c1.correct_key])}')
        print(f'    success rate: {round(success, 3)}%')
        print()
    return i, estimated_key
