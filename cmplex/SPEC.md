# CMPLEx Specification
A Complementary Modular Programming Language Extras specification built on top of the SIMPL blueprint. This language serves as an advanced tutorial step for people wanting to understand structural abstraction, scoping, and modules within an interpreter environment.

## Language Deltas (At a Glance)
Compared to the base SIMPL language, CMPLEx introduces structural control flow constructs, lexical modularity, and fully scoped functions while stripping away flat branch addresses.

### Removals
* **`label [NAME]`**: Removed in favor of proper structural control blocks (`if`/`endif` and `while`/`endwhile`).
* **`jmpif [LABEL] [CONDITION]`**: Removed in favor of structured control flow.

### Additions
* **Structured Flow Control**: Block-scoped conditional statements (`if`) and loops (`while`).
* **First-Class Functions**: Complete function support (`func`) featuring recursive local execution framing and automated type safety checks upon return structures.
* **Scoping Contexts**: Call-stack architecture isolating variable namespaces globally/locally.
* **Encapsulated Modularity**: Modules (`mod`) acting as closed lexical environments that selectively expose variables or subroutines via direct accessor operations (`get`) or global mutations (`exp`).

## Updated Syntax
### Commands
Every structural delimiter block acts as an active keyword component within a stream layout context. The core command vocabulary has expanded from 6 to 14 instructions:

#### 1. Core Inherited Commands
* `set [TYPE] [NAME] [VALUE]`: Standard variable assignment.
* `conv [TYPE] [VALUE]`: Explicit type conversion evaluation.
* `out [VALUE]`: Evaluates and prints to standard output.
* `in [VALUE]`: Prompts user input displaying evaluated prefix value expression.

#### 2. Structured Control Flow Commands (NEW)
* `if [CONDITION] ... endif`: Evaluates `CONDITION`. If falsy, branches forward skipping the internal nested stream block until matching `endif`. Supports nested depth indexing.
* `while ... endwhile`: Tracks the evaluation block point. Evaluates `CONDITION` iteratively. If truthy, the interpreter steps forward into operations and rewinds its position to loop evaluating sequentially until `CONDITION` drops to falsy.

#### 3. Execution Scope/Function Commands (NEW)
* `func [RETURN_TYPE] [NAME] [ARG_COUNT] [ARG_1_TYPE] [ARG_1_NAME] ... endfunc`: Defines a local execution closure with predefined parameter bounds. Immediately steps past internal statements until matching `endfunc` when interpreted within normal top-level sequential streams.
* `ret [VALUE]`: Escapes execution out of the current function context frames, raising its product back to its invocation origin.
* `call [FUNC_NAME] [ARG1] [ARG2] ...`: Creates a localized structural map state frame copy of global elements, parses arguments dynamically matching parameter schemas, and jumps into execution.

#### 4. Namespace and Modular Isolation Commands (NEW)
* `mod [NAME] ... endmod`: Generates closed variable and functional dictionaries bound cleanly into an identifier space map matching `NAME`.
* `get [MOD_NAME] [MEMBER_NAME]`: Evaluates the runtime context of isolated assets inside targeted modules. Can call isolated subroutines or pull static variables directly.
* `exp [MOD_NAME] [MEMBER_NAME]`: Copies a reference of targeted modular assets out directly into current tracking scopes, making it transparently available to local contexts without using explicit module routing.

## Types
CMPLEx updates literal processing typing to feature full Boolean support and establishes systematic structural aliases to balance performance configurations across targets.

### Type Mapping Configuration
There is now one new type: `bool`. `int32` has alias `int` and `uint32` has alias `uint`. `flt16` has alias `half`, `flt32` has aliases `flt` and `single`, and `flt64` has alias `double`.

#### Literals Behavior Changes
* Explicit keyword mappings catch values matching `true` or `false` to translate structural constants cleanly down to Boolean primitives.
* Unmapped alphanumeric literal fallbacks default systematically to internal primitive allocations: standard numbers drop directly to `np.int32` or `np.float64`, while characters allocate down to standard `np.str_` strings.

## Math & Logical Operators
CMPLEx extends the prefix operational notation stack. Arithmetic operations continue to consume two arguments recursively ($X$ and $Y$). Logical evaluations operate with explicit Boolean output semantics.

### Binary Operators (`BINOPER`)
* **Arithmetic**: `+`, `-`, `*`, `/`, `^`, `%`
* **Bitwise**: `&` (AND), `|` (OR), `$` (XOR)
* **Comparison**: `<`, `>`, `<=`, `>=`, `==`, `!=`
* **Short-Circuit Short logical**: `&&` (Logical AND), `||` (Logical OR), `$$` (Logical XOR)

### Unary Operators (`UNOPER`)
Unary operators precede a single tracking symbol expression:

* `~`: Bitwise inversion / Complement operations.
* `!`: Boolean Logical Negation.

## Context Evaluation Architecture
Unlike the flat, linear sequence system of base SIMPL, CMPLEx tracks and executes statements using an explicitly maintained environment structure:

* **`cstk` (Call Stack)**: Keeps a sequential record of token indices to successfully route execution paths back to the correct statement following nested function call terminations.
* **`var` / `func` Scoping Maps**: Stores active state contexts. During custom subroutine executions, a shallow copy mutation protects the top-level outer scopes from localized namespace collisions while supporting access to upper outer contexts.
* **`mod` Isolated Mapping**: A distinct directory layout that encapsulates distinct parameter structures (`var` and `func`) to prevent variable tracking leakage across domain layers.