import numpy as np
import operator
import shlex
import sys

# simpl interpreter example
# by las-r

# token stream class
# this is really not necessary, i just thought it made the syntax look cleaner
# and makes the token stream itself a lot easier to understand.
class Stream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.len = len(tokens)
        self.i = 0
        
    def get(self):
        return self.tokens[self.i]
        
    def next(self):
        token = self.tokens[self.i]
        self.i += 1
        return token
    
    def has_next(self):
        return self.i < self.len

# type parser
# this is to show you don't necessarily need a dictionary of type conversions.
def parsetype(ptype, pval):
    if ptype == "int8": return np.int8(pval)
    elif ptype == "int16": return np.int16(pval)
    elif ptype == "int32": return np.int32(pval)
    elif ptype == "int64": return np.int64(pval)
    elif ptype == "uint8": return np.uint8(pval)
    elif ptype == "uint16": return np.uint16(pval)
    elif ptype == "uint32": return np.uint32(pval)
    elif ptype == "uint64": return np.uint64(pval)
    elif ptype == "flt16": return np.float16(pval)
    elif ptype == "flt32": return np.float32(pval)
    elif ptype == "flt64": return np.float64(pval)
    elif ptype == "str": return np.str_(pval)
    else: raise TypeError(f"{ptype} is not a valid type.")

# operator dictionary
# this is what the type conversions thing was talking about, but with operators
# instead.
OPER = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow,
    "%": operator.mod,
    "<": lambda x, y: 1 if x < y else 0,
    ">": lambda x, y: 1 if x > y else 0,
    "<=": lambda x, y: 1 if x <= y else 0,
    ">=": lambda x, y: 1 if x >= y else 0,
    "==": lambda x, y: 1 if x == y else 0,
    "!=": lambda x, y: 1 if x != y else 0,
}

# tokenizer
# shlex is used for simplicity's sake, it does a lot of the hard work, like
# dealing with strings. you can change some of the lexer settings here.
def tokenize(code):
    lexer = shlex.shlex(code, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = "//"
    return list(lexer)

# expression executer (recursive)
# this is the most complicated part, but the language's name is literally
# simple, so it's really not that difficult to understand once you grasp
# recursion.
def executeexpr(stream: Stream):
    cmd = stream.next()
    
    # var assign
    if cmd == "set":
        vtype = stream.next()
        vname = stream.next()
        vval = executeexpr(stream)
        if vtype == "_":
            if vname in var:
                vvar = var[vname]
                vvar["val"] = parsetype(vvar["type"], vval)
            else:
                raise Exception(f"{vname} not found in variables.")
        else:
            var[vname] = {
                "type": vtype,
                "val": parsetype(vtype, vval)
            }
    
    # convert type
    elif cmd == "conv":
        ctype = stream.next()
        cval = executeexpr(stream)
        return parsetype(ctype, cval)
    
    # output
    elif cmd == "out":
        val = executeexpr(stream)
        print(val)
    
    # input
    elif cmd == "in":
        val = executeexpr(stream)
        return input(val)
    
    # label
    elif cmd == "label":
        label = stream.next()
        lbl[label] = stream.i
    
    # jump if
    elif cmd == "jmpif":
        label = stream.next()
        cond = executeexpr(stream)
        if int(cond) != 0:
            if label in lbl:
                stream.i = lbl[label]
            else: raise Exception(f"{label} not found in labels.")
    
    # math
    elif cmd in OPER:
        x = executeexpr(stream)
        y = executeexpr(stream)
        return OPER[cmd](x, y)
    
    # variables / literals
    else:
        if cmd in var:
            return var[cmd]["val"]
        try:
            if "." in cmd:
                return float(cmd)
            return int(cmd)
        except ValueError:
            return cmd
    return 0        

# everything below this is the "main" code, pretty much all it does is read
# code from a file and call the functions. it also has the variable and label
# dictionaries.

# env values
var = {}
lbl = {}

# code
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("usage: python interpreter.py [filename]")
    sys.exit(1)
with open(filename, "r") as f:
    code = f.read()

# execute the functions
tokens = tokenize(code)
stream = Stream(tokens)
while stream.has_next():
    executeexpr(stream)