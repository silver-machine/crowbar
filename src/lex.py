from src.error import *

class Token:
    def __init__(self, token_type, value, line):
        self.type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line})"

def lex(source: str):
    tokens = []
    i = 0
    line = 1
    identchars = "+-*/=<>!.,_&?$@%"

    while i < len(source):
        char = source[i]

        if char == "\n":
            tokens.append(Token("NEWLINE", "\n", line))
            line += 1
            i += 1
            continue

        elif char.isspace():
            i += 1
            continue

        elif char.isdigit() or (char == "-" and i + 1 < len(source) and source[i + 1].isdigit()):
            num = char
            i += 1
            while i < len(source) and (source[i].isdigit() or source[i] == "."):
                num += source[i]
                i += 1

            if i < len(source) and source[i].lower() in "hkmbt":
                suffix = source[i].lower()
                i += 1
                factor = {"h": 100, "k": 1000, "m": 1_000_000, "b": 1_000_000_000, "t": 1_000_000_000_000}[suffix]
                num = str(int(float(num) * factor))

            tokens.append(Token("NUMBER", num, line))
            continue

        elif char.isalpha() or char == "_" or char in identchars:
            ident = char
            i += 1
            while i < len(source) and (source[i].isalnum() or source[i] in identchars):
                ident += source[i]
                i += 1
            tokens.append(Token("ID", ident, line))
            continue

        elif char == '"' or char == "'":
            quote = char
            i += 1
            string_val = ""
            start_line = line

            while i < len(source):
                c = source[i]

                if c == quote:
                    i += 1
                    tokens.append(Token("STRING", string_val, start_line))
                    break

                elif c == "\n":
                    line += 1
                    string_val += c

                elif c == "\\":
                    i += 1
                    if i >= len(source):
                        error("Syntax Error", f"Unterminated escape sequence on line {line}")

                    next_char = source[i]
                    
                    if next_char == "e" and i + 1 < len(source) and source[i + 1] == "[":
                        i += 2  # skip 'e['
                        esc_seq = "\033["

                        while i < len(source) and source[i] != "]":
                            esc_seq += source[i]
                            i += 1

                        if i >= len(source) or source[i] != "]":
                            error("Syntax Error", f"Unterminated escape sequence on line {line}")
                        
                        string_val += esc_seq
                        i += 1
                        continue

                    escapes = {"n": "\n", "t": "\t", '"': '"', "'": "'", "\\": "\\"}
                    string_val += escapes.get(next_char, next_char)

                else:
                    string_val += c

                i += 1

            else:
                error("Syntax Error", f"Unterminated string starting on line {start_line}")

        elif char in "[](){}":
            tokens.append(Token("PAREN", char, line))
            i += 1
            continue

        elif char == ";" and i + 1 < len(source) and source[i + 1] == ";":
            while i < len(source) and source[i] != "\n":
                i += 1
            continue

        elif char == ":" and i + 1 < len(source) and source[i + 1] == ":":
            i += 2
            while i < len(source) - 1:
                if source[i] == "\n":
                    line += 1
                elif source[i] == ":" and source[i + 1] == ":":
                    i += 2
                    break
                i += 1
            else:
                error("Syntax Error", f"Unterminated multiline comment on line {line}")
            continue

        else:
            error("Syntax Error", f"Unexpected character '{char}' on line {line}")
            i += 1
        
    return tokens