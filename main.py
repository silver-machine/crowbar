from lex import *
from parse import *
from error import *

from sys import argv
import os
import readline
import shutil

def repl():
    error_quit_false()
    reset_line()
    set_running("<REPL>")

    print("Crowbar REPL")

    buffer = ""
    depth = 0

    while True:
        reset_line()

        prompt = "  " if depth > 0 else "\033[0;35m>\033[0m "
        try:
            inp = input(prompt)
            buffer += inp + "\n"
        except EOFError:
            error_quit_true()
            error("\nEOF Error", "End of file read")

        try:
            tokens = lex(buffer)
        except Exception as e:
            print(f"Lexing error: {e}")
            continue

        depth = 0
        for t, v in tokens:
            if t == "ID" and v in ("fn", "if", "while", "for", "try"):
                depth += 1
            elif t == "PAREN" and v in ("[", "{"):
                depth += 1
            elif t == "ID" and v == "end":
                depth -= 1
            elif t == "PAREN" and v in ("]", "}"):
                depth -= 1

        if depth <= 0:
            try:
                parse(tokens)
            except Exception as e:
                print(f"Runtime error: {e}")
            buffer = ""
            depth = 0

def run(f):
    # runs given file
    global currentdir

    error_quit_true()
    reset_line()
    set_running("<file>")

    if not os.path.exists(f):
        error("File Error", f"File '{f}' not found")
        return

    set_current_dir(os.path.dirname(os.path.abspath(argv[2])))
    with open(argv[2]) as f:
        parse(lex(f.read()))


def add(src, name):
    # adds library to ~/crowbar/lib/<name>/ and registers it in env
    library_directory = os.path.join("lib", name)

    if not os.path.exists(src):
        print(f"Folder '{src}' not found!")
        return

    os.makedirs("lib", exist_ok=True)

    if os.path.isdir(src):
        shutil.copytree(src, library_directory, dirs_exist_ok=True)
    else:
        os.makedirs(library_directory, exist_ok=True)
        shutil.copy2(src, os.path.join(library_directory, "main.cb"))

    if not os.path.exists("env"):
        open("env", "w").close()

    with open("env", "r") as env_entries:
        lines = [line.strip() for line in env_entries]

    entry = f"{name} -- ~/crowbar/lib/{name}/main.cb"

    if entry not in lines:
        with open("env", "a") as f:
            f.write(entry + "\n")
        print(f"{name} added and registered")
    else:
       print(f"{name} already exists!")


def new(name):
    # creates new crowbar project folder called <name>
    os.makedirs(name, exist_ok=True)

    mainfile = os.path.join(name, "main.cb")

    if not os.path.exists(mainfile):
        with open(mainfile, "x") as f:
            f.write(";; " + name + "\n")
        print(f"Created {mainfile}")
    else:
        print(f"{mainfile} already exists!")

def libs():
    # lists libraries in lib
    envpath = os.path.expanduser("~/crowbar/env")
    if os.path.exists(envpath):
        with open(envpath) as f:
            for line in f.readlines():
                print(line.rstrip())

if __name__ == "__main__":
    if len(argv) < 2:
        set_current_dir(os.path.dirname(os.path.abspath(__file__)))
        repl()
    cmd = argv[1]
    if cmd == "run" and len(argv) > 2:
        set_current_dir(os.path.dirname(os.path.abspath(argv[2])))
        run(argv[2])
    elif cmd == "add" and len(argv) > 3:
        add(argv[2], argv[3])
    elif cmd == "new" and len(argv) > 2:
        new(argv[2])
    elif cmd == "list":
        libs()
    else:
        print("""  crowbar                     - opens crowbar REPL
  crowbar run <file>          - runs <file>
  crowbar add <source> <name> - adds <source> to libraries with name <name>
  crowbar list                - lists registered libraries""")