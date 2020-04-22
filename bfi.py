#!/usr/bin/env python3

# Simple brainfuck interpreter
# -h for help

# TODO: TEST INPUT

import sys
import argparse

class ProgramException(Exception):

    def __init__(self, operation, line, message):
        s = "\n\nException on operation '{}' at line {}: {}"
        s = s.format(operation, line, message)

        super().__init__(s)

        self.operation = operation
        self.line = line
        self.message = message

class BrainfuckInterpreter:

    def __init__(self, program, memsize, wordsize, wrap):
        self.program = program
        self.pc = 0
        self.pointer = 0
        self.memory = [0] * memsize
        self.wordsize = wordsize
        self.wordmax = (2 ** wordsize) - 1
        self.operation = "\0"
        self.wrap = wrap
        self.line = 0
        self.close = False
    
    def checkmem(self):
        if self.pointer < 0 or self.pointer >= len(self.memory):
            raise ProgramException(self.operation, self.line, "Memory error")
    
    def increment(self):
        self.checkmem()

        if self.memory[self.pointer] == self.wordmax:
            self.memory[self.pointer] = -1

        self.memory[self.pointer] += 1
    
    def decrement(self):
        self.checkmem()

        if self.memory[self.pointer] == 0:
            self.memory[self.pointer] = self.wordmax
        else:
            self.memory[self.pointer] -= 1
    
    def advance(self):
        self.pointer += 1

        if self.wrap and self.pointer >= len(self.memory):
            self.pointer = 0
    
    def retreat(self):
        self.pointer -= 1

        if self.wrap and self.pointer < 0:
            self.pointer = len(self.memory) - 1
    
    def start_test(self):
        self.checkmem()

        if self.memory[self.pointer] == 0:
            # Jump to corresponding "]"
            level = 1
            while level > 0:
                self.pc += 1
                if self.pc >= len(self.program):
                    self.close = True
                else:
                    op = self.program[self.pc]
                    if op == "[":
                        level += 1
                    elif op == "]":
                        level -= 1
    
    def end_test(self):
        self.checkmem()

        if self.memory[self.pointer] != 0:
            # Jump to corresponding "["
            level = 1
            while level > 0:
                self.pc -= 1
                if self.pc < 0:
                    self.close = True
                else:
                    op = self.program[self.pc]
                    if op == "]":
                        level += 1
                    elif op == "[":
                        level -= 1
    
    def output(self):
        self.checkmem()
        sys.stdout.write(chr(self.memory[self.pointer]))
        sys.stdout.flush()
    
    def input(self):
        self.checkmem()
        i = sys.stdin.buffer.read(1)
        if i:
            i = ord(i)
            if i > self.wordmax:
                raise ProgramException(self.operation, self.line,
                    "Input provided does not fit in {}-bit cell: {}".format(self.wordsize, i))
            self.memory[self.pointer] = i
    
    def run(self):
        while not self.close:
            self.pc += 1
            if self.pc >= len(self.program):
                break

            self.operation = self.program[self.pc]
            c = self.operation
            
            if   c == "+": self.increment()
            elif c == "-": self.decrement()
            elif c == ">": self.advance()
            elif c == "<": self.retreat()
            elif c == "[": self.start_test()
            elif c == "]": self.end_test()
            elif c == ".":
                self.output()
            elif c == ",": self.input()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Simple Brainfuck interpreter")
    parser.add_argument("program", type=str, help="program file")
    parser.add_argument("-m", "--memsize", type=int, help="memory size in cells", default=512)
    parser.add_argument("-c", "--cellwidth", type=int, help="cell size in bits", default=8)
    parser.add_argument("-w", "--wrap", action="store_true", help="wrap memory")
    args = parser.parse_args()

    if args.memsize < 0 or args.cellwidth < 0:
        print("Invalid negative arguments", file=sys.stderr)
        exit(1)

    data = None

    # Read program
    with open(args.program, "r") as ifile:
        data = ifile.read()
    
    interpreter = BrainfuckInterpreter(data, args.memsize, args.cellwidth, args.wrap)
    interpreter.run()
