from circuit import Circuit, Gate
from copy import deepcopy
from random import choice
from collections import defaultdict, OrderedDict


def find_routes_util(graph: dict, u: str, visited: list[str], curr_route: list[str],
                     routes: list[list[str]], max_len: int) -> None:
    """
    Recursive function for finding routes. Called in "find_routes"
    :param graph: graph representation of Circuit
    :param u: current node
    :param visited: visited node
    :param curr_route: current route
    :param routes: all found routes
    :param max_len: max length of routes
    :return:
    """
    visited.append(u)
    curr_route.append(u)
    if len(curr_route) == max_len:
        routes.append(deepcopy(curr_route))
    else:
        for v in graph[u]:
            if v not in visited:
                find_routes_util(graph, v, visited, curr_route, routes, max_len)
    curr_route.pop()
    visited.remove(u)


def find_routes(c: Circuit, graph: dict, max_len: int, max_routes: int) -> list[list[str]]:
    """
    Recursively finds routes in circuit of certain quantity and length.
    :param c: Circuit
    :param graph: graph representation of Circuit
    :param max_len: max length of routes
    :param max_routes: max number of routes
    :return: routes
    """
    routes = []
    used = []
    keys = list(graph.keys() - c.input_gates)
    while len(keys) > 0:
        u = choice(keys)
        visited = []
        paths = []
        curr_path = []
        find_routes_util(deepcopy(graph), u, visited, curr_path, paths, max_len)
        keys.remove(u)
        if len(paths) > 0:
            for p in paths:
                if len(list(set(p) & set(used))) == 0:  # if there isnt an intersection of path "p" and nodes "used"
                    routes.append(p)
                    used.extend(p)
                    if len(routes) == max_routes:
                        return routes
    return routes


def add_key(c: Circuit, key: list[bool]) -> None:
    """
    Adds key_gates and correct_key to Circuit.
    :param c: Circuit
    :param key: key
    :return: None
    """
    c.correct_key = key
    c.is_locked = True
    pos = len(c.input_gates)
    items = list(c.gates.items())
    for i in range(len(key)):
        k_g = Gate('input', f'k{i}', [])
        c.key_gates.append(k_g.name)
        items.insert(pos, (k_g.name, k_g))
        pos += 1
    c.gates = OrderedDict(items)


def add_dummy_logic(c: Circuit, dummy_name1: str, dummy_name2: str, pos: int) -> None:
    """
    Adds 2 dummy gates to Circuit and connects them with 3 random input gates.
    :param c: Circuit
    :param dummy_name1: 1st dummy gate name
    :param dummy_name2: 2nd dummy gate name
    :param pos: position where to insert dummy gates in Circuit
    :return: None
    """
    dg_a = Gate('or', dummy_name1, [choice(c.input_gates), choice(c.input_gates)])
    dg_b = Gate('nand', dummy_name2, [dg_a.name, choice(c.input_gates)])
    c.dummy_gates.append(dg_a.name)
    c.dummy_gates.append(dg_b.name)
    items = list(c.gates.items())
    items.insert(pos, (dg_b.name, dg_b))
    items.insert(pos, (dg_a.name, dg_a))
    c.gates = OrderedDict(items)


def add_mux_gate(c: Circuit, mux_name: str, next_g: str, prev_g1: str, prev_g2: str, key_g: str, key_val: bool,
                 pos: int) -> None:
    """
    Adds a locking mux gate to Circuit. Depending on the value of key bit, its will swap the position of inputs of the
    mux gate.
    :param c: Circuit
    :param mux_name: name of mux gate
    :param next_g: name of following gate after mux
    :param prev_g1: name of 1st previous gate before mux
    :param prev_g2: name of 2nd previous gate before mux
    :param key_g: name of key gate
    :param key_val: value of key gate
    :param pos: position where to insert mux gate in Circuit
    :return: None
    """
    mux_g = Gate('mux', mux_name, [prev_g1, prev_g2])
    i = c.gates[next_g].inputs.index(prev_g1)
    c.gates[next_g].inputs[i] = mux_name
    items = list(c.gates.items())
    items.insert(pos, (mux_name, mux_g))
    c.gates = OrderedDict(items)
    if key_val:
        mux_g.inputs.reverse()
    mux_g.inputs.append(key_g)


