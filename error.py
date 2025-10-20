from sys import exit

error_quit = False
line_number = 1
running = ""

def error_quit_true():
    global error_quit
    error_quit = True

def error_quit_false():
    global error_quit
    error_quit = False

def reset_line():
    global line_number
    line_number = 0

def increment_line():
    global line_number
    line_number += 1

def set_running(set_to):
    global running
    running = set_to

def error(error_type, error_text):
    global line_number
    text = f"\033[0;31m\033[1m{error_type}: \033[0m{error_text} (line {str(line_number)}"

    if len(running) > 0:
        text += f" / whilst in \033[0;35m{running}\033[0m"

    text += ")"

    print(text)

    if error_quit:
        exit(0)