from computorV2 import FORBIDDEN_VARIABLE_NAMES, StackSingleton
from polish_notation import Expression, Term
from re import match


RE_VARIABLE_NAME = r"([a-zA-Z]+)"
RE_FUNCTION_NAME = r"([a-zA-Z]+)\(\s*[a-zA-Z]+\s*\)\s*"
RE_FUNCTION = r"([a-zA-Z]+)\(\s*[a-zA-Z\d]+\s*\)\s*"


class Variable(Term):

    def __init__(self, input_string):
        variable_name = input_string.strip().lower()
        super().__init__(StackSingleton().get_from_stack(variable_name))

    @staticmethod
    def can_parse_as_term(input_string):
        result = match(RE_VARIABLE_NAME, input_string)
        if result:
            return result.group(0) == input_string and result.group(1) not in FORBIDDEN_VARIABLE_NAMES
        return False

    def get_value(self):
        return self._value
#
#
# class Function(Term):
#
#     @staticmethod
#     def can_parse_as_term(input_string):
#         pass


def run_test():
    tests = {
        '(52 + 2)^2*(2+(1+1))': '(52 + 2)**2*(2+(1+1))',
    }
    for test_expression, python_test_expression in tests.items():
        result = eval(str(Expression(test_expression, term_types=(Variable, )).evaluate()))
        expected = eval(python_test_expression)
        if result != expected:
            print(f"Error: {test_expression}: result: '{result}', expected: '{expected}'.")
        else:
            print(f"Success: {test_expression}: result: '{result}', expected: '{expected}'.")


if __name__ == '__main__':
    run_test()


