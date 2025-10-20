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

## Installing

Compile using `pyinstaller --onefile main.py`, then find the executable and rename it to crowbar. Then, add this folder to your path variable.