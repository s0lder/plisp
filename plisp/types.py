from plisp import environment


class Type: pass

class Atom(Type):
    def __init__(self, value):
        self.value = value

    def evaluate(self, env):
        return self

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class Number(Atom):
    def __init__(self, value):
        if type(value) in (float, int):
            self.value = value
        else:
            try:
                self.value = int(value)
            except ValueError:
                self.value = float(value)

    def __add__(self, other):
        if type(other) is Number:
            return Number(self.value + other.value)
        raise ValueError("Cannot add a non-number to a number")

    def __sub__(self, other):
        if type(other) is Number:
            return Number(self.value - other.value)
        raise ValueError("Cannot subtract a non-number from a number")

    def __mul__(self, other):
        if type(other) is Number:
            return Number(self.value * other.value)
        raise ValueError("Cannot multiply a non-number by a number")

    def __div__(self, other):
        if type(other) is Number:
            return Number(self.value / other.value)
        raise ValueError("Cannot divide a number by a non-number")

    def __truediv__(self, other):
        return self.__div__(other)

    def __cmp__(self, other):
        if type(other) is Number:
            return self.value - other.value
        raise ValueError("Cannot compare a number to a non-number")


class String(Atom):
    def __init__(self, value):
        try:
            self.value = str(value)
        except ValueError:
            raise


class List(Type):
    def __init__(self, *args):
        self.elements = args

    def evaluate(self, env):
        if len(self.elements) == 0:
            return self
        sym = self.elements[0]
        return sym.evaluate(env).apply(self.elements[1:], env)

    def __iter__(self):
        for e in self.elements:
            yield e

    def __len__(self):
        return len(self.elements)

    def __str__(self):
        return "(" + ' '.join([str(e) for e in self.elements]) + ")"


class Symbol(Type):
    def __init__(self, name):
        self.name = name

    def evaluate(self, env):
        res = env.lookup(self)
        if res is None:
            raise NameError(str(self) + " not found")
        return res

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if type(other) is Symbol:
            return self.name == other.name
        return self.name == other


class Function(Type):
    def __init__(self, args_list, expr, env):
        self.args_list = args_list
        self.env = env
        self.expression = expr

    def apply(self, args, call_env):
        env = environment.Environment(base=self.env)
        if len(args) != len(self.args_list):
            raise Exception("Arity error")
        bindings = zip(self.args_list, args)
        for sym, val in bindings:
            env.set(sym, val.evaluate(call_env))
        return self.expression.evaluate(env)


class Macro(Function):
    def apply(self, args, call_env):
        env = environment.Environment(base=self.env)
        for sym, val in zip(self.args_list, args):
            env.set(sym, val)
        return self.expression.evaluate(env)