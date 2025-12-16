from src.stack import *
from src.error import *
from src.parse import *

from time import sleep, perf_counter

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
    global variables, constants
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