def lock_route(c: Circuit, graph: dict, route: list[str], key: list[bool], r_counter: int) -> None:
    """
    Inserts mux key gates and dummy gates to Circuit in a way so it creates a cycle from nodes in route (last node of
    route is connected to the 1st node).
    :param c: Circuit
    :param graph: graph representation of Circuit
    :param route: route
    :param key: key
    :param r_counter: counter
    :return: None
    """
    for i, gate_name in enumerate(route):
        mux_name = f'm{r_counter + i}'
        key_g = f'k{r_counter + i}'
        next_g = gate_name
        pos = list(c.gates.keys()).index(next_g)
        if i == 0:
            prev_g1 = c.gates[next_g].inputs[0]
            prev_g2 = route[-1]
            add_mux_gate(c, mux_name, next_g, prev_g1, prev_g2, key_g, key[r_counter + i], pos)
        else:
            dummy_name1 = f'd{r_counter + i}_a'
            dummy_name2 = f'd{r_counter + i}_b'
            add_dummy_logic(c, dummy_name1, dummy_name2, pos)
            prev_g1 = route[i - 1]
            prev_g2 = dummy_name1
            pos = list(c.gates.keys()).index(next_g)
            add_mux_gate(c, mux_name, next_g, prev_g1, prev_g2, key_g, key[r_counter + i], pos)

            if len(graph[route[i - 1]]) == 1:
                mux_name = f'md{r_counter + i}'
                dummy_name1 = f'dd{r_counter + i}_a'
                dummy_name2 = f'dd{r_counter + i}_b'
                pos = list(c.gates.keys()).index(next_g)
                add_dummy_logic(c, dummy_name1, dummy_name2, pos)
                next_g = dummy_name2
                prev_g1 = route[i - 1]
                prev_g2 = dummy_name1
                pos = list(c.gates.keys()).index(dummy_name2)
                add_mux_gate(c, mux_name, next_g, prev_g2, prev_g1, key_g, key[r_counter + i], pos)


def lock_circuit2(c: Circuit, max_len: int, max_num: int, key: list[bool]) -> None:
    """
    Finds routes in Circuit and locks them.
    :param c: Circuit
    :param max_len: length of routes
    :param max_num: number of routes
    :param key: key
    :return: None
    """
    g = c.to_graph()
    add_key(c, key)
    routes = find_routes(c, g, max_len, max_num)
    r_counter = 0
    for r in routes:
        lock_route(c, g, r, key, r_counter)
        r_counter += len(r)


