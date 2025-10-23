from src.lex import lex
from src.stack import *
from src.error import *

from time import sleep, perf_counter
import os, random, platform, sys

constants = {"ARGS": sys.argv[2:]}
variables = {}
globalvars = {}
functions = {}
stack = Stack()
trace = False
currentdir = ""

time_trace = True
end_time = 0
start_time = 0

def trace_time():
    global time_trace, end_time, start_time
    time_trace = not time_trace
    if time_trace:
        end_time = perf_counter()
        elapsed = end_time - start_time
        print(f"Execution time: {elapsed:.6f} seconds")
    else:
        start_time = perf_counter()

def set_current_dir(setto):
    global currentdir
    currentdir = setto

def extract_block(tokens, start_index, open_tokens=("fn","for","while","if"), close_token="end"):
    body = []
    depth = 1
    i = start_index
    while i < len(tokens) and depth > 0:
        t, v = tokens[i]
        if t == "ID" and v in open_tokens:
            depth += 1
            body.append(tokens[i])
        elif t == "ID" and v == close_token:
            depth -= 1
            if depth > 0:
                body.append(tokens[i])
        else:
            body.append(tokens[i])
        i += 1
    if depth != 0:
        error("Syntax Error", f"Missing '{close_token}'")
    return body, i

def parse_array(tokens, start_index, open, close):
    arr = []
    i = start_index
    while i < len(tokens):
        t, v = tokens[i]
        if t == "PAREN" and v == close:
            return arr, i
        elif t == "PAREN" and v == open:
            sub_arr, new_i = parse_array(tokens, i + 1, open, close)
            arr.append(sub_arr)
            i = new_i
        else:
            # push simple literals into a temp stack
            if t == "NUMBER":
                arr.append(float(v) if "." in v else int(v))
            elif t == "STRING":
                 arr.append(v)
            elif t == "ID":
                if v in variables:
                    arr.append(variables[v])
                elif v in constants:
                     arr.append(constants[v])
                else:
                    arr.append(v)
        i += 1
    error("Syntax Error", "Unterminated array literal")

def format_data(data):
    t = ""
    if isinstance(data, tuple) and data[0] == "BLOCK":
        t += "{"
        for token in data[1]:
            t += token[1] + " "
        t += "}"

    elif isinstance(data, list):
        t += "["
        d = 0
        for item in data:
            item = str(item)
            if not d == len(data) - 1:
                t += item + " "
            else:
                t += item
            d += 1
        t += "]"
    else:
        t = data
    
    return t

stack = Stack()

