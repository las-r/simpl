import numpy as np
import operator
import shlex
import sys

# cmplex interpreter example
# forked from simpl
# by las-r

# token stream class
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
    
# return exception
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

# type parser
def parsetype(ptype, pval):
    if ptype == "int8": return np.int8(pval)
    elif ptype == "int16": return np.int16(pval)
    elif ptype in ["int32", "int"]: return np.int32(pval)
    elif ptype == "int64": return np.int64(pval)
    elif ptype == "uint8": return np.uint8(pval)
    elif ptype == "uint16": return np.uint16(pval)
    elif ptype in ["uint32", "uint"]: return np.uint32(pval)
    elif ptype == "uint64": return np.uint64(pval)
    elif ptype in ["flt16", "half"]: return np.float16(pval)
    elif ptype in ["flt32", "flt", "single"]: return np.float32(pval)
    elif ptype in ["flt64", "double"]: return np.float64(pval)
    elif ptype == "str": return np.str_(pval)
    elif ptype == "bool": return np.bool_(pval)
    else: raise TypeError(f"{ptype} is not a valid type.")

# operator dictionaries
BINOPER = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow,
    "%": operator.mod,
    "&": operator.and_,
    "|": operator.or_,
    "$": operator.xor,
    "<": lambda x, y: x < y,
    ">": lambda x, y: x > y,
    "<=": lambda x, y: x <= y,
    ">=": lambda x, y: x >= y,
    "==": lambda x, y: x == y,
    "!=": lambda x, y: x != y,
    "&&": lambda x, y: x and y,
    "||": lambda x, y: x or y,
    "$$": lambda x, y: np.bool_(x) != np.bool_(y),
}
UNOPER = {
    "~": operator.inv,
    "!": operator.not_
}

# tokenizer
def tokenize(code):
    lexer = shlex.shlex(code, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = "//"
    return list(lexer)

# expression executer (recursive)
def executeexpr(stream: Stream):
    global var, func
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
    
    # if
    elif cmd == "if":
        cond = executeexpr(stream)
        if not cond:
            depth = 1
            while depth > 0:
                token = stream.next()
                if token == "if":
                    depth += 1
                elif token == "endif":
                    depth -= 1
                    
    # while
    elif cmd == "while":
        entry = stream.i
        while True:
            cond = executeexpr(stream)
            if cond:
                while stream.tokens[stream.i] != "endwhile":
                    executeexpr(stream)
                stream.next()
                stream.i = entry
            else:
                depth = 1
                while depth > 0:
                    token = stream.next()
                    if token == "while":
                        depth += 1
                    elif token == "endwhile":
                        depth -= 1
                break
            
    # function define
    elif cmd == "func":
        rtype = stream.next()
        fname = stream.next()
        argcount = executeexpr(stream)
        args = []
        for _ in range(argcount):
            atype = stream.next()
            aname = stream.next()
            args.append({"type": atype, "name": aname})
        start = stream.i
        func[fname] = {"start": start, "type": rtype, "args": args}
        depth = 1
        while depth > 0:
            token = stream.next()
            if token == "func":
                depth += 1
            elif token == "endfunc":
                depth -= 1
                
    # function return
    elif cmd == "ret":
        val = executeexpr(stream)
        raise ReturnException(val)
    
    # function call:
    elif cmd == "call":
        fname = stream.next()
        if fname not in func:
            raise Exception(f"{fname} not found in functions.")
        finfo = func[fname]
        evalargs = []
        for argdef in finfo["args"]:
            val = executeexpr(stream)
            evalargs.append(parsetype(argdef["type"], val))
        ovar = var
        var = {k: v.copy() for k, v in ovar.items()}
        for argdef, evalval in zip(finfo["args"], evalargs):
            var[argdef["name"]] = {"type": argdef["type"], "val": evalval}
        cstk.append(stream.i) 
        stream.i = finfo["start"]
        retval = 0
        try:
            while stream.get() != "endfunc":
                executeexpr(stream)
        except ReturnException as e:
            retval = e.value
        stream.i = cstk.pop()
        var = ovar
        return parsetype(finfo["type"], retval)
    
    # module define
    elif cmd == "mod":
        mname = stream.next()
        mod[mname] = {"var": {}, "func": {}}
        ovar, ofunc = var, func
        var, func = mod[mname]["var"], mod[mname]["func"]
        while stream.get() != "endmod":
            executeexpr(stream)
        stream.next()
        var, func = ovar, ofunc
        
    # module get
    elif cmd == "get":
        mname = stream.next()
        thing = stream.next()
        if mname not in mod:
            raise Exception(f"{mname} not found in modules.")
        tmod = mod[mname]
        if thing in tmod["func"]:
            finfo = tmod["func"][thing]
            evalargs = []
            for argdef in finfo["args"]:
                val = executeexpr(stream)
                evalargs.append(parsetype(argdef["type"], val))
            ovar, ofunc = var, func
            var = {k: v.copy() for k, v in tmod["var"].items()}
            func = tmod["func"]
            for argdef, evalval in zip(finfo["args"], evalargs):
                var[argdef["name"]] = {"type": argdef["type"], "val": evalval}
            cstk.append(stream.i)
            stream.i = finfo["start"]
            retval = 0
            try:
                while stream.get() != "endfunc":
                    executeexpr(stream)
            except ReturnException as e:
                retval = e.value
            stream.i = cstk.pop()
            var, func = ovar, ofunc
            return parsetype(finfo["type"], retval)
        elif thing in tmod["var"]:
            return tmod["var"][thing]["val"]
        else:
            raise Exception(f"{thing} not found in {mname}.")
        
    # module expose
    elif cmd == "exp":
        mname = stream.next()
        thing = stream.next()
        if mname not in mod:
            raise Exception(f"{mname} not found in modules.")
        tmod = mod[mname]
        if thing in tmod["func"] and thing not in func:
            func[thing] = tmod["func"][thing]
        elif thing in tmod["var"] and thing not in var:
            var[thing] = tmod["var"][thing]
        else:
            raise Exception(f"{thing} not in {mname} or has already been exposed.")
    
    # math
    elif cmd in BINOPER:
        x = executeexpr(stream)
        y = executeexpr(stream)
        return BINOPER[cmd](x, y)
    elif cmd in UNOPER:
        x = executeexpr(stream)
        return UNOPER[cmd](x)
    
    # variables / literals
    else:
        if cmd in var:
            return var[cmd]["val"]
        try:
            if cmd == "true":
                return True
            elif cmd == "false":
                return False
            elif "." in cmd:
                return np.float64(cmd)
            return np.int32(cmd)
        except ValueError:
            return np.str_(cmd)
    return 0        

# env values
cstk = []
var = {}
lbl = {}
func = {}
mod = {}

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