### English
# Simple Python Implementation of Cyclic Obfuscation of Logic Circuits 
This is a simple Python project that offers the ability to lock a logic circuit 
and perform a SAT attack via functions implemented in various Python modules. The
main functionality which each module offers are stated below.


## Module circuit.py: 
Contains classes for representation of logic circuit and methonds that can load 
a logic ciruit from file and simulate its functionality.

## Class : Circuit
Class that represents logic circuit.
Main methods:

- ```__init__(self, bench_file: str):```
  - Description:
    - Initializes an instance of Circuit based on input file. 
    - Examples of input files are in directories /circuits or /cyclocked
  - Example:

```
from circuit import Circuit
c = Circuit('circuits/c432.bench')
```
   

- ```simulate(self, inputs: list[bool]) -> list[bool]:```
  - Description:
    - Simulates the functionality of circuit.
  - Example:

```python
import random
from circuit import Circuit
c = Circuit('circuits/c432.bench')
inp = [random.choice([True, False]) for _ in range(36)]
out = c.simulate(inp)
```

- ```to_file(self, file_name: str) -> None:```
  - Description:
    - Writes Circuit to file.
  - Example:

```python
from circuit import Circuit
c = Circuit('circuits/c432.bench')
c.to_file('circuits/c432_2.bench')
```


## Module locking_module.py: 
Contains functions making it possible to lock circuit. Main function used for this purpose:
- ```lock_circuit(c: Circuit, max_len: int, max_num: int, key: list[bool]) -> Circuit:```
  - Description:
    - Finds max_num number of routes of length max_len in circuit and locks them with key via inserting MUX gates into circuit.
  - Example:

```python
import random
from circuit import Circuit
from locking_module import lock_circuit
c = Circuit('circuits/c432.bench')
key = [random.choice([True, False]) for _ in range(36)]
cl = lock_circuit(c, 6, 6, key)
```


## Module attack_module.py: 
Contains functions that allow to run SAT attack on locked circuit. Main functions used for this purpose:
- ```sat_attack(c1: Circuit, oracle: Circuit, solver_name='m22', limit=100, details=True) -> (bool, list[bool]):```
  - Description:
    - Performs a SAT attack on locked circuit c1 using original circuit as an oracle. 
    - Returns the number of iterations of SAT attack and estimated key.
  - Example:

```python
import random
from circuit import Circuit
from locking_module import lock_circuit
from attack_module import sat_attack
c = Circuit('circuits/c432.bench')
key = [random.choice([True, False]) for _ in range(36)]
cl = lock_circuit(c, 6, 6, key)
i, est_key = sat_attack(cl, c)
```

- ```get_success_rate(correct_key: list[bool], estimated_key: list[bool]) -> float:```
  - Description:
    - Returns percentage of how many bits of keys equivalent.
  - Example:

```python
import random
from circuit import Circuit
from locking_module import lock_circuit
from attack_module import sat_attack, get_success_rate
c = Circuit('circuits/c432.bench')
key = [random.choice([True, False]) for _ in range(36)]
cl = lock_circuit(c, 6, 6, key)
i, est_key = sat_attack(cl, c)
s = get_success_rate(key, est_key)
```
