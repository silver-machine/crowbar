# Crowbar

## Overview

Crowbar is a stack-based interpreted language. Originally, it was meant for ascii roguelike programming, the `clearscr` keyword being a remnant of that, but eventually it became the sort of general purpose/toy language it is now.

## Example Code
```py
;; hello world x times

"How many times? " ask toint store x

x for i
  i tostr ": Hello, World" && .
end
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