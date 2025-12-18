# Crowbar

## Overview

Crowbar (named after [Crowbar](https://en.wikipedia.org/wiki/Crowbar_(American_band)))is a stack-based interpreted language inspired by FORTH and Python. Originally, it was meant to be for ASCII roguelike games (the `clearscr` keyword is a remnant of that), but over time it has become a sort of general purpose/toy language. <br>

***Keep in mind that it is still a work in progress, and that I have much to add and much to fix!***

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

## Speed

Running this in the REPL:
```
!time 10000 for i
    pass
    end 
!time
```

Gives this output:
`Execution time: 0.018350 seconds`

## TODO

- Improve examples/
- Finish `help` library
- Add transpiler
- Syntax highlighter
- Change syntax for file keywords
- Create editor
- Add bytecode support
- Fix import