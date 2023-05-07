from collections import defaultdict, OrderedDict
from helpers_module import tseytin
from logic_module import general_op


class Gate:
    def __init__(self, operation: str, name: str, inputs: list[str]):
        self.operation = operation
        self.inputs = inputs
        self.name = name
        self.value = None


class Circuit:
    def __init__(self, bench_file):
        self.file_name = bench_file
        self.input_gates = []
        self.output_gates = []
        self.key_gates = []
        self.literals = OrderedDict()
        self.gates = OrderedDict()
        self.is_locked = False
        self.correct_key = []

        with open(bench_file, 'r') as bf:
            for line in bf:
                line = line.strip().lower()
                if line:
                    if line[0] != '#':
                        if 'input(' in line:
                            tmp = line.replace('input(', '').replace(')', '').strip()
                            if 'k' in tmp:
                                self.key_gates.append(tmp)
                            else:
                                self.input_gates.append(tmp)
                            self.gates[tmp] = Gate('input', tmp, [])
                        elif 'output(' in line:
                            tmp = line.replace('output(', '').replace(')', '').strip()
                            self.output_gates.append(tmp)
                        else:
                            tmp_s1 = line.split('=')
                            name = tmp_s1[0].strip()
                            tmp_s2 = tmp_s1[1].replace('(', ', ').replace(')', '').split(', ')
                            operation = tmp_s2[0].strip()
                            inputs = []
                            for i in tmp_s2[1:]:
                                i.strip()
                                inputs.append(i)
                            self.gates[name] = Gate(operation, name, inputs)
                    else:
                        if '#0' in line or '#1' in line:
                            self.correct_key = [bool(int(i)) for i in line[1:]]
        if len(self.key_gates) > 0:
            self.is_locked = True

    def simplify_gates(self):
        new_gates = dict()
        cnt = 0
        for name in self.gates:
            if len(self.gates[name].inputs) <= 2:
                new_gates[name] = self.gates[name]
            elif self.gates[name].operation == 'mux':
                new_name1 = f'g_{cnt}'
                cnt += 1
                new_name2 = f'g_{cnt}'
                cnt += 1
                new_name3 = f'g_{cnt}'
                cnt += 1
                new_gates[new_name1] = Gate('not', new_name1, [self.gates[name].inputs[2]])
                new_gates[new_name2] = Gate('and', new_name2, [self.gates[name].inputs[0], new_name1])
                new_gates[new_name3] = Gate('and', new_name3, [self.gates[name].inputs[1], self.gates[name].inputs[2]])
                new_gates[name] = Gate('or', name, [new_name2, new_name3])
            else:
                if self.gates[name].operation == 'nand':
                    new_operation = 'and'
                else:
                    new_operation = self.gates[name].operation
                new_name1 = f'g_{cnt}'
                cnt += 1
                new_gates[new_name1] = Gate(new_operation,
                                            new_name1,
                                            [self.gates[name].inputs[0], self.gates[name].inputs[1]])
                for i in range(2, len(self.gates[name].inputs)):
                    new_name2 = f'g_{cnt}'
                    cnt += 1
                    if i == len(self.gates[name].inputs) - 1:
                        if self.gates[name].operation == 'nand':
                            new_gates[name] = Gate('nand', name, [self.gates[name].inputs[i], new_name1])
                        else:
                            new_gates[name] = Gate(new_operation, name, [self.gates[name].inputs[i], new_name1])
                    else:
                        new_gates[new_name2] = Gate(new_operation, new_name2, [self.gates[name].inputs[i], new_name1])
                    new_name1 = new_name2
        self.gates = new_gates
        for i, name in enumerate(self.gates):
            self.literals[name] = i + 1

    def to_cnf(self) -> list[list[int]]:
        cnf = []
        for name in self.gates:
            if self.gates[name].operation != 'input':
                if len(self.gates[name].inputs) == 1:
                    cnf.extend(tseytin(self.gates[name].operation,
                                       self.literals[name],
                                       self.literals[self.gates[name].inputs[0]]))
                else:
                    cnf.extend(tseytin(self.gates[name].operation,
                                       self.literals[name],
                                       self.literals[self.gates[name].inputs[0]],
                                       self.literals[self.gates[name].inputs[1]]))
        return cnf

    def to_graph(self) -> dict:
        graph = defaultdict(list)
        for g in self.gates:
            if self.gates[g].operation != 'input':
                for i in self.gates[g].inputs:
                    graph[i].append(g)
        return graph

    def unlock(self) -> None:
        if self.is_locked:
            for i, k in enumerate(self.key_gates):
                self.gates[k].value = self.correct_key[i]
            self.is_locked = False

    def simulate(self, inputs: list[bool]) -> list[bool]:
        if not self.is_locked:
            for i, name in enumerate(self.input_gates):
                self.gates[name].value = inputs[i]
        for name in self.gates:
            if self.gates[name].operation != 'input':
                inputs = [self.gates[name2].value for name2 in self.gates[name].inputs]
                self.gates[name].value = general_op(self.gates[name].operation, inputs)
        return [self.gates[name].value for name in self.output_gates]

    def reset_values(self) -> None:
        for name in self.gates:
            self.gates[name].value = None
        self.is_locked = True

    def key_literals(self) -> dict:
        key_lit = dict()
        for g in self.literals:
            if 'k' in g:
                key_lit[g] = self.literals[g]
        return key_lit

    def input_literals(self) -> dict:
        input_lit = dict()
        for g in self.literals:
            if g in self.input_gates:
                input_lit[g] = self.literals[g]
        return input_lit

    def output_literals(self) -> dict:
        output_lit = dict()
        for g in self.literals:
            if g in self.output_gates:
                output_lit[g] = self.literals[g]
        return output_lit

    def to_file(self, file_name: str) -> None:
        with open(file_name, 'w') as f:
            f.write(f'#{"".join(str(int(i)) for i in self.correct_key)}\n')
            for in_g in self.input_gates:
                f.write(f'INPUT({in_g})\n')
            for k_g in self.key_gates:
                f.write(f'INPUT({k_g})\n')
            for out_g in self.output_gates:
                f.write(f'OUTPUT({out_g})\n')
            f.write('\n')
            for g in self.gates:
                if self.gates[g].operation != 'input':
                    f.write(f'{self.gates[g].name} = {self.gates[g].operation}({", ".join(self.gates[g].inputs)})\n')
