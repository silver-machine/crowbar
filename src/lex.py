from src.error import *

def lex(source: str):
    tokens = []
    i = 0
    identchars = "+-*/=<>!.,_&?"

    while i < len(source):
        char = source[i]

        if char == "\n":
            tokens.append(("NEWLINE", "\\n"))
            increment_line()
            i +=1
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
            tokens.append(("NUMBER", num))
            continue

        elif char.isalpha() or char == "_" or char in identchars:
            ident = char
            i += 1
            while i < len(source) and (source[i].isalnum() or source[i] in identchars):
                ident += source[i]
                i += 1
            tokens.append(("ID", ident))
            continue

        elif char == '"' or char == "'":
            quote = char
            i += 1
            string_val = ""

            while i < len(source):
                c = source[i]

                if c == quote:
                    i += 1
                    tokens.append(("STRING", string_val))
                    break

                elif c == "\\":
                    i += 1
                    if i >= len(source):
                        error("Syntax Error", "Unterminated escape sequence")

                    next_char = source[i]
                    
                    if next_char == "e" and i + 1 < len(source) and source[i + 1] == "[":
                        i += 2  # skip 'e['
                        esc_seq = "\033["

                        while i < len(source) and source[i] != "]":
                            esc_seq += source[i]
                            i += 1

                        if i >= len(source) or source[i] != "]":
                            error("Syntax Error", "Unterminated escape sequence")
                        
                        string_val += esc_seq
                        i += 1
                        continue

                    escapes = {"n":"\n", "t":"\t", '"':'"', "'":"'", "\\":"\\"}
                    string_val += escapes.get(next_char, next_char)

                else:
                    string_val += c

                i += 1

            else:
                error("Syntax Error", "Unterminated string")

        elif char in "[](){}":
            tokens.append(("PAREN", char))
            i += 1
            continue

        elif char == ";" and i + 1 < len(source) and source[i + 1] == ";":
            while i < len(source) and source[i] != "\n":
                i += 1
            continue

        elif char == ":" and i + 1 < len(source) and source[i + 1] == ":":
            i += 2
            while i < len(source) - 1:
                if source[i] == ":" and source[i + 1] == ":":
                    i += 2
                    break
                i += 1
            else:
                error("Syntax Error", "Unterminated multiline comment")
            continue

        else:
            error("Syntax Error", f"Unexpected character: {char}")
            i += 1
        
    return tokens