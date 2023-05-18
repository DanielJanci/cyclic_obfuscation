### English
# Simple Python Implementation of Cyclic Obfuscation of Logic Circuits 
This is a simple Python project that offers the ability to lock a logic circuit 
and perform a SAT attack via functions implemented in various Python modules. The
main functionality which each module offers are stated below.


## Module **circuit.py**: 
Contains classes for representation of logic circuit and methonds that can load 
a logic ciruit from file and simulate its functionality.

## Class : Circuit
Class that represents logic circuit.
Main methods:

###'''__init__(self, bench_file: str):'''
- Description
  - Initializes an instance of Circuit based on input file. 
  - Examples of input files are in directories /circuits or /cyclocked
- Example:

'''
from circuit import Circuit
c = Circuit('circuits/c432.bench')
'''
   

###'''simulate(self, inputs: list[bool]) -> list[bool]:'''
- Description
  - Simulates the functionality of circuit.
- Example:

'''
from circuit import Circuit
c = Circuit('circuits/c432.bench')
inp = [random.choice([True, False]) for _ in range(36)]
out = c.simulate(inp)
'''

###'''to_file(self, file_name: str) -> None:'''
- Description
  - Writes Circuit to file.
- Example:

'''
from circuit import Circuit
c = Circuit('circuits/c432.bench')
c.to_file('circuits/c432_2.bench')
'''
