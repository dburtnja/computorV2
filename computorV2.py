from abc import abstractmethod
from pyparsing import nestedExpr

from re import match, search, findall

RE_VALUE = r"=\s(.*)"
FORBIDDEN_VARIABLE_NAMES = ['i']


class StackValues:
    RE_NAME = None
    RE_VALUE = None

    def __init__(self, string):
        self._name = self._parse_name(string)
        self._value = self._parse_value(string)

    def _parse_name(self, string):
        result = search(self.RE_NAME, string)
        return result.group(1)

    def _parse_value(self, string):
        result = search(self.RE_VALUE, string)
        return result.group(1)

    def get_name(self):
        return self._name

    def get_value(self):
        return self._value

    @classmethod
    def can_parse(cls, string):
        pattern = f"{cls.RE_NAME}{cls.RE_VALUE}"
        result = match(pattern, string)
        if result:
            return result.group(0) == string and result.group(1) not in FORBIDDEN_VARIABLE_NAMES
        return False

    def __str__(self):
        return str(self._value)


class Variable(StackValues):
    RE_NAME = r"([a-zA-Z]+)\s*"
    RE_VALUE = RE_VALUE


class Function(StackValues):
    RE_NAME = r"([a-zA-Z]+)\(\s*[a-zA-Z]+\s*\)\s*"
    RE_VALUE = RE_VALUE


class Expression:
    pass


class Computor:

    def __init__(self):
        self._simple_parser = nestedExpr()
        self._stack_values = {}

    def run(self):
        input_string = None

        while True:
            input_string = input("> ")
            if input_string == "q":
                return True
            if "?" in input_string:
                self._calculate_expression(input_string)
            else:
                stack_value = self._get_stack_value(input_string)
                self._add_to_stack_and_print(stack_value, input_string)

    def _calculate_expression(self, input_string):
        pass
        # variables = [var for var in ]
        # return self._get_stack_value()

    def _get_stack_value(self, input_string):
        if Function.can_parse(input_string):
            return Function(input_string)
        if Variable.can_parse(input_string):
            return Variable(input_string)
        return None

    def _add_to_stack_and_print(self, stack_value, input_string):
        if stack_value:
            self._add_to_stack(stack_value)
            print(stack_value)
        else:
            print(f"Not valid token: '{input_string}'")

    def _add_to_stack(self, stack_value):
        name = stack_value.get_name().lower()
        self._stack_values[name] = stack_value

    def _get_from_stack(self, name):
        name = name.lower()
        return self._stack_values.get(name)


def test():
    test_strings = {
        "a = 1": 1,
        "fu() = 0": None,
        "fuN(x)": None,
        "fun(1)=20": None,
        "b = a + b": None,
        # ""
    }


# if __name__ == '__main__':
#     computor = Computor()
#     computor.run()

from numpy import roots
print(nestedExpr(opener='(', closer=')').parseString('(x= 3+2 (1 +1) + (2 /((2-1) + 3)))'))
