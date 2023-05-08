from collections import defaultdict, OrderedDict
from logic_module import general_op


class Gate:
    """
    A class that represents gate in a circuit.
    operation -> a type of operation the gate holds
    inputs -> names of gates of inputs
    name -> name of the gate
    value -> current value the gate has
    """
    def __init__(self, operation: str, name: str, inputs: list[str]):
        """
        Creates a gate.
        :param operation: a type of operation the gate holds
        :param name: name of the gate
        :param inputs: names of gates of inputs
        """
        self.operation = operation
        self.inputs = inputs
        self.name = name
        self.value = None


class Circuit:
    """
    A class that represents ciruit.
    file_name -> name of the file from which the ciruit is loaded
    input_gates -> list of names of input gates
    output_gates -> list of names of output gates
    key_gates -> list of names of key gates
    literals -> literals representing each gate in cnf
    gates -> all of the gates stored in gict (key = name fo the gate, value = Gate instance)
    is_locked -> bool value thats tells if the circuit is locked
    correct_key -> correct key loaded from the file (if the ciruit is locked)
    """
    def __init__(self, bench_file: str):
        """
        Creates a circuit from file. When loading a locked ciruit, key inputs must contain letter k in the file and any
        other gates must not.
        :param bench_file: name of the file
        """
        self.file_name = bench_file
        self.input_gates = []
        self.output_gates = []
        self.key_gates = []
        self.literals = OrderedDict()
        self.gates = OrderedDict()
        self.correct_key = []
        self.load_from_file(bench_file)

    def load_from_file(self, bench_file: str):
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

    def simplify_gates(self) -> None:
        """
        Simplifies gates so that each one has at most 2 inputs.
        :return: None
        """
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

    def to_graph(self) -> dict:
        """
        Returns graph representation of circuit.
        :return: graph as a dict
        """
        graph = defaultdict(list)
        for g in self.gates:
            if self.gates[g].operation != 'input':
                for i in self.gates[g].inputs:
                    graph[i].append(g)
        return graph

    def simulate(self, inputs: list[bool]) -> list[bool]:
        """
        Inserts input values to input gates, evaluates ciruits output, which is then returned.
        :param inputs: input values
        :return: circuits output
        """
        for i, name in enumerate(self.input_gates):
            self.gates[name].value = inputs[i]
        for name in self.gates:
            if self.gates[name].operation != 'input':
                inputs = [self.gates[name2].value for name2 in self.gates[name].inputs]
                self.gates[name].value = general_op(self.gates[name].operation, inputs)
        return [self.gates[name].value for name in self.output_gates]

    def key_literals(self) -> dict:
        """
        Returns dict of key literals.
        :return: dict of key literals
        """
        key_lit = dict()
        for g in self.literals:
            if 'k' in g:
                key_lit[g] = self.literals[g]
        return key_lit

    def input_literals(self) -> dict:
        """
        Returns dict of input literals.
        :return: dict of input literals
        """
        input_lit = dict()
        for g in self.literals:
            if g in self.input_gates:
                input_lit[g] = self.literals[g]
        return input_lit

    def output_literals(self) -> dict:
        """
        Returns dict of output literals.
        :return: dict of output literals
        """
        output_lit = dict()
        for g in self.literals:
            if g in self.output_gates:
                output_lit[g] = self.literals[g]
        return output_lit

    def to_file(self, file_name: str) -> None:
        """
        Writes ciruit to a file.
        :param file_name: name of the file
        :return: None
        """
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
