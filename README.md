# SIMPL
A Super Implementable and Minimalist Programming Language that serves as an example and as a test for people wanting to learn how interpreters work.

I've included an example of a SIMPL interpreter in repo, but it'd be more smart to only use it as a reference to aid in the making of your own interpreter.

## Syntax
### Commands
The core of SIMPL's logic comes from its commands. Every command has a set amount of arguments, with zero optional arguments. This makes SIMPL programs incredibly easy to minify without requiring line-enders.

SIMPL is made of only 6 commands:
- `set [TYPE] [NAME] [VALUE]`: Assign a variable.
    - Variable values can be retrieved by simply putting the name of the variable as the value in any command.
    - Using `_` as the type should use the type of the variable, if any. Otherwise, throw an error.
- `conv [TYPE] [VALUE]`: Returns the value converted to the given type.
- `out [VALUE]`: Print a value to the console.
- `in [VALUE]`: Return an inputted value and also print a value. Identical to python's `input()`.
    - In some programming languages, this can be the most difficult command to implement, but in others this can be easiest. If it's too difficult to implement as is, you may change the behavior to input a value directly into a variable rather than return it as an expression.
- `label [NAME]`: Creates a label that can be jumped to.
- `jmpif [LABEL] [CONDITION]`: Jumps to a label if the condition is evaluated as true.
    - A condition is true if it is non-zero.

### Types
SIMPL has fixed data types. You cannot change the type of a variable without fully resetting it. SIMPL also lacks dynamically sized values (with the sole exception of strings), so it is impossible for there to be a memory leak.

SIMPL has 12 data types:
- Integers
    - Signed
        - `int8`
        - `int16`
        - `int32`
        - `int64`
    - Unsigned
        - `uint8`
        - `uint16`
        - `uint32`
        - `uint64`
- Floats
    - `flt16`
    - `flt32`
    - `flt64`
- Strings
    - `str`

### Math
SIMPL implements mathematical and logical operations through prefix notation (also known as Polish notation), where the operator precedes its operands. When the interpreter encounters an operator, it recursively evaluates the next two complete expressions as the arguments (x and y).

SIMPL supports 12 fundamental operators:
- Arithmetic
    - `+`: Addition
    - `-`: Subtraction
    - `*`: Multiplication
    - `/`: Division
    - `^`: Multiplication
    - `%`: Modulo
- Comparison
    - `<`: Less than
    - `>`: Greater than
    - `<=`: Less than or equal to
    - `>=`: Greater than or equal to
    - `==`: Equal to
    - `!=`: Not equal to

Please note again that math operations are structured `[OPERATOR] [X] [Y]`.

#### Evaluation Example
The standard algebraic formula `(6 - 4) * (10 / 5)` is written in SIMPL as `* - 6 4 / 10 5`.

You can trace the evauluation like so:
- The interpreter reads `*`, recognizing it needs two inputs.
- It then reads `-`, which is another expression that requires two inputs.
- It consumes `6` and `4`, evaluating `- 6 4` as `2`.
- The interpreter moves on the second argument of the encapsulating operator, finding `/`, which is yet another expression that requires two inputs.
- It consumes `10` and `5`, evaluating `/ 10 5` as also being `2`.
- It has now evaluated every argument of the encapsulated argument, so it evaluates `* 2 2` as `4`, which is our final answer!

If prefix notation feels confusing, it helps to imagine expressions as nested functions rather than operators. The example above can be mentally rewritten as `multiply(subtract(6, 4), divide(10, 5))`.