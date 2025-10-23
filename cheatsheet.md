# Crowbar Cheatsheet

## Basics

* **Stack-based**: everything is pushed to the stack, operations pop and push as needed.
* **Comments**: `;;` for single line, `:: ... ::` for multi line.
* **Local Variables**: mutable, stored via `store`, only available in the the space that their defined.
* **Global Variables**: mutable, stored via `global`, available everywhere.
* **Constants**: immutable after definition via `const`.
* **Functions**: defined via `fn ... end`.

---

## Stack Operations

| Keyword | Usage      | Effect                 |
| ------- | ---------- | ---------------------- |
| `dup`   | `x dup`    | Duplicate top of stack |
| `drop`  | `drop`     | Pop top of stack       |
| `swap`  | `x y swap` | Swap top two           |
| `over`  | `x y over` | Push second item again |
| `depth` | `depth`    | Push length of stack   |

---

## Arithmetic

| Keyword | Usage    | Effect                   |
| ------- | -------- | ------------------------ |
| `+`     | `x y +`  | Add numbers              |
| `-`     | `x y -`  | Subtract                 |
| `*`     | `x y *`  | Multiply                 |
| `/`     | `x y /`  | Divide                   |
| `rand`  | `x rand` | Push random int `0 - x`  |

---

## Comparison / Logic

| Keyword | Usage    | Effect              |
| ------- | -------- | ------------------- |
| `=`     | `x y =`  | Equals → `1` or `0` |
| `!=`    | `x y !=` | Not equals          |
| `<`     | `x y <`  | Less than           |
| `>`     | `x y >`  | Greater than        |
| `<=`    | `x y <=` | Less or equal       |
| `>=`    | `x y >=` | Greater or equal    |
| `in`    | `x y in` | Check if x is in y  |

---

## Data Types

* **Numbers**: integers or floats
* **Strings**: `"..."`
* **Arrays**: `[...]`
* **Blocks**: `{ ... }` for code

### Array / String Ops

| Keyword  | Usage          | Effect                              |
| -------- | -------------- | ----------------------------------- |
| `len`    | `x len`        | Length                              |
| `get`    | `x y get`      | Get index y                         |
| `set`    | `x y z set`    | Set index y = z                     |
| `add`    | `x y add`      | Append y to x                       |
| `cut`    | `x y cut`      | Remove element y                    |
| `pop`    | `x pop`        | Pop from x (pushes value and new x) |
| `pops`   | `x y pops`     | Pop index y from x                  |
| `substr` | `x y z substr` | Get slice y→y+z                     |
| `split`  | `x y split`    | Split string x by y                 |

---

## IO Operations

| Keyword | Usage     | Effect                     |
| ------- | --------- | -------------------------- |
| `.`     | `x .`     | Print x (newline)          |
| `,`     | `x ,`     | Print x (no newline)       |
| `emit`  | `x emit`  | Print ASCII char of x      |
| `ascii` | `x ascii` | Push ASCII value of char x |
| `ask`   | `x ask`   | Prompt input with str x    |

### File Operations

| Keyword    | Usage         | Effect                    |
| ---------- | ------------- | ------------------------- |
| `create`   | `x create`    | Create file x             |
| `write`    | `x y write`   | Write x to file y         |
| `append`   | `x y append`  | Append x to file y        |
| `getline`  | `x y getline` | Get line x from file y    |
| `getlines` | `x getlines`  | Get all lines from file x |

---

## Control Flow

| Keyword | Usage                        | Effect                            |
| ------- | ---------------------------- | --------------------------------- |
| `fn`    | `fn name ... end`            | Define function                   |
| `if`    | `if ... do ... else ... end` | Conditional                       |
| `for`   | `x for i ... end`            | Repeat block x times, i = counter |
| `while` | `while ... do ... end`       | Loop while condition true         |
| `eval`  | `x eval`                     | Evaluate string/block x           |

---

## Type Conversion

| Keyword     | Usage         | Effect                           |
| ----------- | ------------- | -------------------------------- |
| `tostr`     | `x tostr`     | Convert int → string             |
| `toint`     | `x toint`     | Convert numeric string → int     |
| `isalpha`   | `x isalpha`   | Push 1 if string x is alphabetic |
| `isnumeric` | `x isnumeric` | Push 1 if string x is numeric    |
| `strip`     | `x strip`     | Strip trailing whitespace        |

---

## Environment / Utility

| Keyword    | Usage       | Effect                                       |
| ---------- | ----------- | -------------------------------------------- |
| `reset`    | `reset`     | Clear variables/functions, reset constants   |
| `release`  | `x release` | Remove x from vars, consts, functions        |
| `defined`  | `defined x` | Push 1 if x exists                           |
| `trace`    | `trace`     | Toggle debug trace                           |
| `clearscr` | `clearscr`  | Clear console                                |
| `wait`     | `x wait`    | Sleep x seconds                              |
| `use`      | `x use`     | Import x                                     |
| `quit`     | `quit`      | Exit interpreter                             |
| `pass`     | `pass`      | No operation                                 |

---

## Tips

* Everything operates on the **stack**; stay aware of it.
* Blocks `{}` are first-class; they can be pushed, popped, or `eval`ed.
* Constants and variables are distinct: `const` vs `store`.
* Functions are lambdas: capture variables at call time (stack-aware).
* Use `!stack` and `!trace` for debugging.