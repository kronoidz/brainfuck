#!/usr/bin/env python3

# Simple brainfuck interpreter by kronoidz
# -h for help

from sys import stdin, stdout, stderr
from argparse import ArgumentParser

def dumpMem(f, mem=None):
    if mem:
        print("Memory: {}".format([int(i) for i in mem]), file=f)

def throw(instruction, iprog, message, mem=None):
    print("\n\nException on instruction {} at {}: {}".format(instruction, iprog, message),
        file=stderr)
    dumpMem(stderr, mem)
    exit(1)

if __name__ == "__main__":

    parser = ArgumentParser(description="Simple Brainfuck interpreter")
    parser.add_argument("program", type=str, help="program file")
    parser.add_argument("memsize", type=int, help="memory size in bytes", default=512, nargs="?")
    parser.add_argument("-d", "--dump", action="store_true", help="dump memory on a file after every access")
    args = parser.parse_args()    
    
    # Create program memory
    mem = bytearray(args.memsize)
    imem = 0

    if args.dump:
        fdump = open("dump.txt", "w")
        dumpMem(fdump, mem)

    with open(args.program, "r") as ifile:
        data = ifile.read()

    prog = "".join(c for c in data if c in ["+", "-", ">", "<", "[", "]", ",", "."])
    iprog = 0

    while iprog < len(prog):

        if prog[iprog] == "+":
            if imem not in range(args.memsize) or mem[imem] == 255:
                throw(prog[iprog], iprog, "Memory error", mem)
            mem[imem] += 1

            if args.dump:
                dumpMem(fdump, mem)

        elif prog[iprog] == "-":
            if imem not in range(args.memsize) or mem[imem] == 0:
                throw(prog[iprog], iprog, "Memory error", mem)
            mem[imem] -= 1
            
            if args.dump:
                dumpMem(fdump, mem)

        elif prog[iprog] == ">":
            imem += 1

        elif prog[iprog] == "<":
            imem -= 1

        elif prog[iprog] == ".":
            stdout.buffer.write(bytes([mem[imem]]))
            stdout.flush()

        elif prog[iprog] == ",":
            b = stdin.buffer.read(1)
            if b:
                mem[imem] = ord(b)
            
                if args.dump:
                    dumpMem(fdump, mem)

        elif prog[iprog] == "[" and mem[imem] == 0:
            jprog = iprog
            nest = 0
            while True:
                jprog += 1
                if jprog >= len(prog):
                    throw(prog[iprog], iprog, "Unbalanced []")
                if prog[jprog] == "[":
                    nest += 1
                elif prog[jprog] == "]":
                    if nest > 0:
                        nest -= 1
                    else:
                        iprog = jprog
                        break

        elif prog[iprog] == "]" and mem[imem] != 0:
            jprog = iprog
            nest = 0
            while True:
                jprog -= 1
                if jprog < 0:
                    throw(prog[iprog], iprog, "Unbalanced []")
                if prog[jprog] == "]":
                    nest += 1
                elif prog[jprog] == "[":
                    if nest > 0:
                        nest -= 1
                    else:
                        iprog = jprog
                        break
        
        iprog += 1
    
    if args.dump:
        fdump.close()
