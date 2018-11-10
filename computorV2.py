from abc import abstractmethod
from pyparsing import nestedExpr, ParseResults

from re import match, search, split

RE_RIGHT = r"=\s*(.*)"
FORBIDDEN_VARIABLE_NAMES = ['i']

FIRST_STEP_OPERATORS = ['^']
SECOND_STEP_OPERATORS = ['*', '/', '%']
THIRD_STEP_OPERATORS = ['+', '-']
OPERATORS = [*FIRST_STEP_OPERATORS, *SECOND_STEP_OPERATORS, *THIRD_STEP_OPERATORS]


class Value:
    RE_LEFT = None
    RE_RIGHT = None

    @staticmethod
    def _parse_group_value(reg_exp, string):
        result = search(reg_exp, string)
        return result.group(1)

    @classmethod
    def _get_value_pattern(cls):
        return f"{cls.RE_LEFT}{cls.RE_RIGHT}"

    @classmethod
    def can_parse(cls, string):
        pattern = cls._get_value_pattern()
        result = match(pattern, string)
        if result:
            return result.group(0) == string and result.group(1) not in FORBIDDEN_VARIABLE_NAMES
        return False


class Expression:

    def __init__(self, expression):
        if isinstance(expression, ParseResults):
            self._create_expression_from_list(expression)
        else:
            self._create_expression_from_string(expression)

    def _create_expression_from_list(self, list_expression):
        format_string = f"([{''.join(OPERATORS)}])"
        # print(format_string)
        # self._expression = [
        #     Expression(term) if isinstance(term, ParseResults) else term
        #     for term in list_expression
        # ]
        self._expression = []
        for term in list_expression:
            if isinstance(term, ParseResults):
                self._expression.append(Expression(term))
            else:
                res = split(format_string, term)
                res = list(filter(None, res))
                self._expression.extend(res)

    def _create_expression_from_string(self, str_expression):
        self._str_expression = f"({str_expression})".replace(' ', '')
        nested_exp = nestedExpr().parseString(self._str_expression)[0]
        self._create_expression_from_list(nested_exp)

    def __str__(self):
        return str(self._expression)

    def __repr__(self):
        return self.__str__()


class StackValues(Value):

    def __init__(self, string):
        self._name = self._parse_group_value(self.RE_LEFT, string)
        self._value = self._parse_group_value(self.RE_RIGHT, string)

    def get_name(self):
        return self._name

    def get_value(self):
        return self._value

    def __str__(self):
        return str(self._value)


class Variable(StackValues):
    RE_LEFT = r"([a-zA-Z]+)\s*"
    RE_RIGHT = RE_RIGHT


class Function(StackValues):
    RE_LEFT = r"([a-zA-Z]+)\(\s*[a-zA-Z]+\s*\)\s*"
    RE_RIGHT = RE_RIGHT


class Calculator(Value):
    RE_LEFT = r"(.*)\s*"
    RE_RIGHT = r"=\s*\?\s*"

    def __init__(self, string):
        self._expression = Expression(
            self._parse_group_value(self._get_value_pattern(), string)
        )

    def __str__(self):
        return str(self._expression)


class Computor:

    def __init__(self):
        self._stack_values = {}

    def run(self):
        input_string = None

        while True:
            input_string = input("> ")
            if input_string == ":q":
                return True
            value = self._get_value(input_string)
            if isinstance(value, StackValues):
                self._add_to_stack_and_print(value, input_string)
            elif value is not None:
                print(value)
            else:
                print(f"Unexpected expression: {input_string}.")

    def _get_value(self, input_string):
        for obj in (Function, Variable, Calculator):
            if obj.can_parse(input_string):
                return obj(input_string)
        saved_value = self._get_from_stack(input_string)
        return saved_value

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
        "a": 1,
        "1 +(2-3)+(4-(3-2)) = ?": 1
    }


if __name__ == '__main__':
    computor = Computor()
    computor.run()

# from numpy import roots
# print(nestedExpr(opener='(', closer=')').parseString('(x= 3+2 (1 +1) + (2 /((2-1) + 3)))'))
