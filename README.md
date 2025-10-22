# Crowbar

## Overview

Crowbar is a stack-based interpreted language. Originally, I meant for it to be for ASCII roguelike programming (the `clearscr` keyword is a remnant of that), but over time it has become a sort of general purpose/toy language.

## Example Code

```py
;; hello world x times

"How many times? " ask toint store x

x for i
  i tostr ": Hello, World" && .
end
```

## Usage

```
crowbar                     - opens crowbar REPL
crowbar run <file>          - runs <file>
crowbar add <source> <name> - adds <source> to libraries with name <name>
crowbar list                - lists registered libraries
```

## Learning Crowbar

`examples/` has a few simple examples that show how to use Crowbar. The [cheatsheet](cheatsheet.md) is useful for quick references. The `help` library (WIP) is can help with learning the base keywords.

## Installing

Compile using `pyinstaller --onefile main.py`, then find the executable and rename it to crowbar. Then, add this folder to your path variable.

## TODO

- Improve examples/
- Finish `help` library
- Add transpiler
- Syntax highlighter