def parse(tokens):
    global stack, variables, globalvars, functions, constants, currentdir, trace, line_number, time_trace
    i = 0
    while i < len(tokens):
        ttype, value = tokens[i]
        set_errtoken(value)

        if trace and ttype != "NEWLINE":
            print(f"\033[0;35m\033[1m{ttype}\033[0m: \033[0;35m\033[1m{value}\033[0m")

        if ttype == "NUMBER":
            stack.push(float(value) if "." in value else int(value))

        elif ttype == "STRING":
            stack.push(value)

        elif ttype == "PAREN" and value == "[":
            arr, j = parse_array(tokens, i + 1, "[", "]")
            stack.push(arr)
            i = j
            continue

        if ttype == "PAREN" and value == "{":
            body = []
            depth = 1
            j = i + 1
            while j < len(tokens) and depth > 0:
                t, v = tokens[j]
                if t == "PAREN" and v == "{":
                    depth += 1
                    body.append(tokens[j])
                elif t == "PAREN" and v == "}":
                    depth -= 1
                    if depth > 0:
                        body.append(tokens[j])
                else:
                    body.append(tokens[j])
                j += 1
            if depth != 0:
                error("Syntax Error", "Unterminated block literal")
            stack.push(("BLOCK", body))
            i = j
            continue
        
        elif ttype == "ID":

            # Run functions
            if value in functions:
                try: 
                    prev = running
                    prev_vars = variables.copy()
                    variables = {}
                    fn = functions[value]
                    if callable(fn):
                        set_running(value)
                        fn()
                    variables = prev_vars
                    set_running(prev)
                except RecursionError: error("Function Error", "Maximum recursion exceeded")

            # Push variable to stack
            elif value in variables:
                stack.push(variables[value])
            
            elif value in globalvars:
                stack.push(globalvars[value])

            # Push constant to stack
            elif value in constants:
                stack.push(constants[value])

            elif value == "store":
                # x store y / stores data x to variable y
                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected variable name after '{value}' keyword")

                name_type, name_val = tokens[i + 1]
                
                if name_type != "ID":
                    error("Type Error", "Variable name must be identifier")
                elif name_val in constants:
                    error("Definition Error", f"'{name_val}' already defined (as constant)")
                elif name_val in functions:
                    error("Definition Error", f"'{name_val}' already defined (as function)")
                elif name_val in globalvars:
                    error("Definition Error", f"'{name_val}' already defined (as global variable)")
                else:              
                    val = stack.pop()
                    variables[name_val] = val
                    i += 1
            
            elif value == "global":
                # x store y / stores data x to variable y
                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected variable name after '{value}' keyword")

                name_type, name_val = tokens[i + 1]
                
                if name_type != "ID":
                    error("Type Error", "Variable name must be identifier")
                elif name_val in constants:
                    error("Definition Error", f"'{name_val}' already defined (as constant)")
                elif name_val in functions:
                    error("Definition Error", f"'{name_val}' already defined (as function)")
                elif name_val in variables:
                    error("Definition Error", f"'{name_val}' already defined (as local variable)")
                else:              
                    val = stack.pop()
                    globalvars[name_val] = val
                    i += 1

            elif value == "const":
                # x const y / stores data x to const y if not previously defined
                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected variable name after '{value}' keyword")

                name_type, name_val = tokens[i + 1]
                
                if name_type != "ID":
                    error("Type Error", "Constant name must be identifier")

                val = stack.pop()
                if name_val in constants:
                    error("Definition Error", f"Constant '{name_val}' already defined")
                elif name_val in variables:
                    error("Definition Error", f"'{name_val}' already defined (as variable)")   
                elif name_val in functions:
                    error("Definition Error", f"'{name_val}' already defined (as function)")
                elif name_val in globalvars:
                    error("Definition Error", f"'{name_val}' already defined (as global variable)")     
                else:
                    constants[name_val] = val
                i += 1

            elif value == "ask":
                # x (str) / gets input with prompt x, pushes result to stack
                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                prompt = stack.pop()
                if not isinstance(prompt, str):
                    error("Type Error", f"{value} expects 1 string")
                else:
                    stack.push(input(str(prompt)))
                
            elif value == "&&":
                # x (str) y (str) && / concatenates x and y, pushes result to stack
                
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if not type(b) == type(a) == str:
                    error("Type Error", f"'{value}' keyword expects two strings")
                else:
                    stack.push(a + b)

            elif value == "+":
                # x (int) y (int) + / adds x and y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    error("Type Error", f"'{value}' keyword expects two integers or floats")
                else:
                    stack.push(a + b)

            elif value == "-":
                # x (int) y (int) - / substracts y from x, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    stack.push(a - b)
                else:
                    error("Type Error", f"{value} expects numbers")


            elif value == "*":
                # x (int) y (int) * / multiplies x by y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    stack.push(a * b)
                else:
                    error("Type Error", f"{value} expects numbers")

            elif value == "/":
                # x (int) y (int) / / divides x by y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    error("Type Error", f"{value} expects 2 integers")
                if not (a == b > 0):
                    error("Zero Division Error", "Division by zero")
                else:
                    stack.push(a / b)

            elif value == "=":
                # x y = / checks if x is equal to y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                stack.push(1 if a == b else 0)
                
            elif value == "<":
                # x y < / checks if x is less than to y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    stack.push(1 if a < b else 0)
                else:
                    error("Type Error", f"{value} expects 2 integers")

            elif value == ">":
                # x y > / checks if x is greater than y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()

                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    stack.push(1 if a > b else 0)
                else:
                    error("Type Error", f"{value} expects 2 integers")
            
            elif value == "!=":
                # x y != / checks if x is not equal to y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                
                b = stack.pop()
                a = stack.pop()

                if type(a) == type(b):
                    stack.push(1 if a != b else 0)
                else:
                    error("Type Error", f"{value} expects 2 integers")

            elif value == "<=":
                # x y <= / checks if x is less than or equal to y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    stack.push(1 if a <= b else 0)
                else:
                    error("Type Error", f"{value} expects 2 integers")

            elif value == ">=":
                # x y >= / checks if x is greater than or equal to y, pushes result to stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    stack.push(1 if a >= b else 0)
                else:
                    error("Type Error", f"{value} expects 2 integers")

            elif value == "in":
                # x y (arr) / checks if x is found in array y, pushes result to stack
                
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if isinstance(b, list):
                    stack.push(1 if a in b else 0)
                else:
                    error("Type Error", f"'{value}' expects 1 any and 1 array")

            elif value == ".":
                # x . / prints x with newline

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                
                print(format_data(stack.pop()))

            elif value == ",":
                # x , / prints x without newline

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                s = stack.pop()
                t = ""

                if isinstance(s, tuple) and s[0] == "BLOCK":
                    for token in s[1]:
                        t += token[1] + " "
                
                elif isinstance(s, list):
                    t += "["
                    d = 0
                    for item in s:
                        item = str(item)
                        if not d == len(s) - 1:
                            t += item + " "
                        else:
                            t += item
                        d += 1
                    t += "]"
                else:
                    t = s
                
                print(t, end="")

            elif value == "emit":
                # x (int) emit / prints ascii value of x

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                s = stack.pop()
                if isinstance(s, int):
                    print(chr(s))
                else:
                    error("Type Error", f"{value} expects 1 integer")
            
            elif value == "ascii":
                # x (str) ascii / pushes ascii value of x to stack

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                s = stack.pop()
                if isinstance(s, str) and len(s) == 1:
                    stack.push(ord(s))
                else:
                    error("Type Error", f"{value} expects 1 character string")

            elif value == "quit":
                exit()

            elif value == "dup":
                # x dup / duplicates x on the stack

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                dup = stack.pop()
                stack.push(dup)
                stack.push(dup)
            
            elif value == "drop":
                # drop / pops from stack

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                stack.pop()

            elif value == "swap":
                # x y swap / swaps x and y on the stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                stack.push(b)
                stack.push(a)
            
            elif value == "over":
                # x y over / push x y x to the stack

                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                stack.push(a)
                stack.push(b)
                stack.push(a)

            elif value == "clearscr":
                if platform.system() != "Windows": os.system("clear")
                else: os.system("cls")

            elif value == "use":
                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected library name after {value}")
                    i += 1
                    continue

                name_type, name_val = tokens[i + 1]
                if name_type == "STRING":
                    fname = name_val
                elif name_type == "ID":
                    fname = name_val
                else:
                    error("Syntax Error", "Library name must be string or identifier")

                handle = None
                if getattr(sys, 'frozen', False):
                    # Running as PyInstaller bundle
                    cbarpath = sys._MEIPASS  # Temporary folder PyInstaller extracts to
                else:
                    cbarpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                envpath = os.path.join(cbarpath, "env")

                if os.path.exists(envpath):
                    with open(envpath) as f:
                        for line in f:
                            if "--" not in line:
                                continue
                            name, path = line.strip().split(" -- ", 1)
                            if name == fname:
                                handle = os.path.abspath(os.path.join(cbarpath, path))
                                break

                if handle is None and currentdir:
                    sibling_path = os.path.join(currentdir, fname)
                    if os.path.isfile(sibling_path):
                        handle = os.path.expanduser(sibling_path)

                if handle is None:
                    lib_path = os.path.join(cbarpath, "lib", fname, "main.cb")
                    if os.path.isfile(lib_path):
                        handle = os.path.expanduser(lib_path)

                if handle is None:
                    error("File Error", f"Library '{fname}' not found (searched in env, sibling folder, and lib folder)")

                prevdir = currentdir
                currentdir = os.path.dirname(os.path.abspath(handle))
                with open(handle, "r") as f:
                    content = f.read()
                
                split_line()
                set_running(fname)
                prev_vars = variables.copy()
                parse(lex(content))
                variables = prev_vars
                return_line()
                currentdir = prevdir

                i += 1

            elif value == "create":
                # create x (id/str) / creates new file with name x

                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected file name after {value}")
                    i += 2
                    continue

                name_type, name_val = tokens[i + 1]
                if name_type == "STRING":
                    fname = name_val
                elif name_type == "ID":
                    if name_val in variables:
                        fname = variables[name_val]
                    elif name_val in constants:
                        fname = constants[name_val]
                    elif name_val in globalvars:
                        fname = globalvars[name_val]
                else:
                    error("Syntax Error", "File name must be variable, constant, or stringß")

                try:
                    open(fname, "x").close()
                except FileExistsError:
                    error("File Error", "File already exists")

                i += 1
            
            elif value == "write":
                # x write y (id/str) / writes x to file y

                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected file name after {value}")
                    i += 1
                    continue

                name_type, name_val = tokens[i + 1]
                if name_type == "STRING":
                    fname = name_val
                elif name_type == "ID":
                    if name_val in variables:
                        fname = variables[name_val]
                    elif name_val in constants:
                        fname = constants[name_val]
                    elif name_val in globalvars:
                        fname = globalvars[name_val]
                    else:
                        error("File Error", f"Unknown identifier '{name_val}'")
                        i += 1
                        continue
                else:
                    error("Syntax Error", "File name must be variable, constant, or string")
                    i += 1
                    continue

                if len(stack.stack) < 1:
                    error("Stack Error", f"Stack underflow")
                    i += 1
                    continue

                try:
                    with open(fname, "w") as f:
                        f.write(str(stack.pop()))
                except FileNotFoundError:
                    error("File Error", f"File '{fname}' not found")

                i += 1

            elif value == "append":
                # x append y (id/str) / appends x to file y

                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected file name after {value}")
                    i += 1
                    continue

                name_type, name_val = tokens[i + 1]
                if name_type == "STRING":
                    fname = name_val
                elif name_type == "ID":
                    if name_val in variables:
                        fname = variables[name_val]
                    elif name_val in constants:
                        fname = constants[name_val]
                    elif name_val in globalvars:
                        fname = globalvars[name_val]
                    else:
                        error("File Error", f"Unknown identifier '{name_val}'")
                        i += 1
                        continue
                else:
                    error("Syntax Error", "File name must be variable, constant, or string")
                    i += 1
                    continue

                if len(stack.stack) < 1:
                    error("Stack Error", f"Stack underflow")
                    i += 1
                    continue

                try:
                    with open(fname, "a") as f:
                        f.write(str(stack.pop()))
                except FileNotFoundError:
                    error("File Error", f"File '{fname}' not found")

                i += 1


            elif value == "getline":
                # x (int) getline y (id/str) / gets line x from file y

                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected file name after {value}")
                    i += 1
                    continue

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                name_type, name_val = tokens[i + 1]
                if name_type == "STRING":
                    fname = name_val
                elif name_type == "ID":
                    if name_val in variables:
                        fname = variables[name_val]
                    elif name_val in constants:
                        fname = constants[name_val]
                    elif name_val in globalvars:
                        fname = globalvars[name_val]
                    else:
                        error("File Error", f"Unknown identifier '{name_val}'")
                        i += 1
                        continue
                else:
                    error("Syntax Error", "File name must be variable, constant, or string")
                    i += 1
                    continue

                idx = stack.pop()
                if isinstance(idx, int):
                    try:
                        with open(fname, "r") as f:
                            lines = f.readlines()
                        if 0 <= idx < len(lines):
                            stack.push(lines[idx].rstrip("\n"))
                        else:
                            error("Index Error", "Line index out of range")
                    except FileNotFoundError:
                        error("File Error", f"File '{fname}' not found")
                else:
                    error("Type Error", f"'{value}' expects 1 integer")

                i += 1

            elif value == "getlines":
                # getlines x (id/str) / get all lines from file x

                if i + 1 >= len(tokens):
                    error("Syntax Error", "Expected file name after 'getlines'")
                    i += 1
                    continue

                name_type, name_val = tokens[i + 1]
                if name_type == "STRING":
                    fname = name_val
                elif name_type == "ID":
                    if name_val in variables:
                        fname = variables[name_val]
                    elif name_val in constants:
                        fname = constants[name_val]
                    elif name_val in globalvars:
                        fname = globalvars[name_val]
                    else:
                        error("File Error", f"Unknown identifier '{name_val}'")
                        i += 1
                        continue
                else:
                    error("Syntax Error", "File name must be variable, constant, or string")
                    i += 1
                    continue

                try:
                    with open(fname, "r") as f:
                        stack.push([line.rstrip("\n") for line in f.readlines()])
                except FileNotFoundError:
                    error("File Error", f"File '{fname}' not found")

                i += 1


            elif value == "fn":
                # fn x ... end / define function with name x

                if i + 1 >= len(tokens):
                    error("Syntax Error", "Expected word name after 'fn'")
                name_type, name_val = tokens[i + 1]
                if name_type != "ID":
                    error("Syntax Error", "Word name must be identifier")
                
                body, j = extract_block(tokens, i + 2)
                functions[name_val] = lambda body=body: parse(body)
                i = j
                continue

            elif value == "if":
                # if x do ... else ... end / if else on x

                tokens_block, j = extract_block(tokens, i + 1, open_tokens=("if","fn","while","for"), close_token="end")

                condition_tokens = []
                true_tokens = []
                false_tokens = []

                depth = 0
                mode = "condition"
                for t, v in tokens_block:
                    if t == "ID" and v in ("if", "while", "for", "fn"):
                        depth += 1
                    elif t == "ID" and v == "end":
                        depth -= 1
                    elif t == "ID" and v == "do" and depth == 0 and mode == "condition":
                        mode = "true"
                        continue
                    elif t == "ID" and v == "else" and depth == 0 and mode == "true":
                        mode = "false"
                        continue

                    if mode == "condition":
                        condition_tokens.append((t, v))
                    elif mode == "true":
                        true_tokens.append((t, v))
                    else:
                        false_tokens.append((t, v))

                if not condition_tokens:
                    error("Syntax Error", "'if' missing condition")
                if not true_tokens:
                    error("Syntax Error", "'if' missing body after 'do'")

                parse(condition_tokens)
                condition = stack.pop()

                if condition:
                    parse(true_tokens)
                else:
                    parse(false_tokens)

                i = j
                continue


            elif value == "for":
                # x (int) for y (id) ... end

                if i + 1 >= len(tokens):
                    error("Syntax Error", "Expected increment variable after for")
                    i += 1
                    continue

                name_type, name_val = tokens[i + 1]
                if name_type != "ID":
                    error("Syntax Error", "Icrement variable name must be an identifier")
                    i += 2
                    continue

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 2
                    continue

                count = stack.pop()
                if not isinstance(count, int):
                    error("Type Error", f"{value} expects an integer count")
                    i += 2
                    continue

                body, j = extract_block(tokens, i + 2)

                old_val = variables.get(name_val, None)
                try:
                    for k in range(count):
                        variables[name_val] = k
                        parse(body)
                finally:
                    if old_val is not None:
                        variables[name_val] = old_val
                    else:
                        variables.pop(name_val, None)

                i = j
                continue


            elif value == "while":
                # while x do .. end
                tokens_block, j = extract_block(tokens, i + 1, open_tokens=("while","fn","if","for"), close_token="end")

                condition_tokens = []
                body_tokens = []

                depth = 0
                mode = "condition"
                for t, v in tokens_block:
                    if t == "ID" and v in ("if", "while", "for", "fn"):
                        depth += 1
                    elif t == "ID" and v == "end":
                        depth -= 1
                    elif t == "ID" and v == "do" and depth == 0 and mode == "condition":
                        mode = "body"
                        continue

                    if mode == "condition":
                        condition_tokens.append((t, v))
                    else:
                        body_tokens.append((t, v))

                if not condition_tokens:
                    error("Syntax Error", "'while' missing condition")
                if not body_tokens:
                    error("Syntax Error", "'while' missing body after 'do'")

                while True:
                    parse(condition_tokens)
                    condition = stack.pop()
                    if not condition:
                        break
                    parse(body_tokens)

                i = j
                continue

            elif value == "tostr":
                # x (int) tostr / turns x to str, pushes result to stack

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    s = stack.pop()

                    if isinstance(s, int):
                        stack.push(str(s))
                    else:
                        error("Type Error", f"{value} expects 1 non-string")

            elif value == "toint":
                # x (str) tostr / turns x to int, pushes result to stack

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    s = stack.pop()
                    if isinstance(s, str) and s.isnumeric():
                        stack.push(int(s))
                    else:
                        error("Type Error", f"{value} expects 1 numeric string")

            elif value == "depth":
                # depth / pushes length of stack to stack
                stack.push(len(stack.stack))

            elif value == "len":
                # x len / pushes length of x to stack
                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    stack.push(len(stack.pop()))

            elif value == "rand":
                # x (int) rand
                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    s = stack.pop()

                    if isinstance(s, int):
                        stack.push(random.randrange(0, s))
                    else:
                        error("Type Error", f"{value} expects 1 integer")

            elif value == "pass":
                pass

            elif value == "eval":
                # x (str/block) eval / evaluates x
                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    c = stack.pop()

                    if isinstance(c, tuple) and c[0] == "BLOCK":
                        parse(c[1])
                    elif isinstance(c, str):
                        parse(lex(c))
                    else:
                        error("Type Error", f"{value} expects 1 string/block")

            elif value == "set":
                # x (arr) y (int) z set / sets x[y] to z
                if len(stack.stack) < 3:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    val = stack.pop()
                    idx = stack.pop()
                    arr = stack.pop()

                    if isinstance(arr, list) and isinstance(idx, int):
                        arr[idx] = val
                        stack.push(arr)
                    else:
                        error("Type Error", f"{value} expects 1 array, 1 integer, and 1 anything")
            
            elif value == "get":
                # x (arr/str) y (int) get / pushes x[y]
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    idx = stack.pop()
                    arr = stack.pop()

                    if isinstance(arr, (list, str)) and isinstance(idx, int):
                        stack.push(arr[idx])
                    else:
                        error("Type Error", f"{value} expects 1 array/string and 1 integer")

            elif value == "add":
                # x (arr/str) y (str if str, any if arr) add / appends y to x
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    val = stack.pop()
                    arr = stack.pop()

                    if isinstance(arr, list):
                        arr.append(val)
                        stack.push(arr)
                    elif isinstance(arr, str) and isinstance(val, str):
                        arr+=val
                        stack.push(arr)
                    else:
                        error("Type Error", f"{value} expects 1 string/array and 1 string if string is passed, anything if array is passed")
            
            elif value == "cut":
                # x (arr/str) y cut / cuts index y from x
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    idx = stack.pop()
                    arr = stack.pop()

                    if isinstance(arr, (list, str)):
                        arr.remove(idx)
                        stack.push(arr)
                    else:
                        error("Type Error", f"{value} expects 1 array/string and 1 integer")
            
            elif value == "pops":
                # x (arr/str) y (idx) pops / pop y from x, pushes result to stack
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    idx = stack.pop()
                    arr = stack.pop()

                    if isinstance(arr, list) and isinstance(idx, int):
                        stack.push(arr.pop(idx))
                        stack.push(arr)
                    elif isinstance(arr, str) and isinstance(idx, int):
                        stack.push(arr[idx:idx+1])
                        stack.push(arr[:idx] + arr[idx+1:])
                    else:
                        error("Type Error", f"{value} expects 1 array/string and 1 integer")

            elif value == "pop":
                # x (arr/str) pop / pops from x, pushes x and popped to stack
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    arr = stack.pop()

                    if isinstance(arr, list):
                        stack.push(arr.pop())
                        stack.push(arr)
                    elif isinstance(arr, str):
                        stack.push(arr[-1])
                        stack.push(arr[0:-1])
                    else:
                        error("Type Error", f"{value} expects 1 array/string")
            
            elif value == "isalpha":
                # x (str) isalpha / checks if x is alphabetical, pushes result to stack
                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    x = stack.pop()

                    if isinstance(x, str):
                        stack.push(1 if x.isalpha() else 0)
                    else:
                        error("Type Error", f"{value} expects 1 string")

            elif value == "isnumeric":
                # x (str) isnumeric / checks if x is numeric, pushes result to string
                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    x = stack.pop()

                    if isinstance(x, str):
                        stack.push(1 if x.isnumeric() else 0)
                    else:
                        error("Type Error", f"{value} expects 1 string")

            elif value == "wait":
                # x (int) wait / waits x seconds
                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    x = stack.pop()

                    if isinstance(x, (int, float)):
                        sleep(x)
                    else:
                        error("Type Error", f"{value} expects 1 string")
            
            elif value == "split":
                # x (str) y (str) split / splits x by y, pushes result to stack
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    y = stack.pop()
                    x = stack.pop()

                    if type(x) == type(y) == str:
                        stack.push(y.split(x))
                    else:
                        error("Type Error", f"{value} expects 2 strings")
            
            elif value == "substr":
                # x (str) y (int) z (int) substr / takes character y to z from x, pushes result to stack
                if len(stack.stack) < 3:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    distance = stack.pop()
                    start = stack.pop()
                    string = stack.pop()

                    if isinstance(start, int) and isinstance(distance, int) and isinstance(string, str):
                        stack.push(string[start:start+distance])
                    else:
                        error("Type Error", f"{value} expects 2 integers and 1 string")
            
            elif value == "reset":
                functions = {}
                constants = {"ARGS": sys.argv[2:]}
                variables = {}
                globalvars = {}
            
            elif value == "release":
                # release x (id) / removes x from constants variables or functions
                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected variable/constant/function name after {value}")

                name_type, name_val = tokens[i + 1]
                if name_type != "ID":
                    error("Type Error", "Variable/constant/function name must be identifier")
                
                if name_val in variables:
                    del variables[name_val]
                elif name_val in constants:
                    del constants[name_val]
                elif name_val in functions:
                    del functions[name_val]
                elif name_val in globalvars:
                    del globalvars[name_val]
                else:
                    error("Syntax Error", f"Variable/constant/function {name_val} not found")
                i += 1

            elif value == "defined":
                # defined x (id) / checks if x has already been defined as a variable/constant/function, pushes result to stack
                if i + 1 >= len(tokens):
                    error("Syntax Error", f"Expected variable/constant/function name after {value}")
                    i += 2
                    continue
                else:
                    name_type, name_val = tokens[i + 1]
                    if name_type != "ID":
                        error("Type Error", "Variable/constant/function name must be identifier")
                    
                    if name_val in variables or name_val in constants or name_val in functions or name_val in globalvars:
                        stack.push(1)
                    else:
                        stack.push(0)
                i += 1

            elif value == "strip":
                # x (str) strip / strips trailing characters from x, pushes x to stack

                if len(stack.stack) < 1:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue
                else:
                    s = stack.pop()
                    if isinstance(s, str):
                        stack.push(s.rstrip())
                    else:
                        error("Type Error", f"{value} expects 1 string")

            elif value == "error":
                # x (str) y (str) error / raises error with error type x and error text y
                
                if len(stack.stack) < 2:
                    error("Stack Error", "Stack underflow")
                    i += 1
                    continue

                b = stack.pop()
                a = stack.pop()
                if not type(b) == type(a) == str:
                    error("Type Error", f"'{value}' keyword expects two strings")
                else:
                    error(a, b)
            
            elif value == "!stack":
                print(format_data(stack.stack))
            
            elif value == "!trace":
                trace = not trace
            
            elif value == "!time":
                trace_time()

            elif value in ("do", "end", "else"):
                error("Syntax Error", f"'{value}' found where not expected")

            else:
                error("Syntax Error", f"Unknown/undefined identifier '{value}'")

        i += 1