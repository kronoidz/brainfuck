#!/usr/bin/env python3

# Brainfuck compiler

from argparse import ArgumentParser
from collections import deque
from subprocess import run
from os import name as osname

if __name__ == "__main__":
    parser = ArgumentParser(description="Brainfuck x86-64 compiler")
    parser.add_argument("inputfile", type=str, help="brainfuck program file")
    parser.add_argument("-m", "--memsize", type=int, help="memory size in bytes", default=512, nargs="?")
    parser.add_argument("-b", "--build", action="store_true", help="generate object file and" +
                        " executable (requires NASM and LD linker)")
    args = parser.parse_args()

    with open(args.inputfile, "r") as ifile:
        data = ifile.read()
    
    prog = "".join(c for c in data if c in ["+", "-", ">", "<", "[", "]", ",", "."])

    asm = ["bits 64"]
    asm.append("global _start")

    # Section .bss, where program memory is located
    # (I assume it's zeroed by the program loader)
    asm.append("section .bss")
    asm.append("memory: resb {}".format(args.memsize))

    # Beginning of section .text
    asm.append("section .text")
    asm.append("_start:")
    # Initialize registers
    asm.append("mov rdx, 1")   # read/write one character

    reg = "rsi"
    asm.append("mov {}, memory".format(reg))

    b = 0
    lstack = deque()

    for o in range(len(prog)):
        operation = prog[o]

        # Incrementation operations
        if operation in ["+", "-", ">", "<"] and (o == 0 or operation != prog[o-1]):
            r = 0
            while prog[o+r] == operation:
                r += 1
            if r == 1:
                if operation == "+":
                    asm.append("inc byte [{}]".format(reg))
                elif operation == "-":
                    asm.append("dec byte [{}]".format(reg))
                elif operation == ">":
                    asm.append("inc {}".format(reg))
                elif operation == "<":
                    asm.append("dec {}".format(reg))
            else:
                if operation == "+":
                    asm.append("add byte [{}], {}".format(reg, r))
                elif operation == "-":
                    asm.append("sub byte [{}], {}".format(reg, r))
                elif operation == ">":
                    asm.append("add {}, {}".format(reg, r))
                elif operation == "<":
                    asm.append("sub {}, {}".format(reg, r))
        
        # Control flow operations
        elif operation == "[":
            lstack.append(b)

            asm.append("cmp byte [{}], 0".format(reg))
            asm.append("je end_{}".format(b))
            asm.append("start_{}:".format(b))

            b += 1
        
        elif operation == "]":
            n = lstack.pop()

            asm.append("cmp byte [{}], 0".format(reg))
            asm.append("jne start_{}".format(n))
            asm.append("end_{}:".format(n))
        
        # I/O operations
        elif operation == ".":
            asm.append("mov rax, 1")        # Write syscall
            asm.append("mov rdi, 1")        # Write to stdout
            asm.append("syscall")
        elif operation == ",":
            asm.append("xor rax, rax")      # Read syscall
            asm.append("xor rdi, rdi")      # Read from stdin
            asm.append("syscall")
    
    asm.append("exit:")
    asm.append("mov rax, 60")
    asm.append("xor rdi, rdi")
    asm.append("syscall")

    if args.inputfile.endswith(".b"):
        basename = args.inputfile[:-2]
    else:
        basename = args.proginputfileram

    asmfile = basename + ".asm"

    # Output generated assembly
    with open(asmfile, "w") as f:
        print("\n".join(asm), file=f)

    # Build if flag is set
    if args.build:
        if osname != "posix":
            print("bfc: Warning: Building only works on POSIX systems")
        else:
            objfile = basename + ".o"
            run(["nasm", "-felf64", "-o" + objfile, asmfile], check=True)
            run(["ld", "-o" + basename, objfile], check=True)
    
    print("DONE")
