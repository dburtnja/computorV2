from abc import abstractmethod
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


def common_expression_get_value(expression):
    return Expression(expression, term_types=(TermVariable, )).evaluate()


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
        lower_name = name.lower()
        variable = self._stack_values.get(lower_name)
        if variable:
            return variable
        else:
            raise StackValueDoesntExist(f"Unresolved reference: '{name}'")

    def get_all_values(self):
        return self._stack_values


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


class TermMatrix(Term):

    def __init__(self, value):
        super().__init__(value)

    @staticmethod
    def can_parse_as_term(input_string):
        pass

    def get_value(self):
        pass


class Variable(StackValues):

    def _count_result(self):
        return int(common_expression_get_value(self._str_value))

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


class Matrix:
    OPENED_BRACKET = '['
    CLOSED_BRACKET = ']'
    DELIMETERS = r"([\[\],;])"

    def __init__(self, matrix_str):
        self._matrix_list = iter(
            el for el in split(self.DELIMETERS, matrix_str.replace(' ', ''))
            if el and el not in (';', ',')
        )
        self._matrix = self.__recursive()[0]
        self._y = len(self._matrix)
        if self._y:
            self._x = len(self._matrix[0])
            for row in self._matrix:
                if len(row) != self._x:
                    raise ValueError("Matrices have different columns len: '{}'.")

    def size(self):
        return self._x, self._y

    def __recursive(self):
        result = []

        for el in self._matrix_list:
            if el == self.OPENED_BRACKET:
                result.append(self.__recursive())
            elif el == self.CLOSED_BRACKET:
                return result
            else:
                result.append(el)
        return result

    def __add__(self, other):
        if isinstance(other, Matrix):
            result = []

            if other.size() != self.size():
                raise ValueError("Can't add matrices with different size.")
            for i, self_row in enumerate(self._matrix):
                inner_result = []
                for j, self_el in enumerate(self_row):
                    inner_result.append(common_expression_get_value(f"{self_el} + {other._matrix[i][j]}"))
                result.append(inner_result)
            return result
        return NotImplemented

    def __repr__(self):
        return str(self._matrix)


class Calculator(Value):

    def __init__(self, string):
        self._str_value = self._parse_group_value(self._get_value_pattern(), string)
        self._result = self._count_result()

    def _count_result(self):
        return common_expression_get_value(self._str_value)

    @classmethod
    def _get_re_left(cls):
        return r"(.*)\s*"

    @classmethod
    def _get_re_right(cls):
        return r"=\s*\?\s*"

    def __str__(self):
        return str(self._result)


class Computor:

    def __init__(self):
        self._stack_values = StackSingleton()

    def run(self):

        while True:
            input_string = input("> ")
            result = self._calculate_input(input_string)
            print(result)

    def _calculate_input(self, input_string):
        if input_string.startswith(':'):
            self._system_commands(input_string[1:])
        else:
            try:
                value = self._get_value(input_string)
                if value is None:
                    return f"Unexpected expression: {input_string}."
                if isinstance(value, StackValues):
                    self.add_to_stack(value)
                return str(value)
            except (StackValueDoesntExist, ValueError) as message:
                return str(message)

    def _system_commands(self, input_string):
        if input_string == "q":
            exit(0)
        elif input_string == "stack":
            print(f"{'Variable name':15s} Variable value")
            for name, value in self._stack_values.get_all_values().items():
                print(f"{name:15s} {value}")
        elif input_string == "self_test":
            self.__run_test(TEST_CASES)
        else:
            print(f"System command doesn't exist: '{input_string}'")

    def _get_value(self, input_string):
        for obj in (Function, Variable, Calculator):
            if obj.can_parse(input_string):
                return obj(input_string)
        saved_value = self.get_from_stack(input_string)
        return saved_value

    def add_to_stack(self, stack_value):
        self._stack_values.add_to_stack(stack_value)

    def get_from_stack(self, name):
        return self._stack_values.get_from_stack(name)

    def __run_test(self, test_cases):
        error_counter = 0

        for test_case, expected_result in test_cases.items():
            input_string = test_case
            if input_string == ":self_test":
                continue
            else:
                result = self._calculate_input(input_string)
                if result == expected_result:
                    print(f"Success: input = {input_string}, result = {result}")
                else:
                    print(f"ERROR: input='{input_string}'. Expected: '{expected_result}'. Result '{result}'")
                    error_counter += 1
        print(f"Run {len(test_cases)} tests. {error_counter} failed.")


TEST_CASES = {
    "a = 1": '1',
    "fu() = 0": "0",
    "fuN(x)": "Unresolved reference: 'fuN(x)'",
    "fun(1)=20": "Invalid parameter name: '1'",
    "b = a + b": "Unresolved reference: 'b'",
    "a": "1",
    "1 +(2-3)+(4-(3-2)) = ?": "3",
    "1 +(2-3)+(4-(3-a)) = ?": "2",
    "a = a +1": "2",
    "M = [[2, 3];[1, 2]] + [[fu(), 2];[1, 2]]": "[[2, 5];[2,4]]",
}


if __name__ == '__main__':
    computor = Computor()
    computor.run()
#
# print(Matrix("[2, 3]") + Matrix("[2, a]"))
