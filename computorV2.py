from abc import abstractmethod
from pyparsing import nestedExpr, ParseResults
from pprint import pprint
from re import match, search, split
from polish_notation import Expression, Term


RE_RIGHT = r"=\s*(.*)"
RE_VARIABLE = r"([a-zA-Z]+)\s*"
RE_FUNCTION_NAME = r"([a-zA-Z]+)\(\s*[a-zA-Z]+\s*\)\s*"
RE_FUNCTION = r"([a-zA-Z]+)\(\s*[a-zA-Z\d]+\s*\)\s*"

FORBIDDEN_VARIABLE_NAMES = ['i']

FIRST_STEP_OPERATORS = ['^']
SECOND_STEP_OPERATORS = ['*', '/', '%']
THIRD_STEP_OPERATORS = ['+', '-']
OPERATORS = [*FIRST_STEP_OPERATORS, *SECOND_STEP_OPERATORS, *THIRD_STEP_OPERATORS]


class StackValueDoesntExist(RuntimeWarning):
    pass


class StackSingleton:

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = super(StackSingleton, cls).__new__(cls, *args, **kwargs)
            cls._stack_values = {}
        return cls._singleton

    def add_to_stack(self, stack_value):
        if isinstance(stack_value, StackValues):
            name = stack_value.get_name().lower()
            self._stack_values[name] = stack_value
        else:
            raise ValueError(f"stack_value should be instance of StackValues class, received: '{type(stack_value)}'")

    def get_from_stack(self, name):
        name = name.lower()
        variable = self._stack_values.get(name)
        if variable:
            return variable
        else:
            raise StackValueDoesntExist(f"Unresolved reference: '{name}'")


class Value:

    @classmethod
    @abstractmethod
    def _get_re_left(cls):
        pass

    @classmethod
    @abstractmethod
    def _get_re_right(cls):
        pass

    @staticmethod
    def _parse_group_value(reg_exp, string):
        result = search(reg_exp, string)
        return result.group(1)

    @classmethod
    def _get_value_pattern(cls):
        return f"{cls._get_re_left()}{cls._get_re_right()}"

    @classmethod
    def can_parse(cls, string):
        pattern = cls._get_value_pattern()
        result = match(pattern, string)
        if result:
            return result.group(0) == string and result.group(1) not in FORBIDDEN_VARIABLE_NAMES
        return False


class StackValues(Value):

    def __init__(self, string):
        self._name = self._parse_group_value(self._get_re_left(), string)
        self._str_value = self._parse_group_value(self._get_re_right(), string)
        self._result = self._count_result()

    def get_name(self):
        return self._name

    def get_result(self):
        return self._result

    def __str__(self):
        return str(self._result)

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def _count_result(self):
        pass


class TermVariable(Term):

    def __init__(self, input_string):
        variable_name = input_string.strip().lower()
        variable = StackSingleton().get_from_stack(variable_name)
        super().__init__(variable.get_result())

    @staticmethod
    def can_parse_as_term(input_string):
        result = match(RE_VARIABLE, input_string)
        if result:
            return result.group(0) == input_string and result.group(1) not in FORBIDDEN_VARIABLE_NAMES
        return False

    def get_value(self):
        return self._value


class Variable(StackValues):

    def _count_result(self):
        return Expression(self._str_value, term_types=(TermVariable, )).evaluate().get_value()

    @classmethod
    def _get_re_left(cls):
        return RE_VARIABLE

    @classmethod
    def _get_re_right(cls):
        return RE_RIGHT


class Function(StackValues):

    @classmethod
    def _get_re_left(cls):
        return RE_FUNCTION_NAME

    @classmethod
    def _get_re_right(cls):
        return RE_RIGHT


class Calculator(Value):

    @classmethod
    def _get_re_left(cls):
        return r"(.*)\s*"

    @classmethod
    def _get_re_right(cls):
        return r"=\s*\?\s*"

    def __str__(self):
        return str(self._expression)


class Computor:

    def __init__(self):
        self._stack_values = StackSingleton()

    def run(self):
        input_string = None

        while True:
            input_string = input("> ")
            if input_string.startswith(':'):
                self._system_commands(input_string[1:])
            else:
                value = self._get_value(input_string)
                if isinstance(value, StackValues):
                    self.add_to_stack_and_print(value, input_string)
                elif value is not None:
                    print(value)
                else:
                    print(f"Unexpected expression: {input_string}.")

    @staticmethod
    def _system_commands(input_string):
        if input_string == "q":
            exit(0)
        elif input_string == "stack":
            print(f"{'Variable name':15s} Variable value")
            for name, value in Computor._stack_values.items():
                print(f"{name:15s} {value}")
        else:
            print(f"System command doesn't exist: '{input_string}'")

    def _get_value(self, input_string):
        for obj in (Function, Variable, Calculator):
            if obj.can_parse(input_string):
                return obj(input_string)
        saved_value = self.get_from_stack(input_string)
        return saved_value

    def add_to_stack_and_print(self, stack_value, input_string):
        if stack_value:
            self.add_to_stack(stack_value)
            print(stack_value)
        else:
            print(f"Not valid token: '{input_string}'")

    def add_to_stack(self, stack_value):
        name = stack_value.get_name().lower()
        self._stack_values.add_to_stack(name, stack_value)

    def get_from_stack(self, name):
        name = name.lower()
        return self._stack_values.get_from_stack(name)

#
# def test():
#     test_strings = {
#         "a = 1": 1,
#         "fu() = 0": None,
#         "fuN(x)": None,
#         "fun(1)=20": None,
#         "b = a + b": None,
#         "a": 1,
#         "1 +(2-3)+(4-(3-2)) = ?": 1,
#         "1 +(2-3)+(4-(3-a)) = ?": 0,
#         "a = a +1": 2,
#     }




# RE_VARIABLE_NAME = r"([a-zA-Z]+)"
# RE_FUNCTION_NAME = r"([a-zA-Z]+)\(\s*[a-zA-Z]+\s*\)\s*"
# RE_FUNCTION = r"([a-zA-Z]+)\(\s*[a-zA-Z\d]+\s*\)\s*"
#
#

def run_test():
    tests = {
        '(52 + 2)^2*(2+(1+1))': '(52 + 2)**2*(2+(1+1))',
    }
    for test_expression, python_test_expression in tests.items():
        result = eval(str(Expression(test_expression).evaluate()))
        expected = eval(python_test_expression)
        if result != expected:
            print(f"Error: {test_expression}: result: '{result}', expected: '{expected}'.")
        else:
            print(f"Success: {test_expression}: result: '{result}', expected: '{expected}'.")


if __name__ == '__main__':
    computor = Computor()
    computor.run()

