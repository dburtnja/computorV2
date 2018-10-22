from pyparsing import nestedExpr
from re import match

RE_VALUE = r""


class Variable:
    # _name = None
    # _value = None

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __str__(self):
        return self._value


class Function:
    RE_NAME = r"(\w+)(\s*(\w+)\s*)"
    RE_VALUE = RE_VALUE

    def __init__(self, string):
        self._name = string
        self._value = string

    def is_function(self, string):
        pattern = f"{self.RE_NAME}\s*=\s*{self.RE_VALUE}"
        return match(pattern, string).group(0) == string


class Computor:

    def __init__(self):
        self._simple_parser = nestedExpr()
        self._variables = {}

    def run(self):
        input_string = None

        while input_string != "q":
            input_string = input("> ")
            if Function.is_function(input_string):
                self._variables[Function] = Function()
            print(input_string)


if __name__ == '__main__':
    computor = Computor()
    computor.run()
