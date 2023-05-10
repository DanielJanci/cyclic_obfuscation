from circuit import Circuit, Gate
from copy import deepcopy
from random import choice
from collections import OrderedDict


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
    pos = len(c.input_gates)
    items = list(c.gates.items())
    for i in range(len(key)):
        k_g = Gate('input', f'k{i}', [])
        c.key_gates.append(k_g.name)
        items.insert(pos, (k_g.name, k_g))
        pos += 1
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


def available_gates(c: Circuit, routes: list[list[str]]) -> list[str]:
    """
    Returns list of gates that can be randomly selected in lock_route.
    :param c: Circuit
    :param routes: lists of gates creating a cycle
    :return: list of gates
    """
    avail_gates = set(c.gates.keys() - set(c.input_gates) - set(c.key_gates))
    for r in routes:
        avail_gates -= set(r)
    return list(avail_gates)


def lock_route(c: Circuit, graph: dict, route: list[str], key: list[bool], r_counter: int, avail_g: list[str]) -> None:
    """
    Inserts mux key gates to Circuit in a way so it creates a cycle from nodes in route (last node of route is
    connected to the 1st node).
    :param avail_g: gates thats can be connected with mux gates
    :param c: Circuit
    :param graph: graph representation of Circuit
    :param route: list of gates creating a cycle
    :param key: key
    :param r_counter: counter
    :return: None
    """
    for i, next_g in enumerate(route):
        mux_name = f'm{r_counter + i}'
        key_g = f'k{r_counter + i}'
        pos = list(c.gates.keys()).index(next_g)

        if i == 0:
            prev_g1 = c.gates[next_g].inputs[0]
            prev_g2 = route[-1]
            add_mux_gate(c, mux_name, next_g, prev_g1, prev_g2, key_g, key[r_counter + i], pos)

        else:
            prev_g1 = route[i - 1]
            prev_g2 = choice(avail_g)
            add_mux_gate(c, mux_name, next_g, prev_g1, prev_g2, key_g, key[r_counter + i], pos)

        if len(graph[prev_g1]) == 1:
            new_next_g = choice(avail_g)
            new_pos = list(c.gates.keys()).index(new_next_g)
            prev_g2 = prev_g1
            prev_g1 = c.gates[new_next_g].inputs[0]
            mux_name = f'mm{r_counter + i}'
            add_mux_gate(c, mux_name, new_next_g, prev_g1, prev_g2, key_g, key[r_counter + i], new_pos)


def lock_circuit(c: Circuit, max_len: int, max_num: int, key: list[bool]) -> Circuit:
    """
    Finds routes in Circuit and locks them.
    :param c: Circuit
    :param max_len: length of routes
    :param max_num: number of routes
    :param key: key
    :return: None
    """
    c_l = deepcopy(c)
    add_key(c_l, key)
    g = c_l.to_graph()

    routes = find_routes(c_l, g, max_len, max_num)
    attempts = 100
    while len(routes) < max_num and attempts > 0:
        print(f"Couldn't find {max_num} routes of length {max_len}, Trying again... Remaining attempts: {attempts}")
        routes = find_routes(c_l, g, max_len, max_num)
        attempts -= 1

    r_counter = 0
    avail_g = available_gates(c_l, routes)
    for r in routes:
        lock_route(c_l, g, r, key, r_counter, avail_g)
        r_counter += len(r)
    return c_l


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
