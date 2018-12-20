from computorV2 import FORBIDDEN_VARIABLE_NAMES, StackSingleton, StackValueDoesntExist, TermVariable, Variable
from polish_notation import Expression, Term
from re import match


RE_FUNCTION_NAME = r"([a-zA-Z]+)\(\s*[a-zA-Z]+\s*\)\s*"
RE_FUNCTION = r"([a-zA-Z]+)\(\s*[a-zA-Z\d]+\s*\)\s*"


#
#
# class Function(Term):
#
#     @staticmethod
#     def can_parse_as_term(input_string):
#         pass


def run_test():
    tests = {
        # '(52 + 2)^2*(2+(1+1))': '(52 + 2)**2*(2+(1+1))',
        # "a + b": '7 ',
        # "a + b - c": '7 ',
        # "5- 3": "5 -3",
        # '2+2': "2+2",
        # '3-2': "3-2",
        # '2*3': "2*3",
        # '6/2': "6/2",
        # '3^3': "3**3",
        # '6%5': "6%5",
        # '6.255+2': "6.255+2",
        # '4.242': "4.242",
        '-3 +2': "-3 +2",
        "2+(-(-3))": "2+(-(-3))",
        "2+--2": "2+--2",
    }
    StackSingleton().add_to_stack(Variable("a=2"))
    StackSingleton().add_to_stack(Variable("b=5"))
    for test_expression, python_test_expression in tests.items():
        try:
            result = eval(str(Expression(test_expression, term_types=(TermVariable,)).evaluate()))
        except StackValueDoesntExist as e:
            result = e
        expected = eval(python_test_expression)
        if result != expected:
            print(f"Error: {test_expression}: result: '{result}', expected: '{expected}'.")
        else:
            print(f"Success: {test_expression}: result: '{result}', expected: '{expected}'.")#hd khrystynka smart



if __name__ == '__main__':
    try:
        run_test()
    except StackValueDoesntExist as e:
        print(e)


