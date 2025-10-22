from sys import exit

error_quit = False
line_number = 1
old_line = 1
running = ""

def error_quit_true():
    global error_quit
    error_quit = True

def error_quit_false():
    global error_quit
    error_quit = False

def reset_line():
    global line_number
    line_number = 1

def split_line():
    global line_number, old_line
    old_line = line_number
    reset_line()

def return_line():
    global line_number, old_line
    line_number = old_line

def increment_line():
    global line_number
    line_number += 1

def set_errtoken(et):
    global errtoken
    errtoken = et

def set_running(set_to):
    global running
    running = set_to

def error(error_type, error_text):
    global line_number
    text = f"\033[0;31m\033[1m{error_type}: \033[0m{error_text} (on line {str(line_number)}"

    if errtoken:
        text += f" / from token '\033[0;35m{errtoken}\033[0m'"

    if len(running) > 0:
        text += f" / whilst in \033[0;35m{running}\033[0m"

    text += ")"

    print(text)

    if error_quit:
        exit(0)