# def explore_circuit_util(c: Circuit, graph: dict, u: str, visited: list[str], curr_path: list[str],
#                          paths: list[list[str]]) -> None:
#     visited.append(u)
#     curr_path.append(u)
#     if u in c.output_gates:
#         paths.append(deepcopy(curr_path))
#     else:
#         for v in graph[u]:
#             if v not in visited:
#                 explore_circuit_util(c, graph, v, visited, curr_path, paths)
#     curr_path.pop()
#     visited.remove(u)
#
#
# def explore_circuit(c: Circuit, graph: dict) -> dict:
#     expl = defaultdict(int)
#     for u in graph:
#         if u not in c.input_gates:
#             visited = []
#             paths = []
#             curr_path = []
#             explore_circuit_util(c, deepcopy(graph), u, visited, curr_path, paths)
#             for p in paths:
#                 # print(f'{u} --> {p}')
#                 expl[len(p)] += 1
#     return dict(sorted(expl.items(), key=lambda item: item[1], reverse=True))
#
#
# def lock_circuit(c: Circuit) -> None:
#     g = c.to_graph()
#     r_qty = explore_circuit(c, g)
#     for k, v in r_qty.items():
#         print(f'route len: {k} --> qty of routes: {v}... Max possible key len: {v * k} (recommended lower)')
#
#     max_len = int(input('Input length of cyckles: '))
#     max_num = int(input('Input number of cykles: '))
#
#     key_str = str(input(f'Input key value (must be of lenght {max_num * max_len}): '))
#     key = [bool(int(c)) for c in key_str]
#     key_len = len(key)
#     while key_len != max_num * max_len:
#         key_str = str(input(f'Input key value (must be of lenght {max_num * max_len}): '))
#         key = [bool(int(c)) for c in key_str]
#         key_len = len(key)
#
#     print('Searching for possible routes...')
#     routes = find_routes(c, g, max_len, max_num)
#     while len(routes) != max_num:
#         routes = find_routes(c, g, max_len, max_num)
#     print(f'routes found: {routes}')
#
#     add_key(c, key)
#     # add_dummy_gate(c, f'd0', c.input_gates[0], list(c.gates.keys()).index(c.input_gates[0]) + 1)
#     # add_dummy_gate_simple(c, 'd0', 0)
#     r_counter = 0
#     for r in routes:
#         lock_route(c, g, r, key, r_counter)
#         r_counter += len(r)
#
#
# def add_dummy_gate(c: Circuit, dummy_name: str, prev_g: str, pos: int) -> None:
#     items = list(c.gates.items())
#     d_g = Gate('not', dummy_name, [prev_g])
#     c.dummy_gates.append(d_g.name)
#     items.insert(pos, (d_g.name, d_g))
#     c.gates = OrderedDict(items)
#
#
# def add_dummy_gate_simple(c: Circuit, dummy_name: str, pos: int) -> None:
#     items = list(c.gates.items())
#     d_g = Gate('input', dummy_name, [])
#     d_g.value = choice([True, False])
#     c.dummy_gates.append(d_g.name)
#     items.insert(pos, (d_g.name, d_g))
#     c.gates = OrderedDict(items)
#
#
# def add_dummy_mux_simple(c: Circuit, mux_name: str, prev_g1: str, prev_g2: str, key_g: str, key_val: bool, pos: int) -> None:
#     mux_g = Gate('mux', mux_name, [prev_g1, prev_g2])
#     items = list(c.gates.items())
#     items.insert(pos, (mux_name, mux_g))
#     c.gates = OrderedDict(items)
#     if key_val:
#         mux_g.inputs.reverse()
#     mux_g.inputs.append(key_g)
#
#
# def lock_route_simple(c: Circuit, graph: dict, route: list[str], key: list[bool], r_counter: int):
#     for i, name in enumerate(route):
#         mux_name = f'm{r_counter + i}'
#         key_g = f'k{r_counter + i}'
#         next_g = name
#         if i == 0:
#             prev_g1 = c.gates[next_g].inputs[0]
#             prev_g2 = route[-1]
#         else:
#             prev_g1 = route[i - 1]
#             prev_g2 = c.dummy_gates[-1]
#             add_dummy_gate_simple(c, f'd{len(c.dummy_gates)}', list(c.gates.keys()).index(prev_g2) + 1)
#
#         m_pos = list(c.gates.keys()).index(next_g)
#         add_mux_gate(c, mux_name, next_g, prev_g1, prev_g2, key_g, key[r_counter + i], m_pos)
#
#         if len(graph[route[i - 1]]) == 1:
#             mux_name = f'{mux_name}_d'
#             prev_g1 = route[i - 1]
#             prev_g2 = c.dummy_gates[-1]
#             m_pos = list(c.gates.keys()).index(prev_g1) + 1
#             add_dummy_mux_simple(c, mux_name, prev_g1, prev_g2, key_g, key[r_counter + i], m_pos)
#
#
# def lock_route(c: Circuit, graph: dict, route: list[str], key: list[bool], r_counter: int) -> None:
#     for i, name in enumerate(route):
#         mux_name = f'm{r_counter + i}'
#         key_g = f'k{r_counter + i}'
#         next_g = name
#         if i == 0:
#             prev_g1 = c.gates[next_g].inputs[0]
#             prev_g2 = route[-1]
#         else:
#             prev_g1 = route[i - 1]
#             prev_g2 = c.dummy_gates[-1]
#             d_pos = list(c.gates.keys()).index(prev_g2) + 1
#             add_dummy_gate(c, f'd{len(c.dummy_gates)}', prev_g2, d_pos)
#
#         m_pos = list(c.gates.keys()).index(next_g)
#         add_mux_gate(c, mux_name, next_g, prev_g1, prev_g2, key_g, key[r_counter + i], m_pos)
#
#         if len(graph[route[i - 1]]) == 1:
#             mux_name = f'{mux_name}_d'
#             next_g = f'd{len(c.dummy_gates)}'
#             prev_g1 = route[i - 1]
#             prev_g2 = c.dummy_gates[-1]
#
#             m_pos = list(c.gates.keys()).index(prev_g1) + 1
#             d_pos = m_pos + 1
#             add_dummy_gate(c, next_g, c.dummy_gates[-1], d_pos)
#             add_mux_gate(c, mux_name, next_g, prev_g2, prev_g1, key_g, key[r_counter + i], m_pos)
