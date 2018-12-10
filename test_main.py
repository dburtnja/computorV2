from computorV2 import FORBIDDEN_VARIABLE_NAMES
from polish_notation import Expression, Term


class Variable(Term):

    def __init__(self, input_string):
        pass

    @staticmethod
    def can_pars(input_string):
        result = match(RE_NUMBER, input_string)
        if result:
            return result.group(0) == input_string and result.group(1) not in FORBIDDEN_VARIABLE_NAMES
        return False


class Function(Term):
    pass


def run_test():
    tests = {
        '(52 + 2)^2*(2+(1+1))': '(52 + 2)**2*(2+(1+1))'
    }
    for test_expression, python_test_expression in tests.items():
        result = eval(str(Expression(test_expression).evaluate()))
        expected = eval(python_test_expression)
        if result != expected:
            print(f"Error: {test_expression}: result: '{result}', expected: '{expected}'.")


if __name__ == '__main__':
    run_test()


