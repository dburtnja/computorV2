from abc import abstractmethod
from re import match, split

__all__ = ['Expression', 'Term']

OPERATOR_PRIORITY = 0
OPERATOR_FUNCTION = 1

RE_NUMBER = r"(\d+)"

OPEN_BRACKET = '('
CLOSE_BRACKET = ')'

BRACKETS = [OPEN_BRACKET, CLOSE_BRACKET]

OPERATORS = {
    '+': (1, lambda x, y: x + y),
    '-': (1, lambda x, y: x - y),
    '*': (2, lambda x, y: x * y),
    '/': (2, lambda x, y: x / y),
    '^': (3, lambda x, y: x ** y),
    '%': (2, lambda x, y: x % y),
}

EXPRESSION_SPLITTERS = [*BRACKETS, *OPERATORS]


class Stack:

    def __init__(self, iterable=None):
        if iterable:
            self._stack = list(iterable)
        else:
            self._stack = []

    def add(self, el):
        self._stack.append(el)

    def get(self):
        if self._stack:
            return self._stack.pop()

    def look_on_top(self, default=None):
        if self.is_empty():
            return default
        return self._stack[-1]

    def is_empty(self):
        return not self._stack

    def is_not_empty(self):
        return not self.is_empty()

    def get_from_bottom(self):
        return self._stack.pop(0)

    def __str__(self):
        return str(self._stack)

    def __bool__(self):
        return self.is_not_empty()


class ExpressionElement:

    @staticmethod
    @abstractmethod
    def can_pars(input_string):
        pass


class Operator(ExpressionElement):

    @staticmethod
    def can_pars(input_string):
        return input_string in OPERATORS

    def __init__(self, operator_str):
        if operator_str not in OPERATORS:
            raise ValueError(f"{operator_str} is not operator")
        operator = OPERATORS[operator_str]
        self._operator_str = operator_str
        self._priority = operator[OPERATOR_PRIORITY]
        self._function = operator[OPERATOR_FUNCTION]

    def __call__(self, left_argument, right_argument):
        if isinstance(left_argument, Term) and isinstance(right_argument, Term):
            result = self._function(left_argument._value, right_argument._value)
            return Number(str(result))
        raise TypeError(
            f"Ithere of input parameters should be instance of Term class, received: "
            f"'{left_argument} {right_argument}'"
        )

    def __return_ordering(self, other, method):
        if isinstance(other, Operator):
            return method(self._priority, other._priority)
        return NotImplemented

    def __lt__(self, other):
        return self.__return_ordering(other, lambda x, y: x < y)

    def __le__(self, other):
        return self.__return_ordering(other, lambda x, y: x <= y)

    def __gt__(self, other):
        return self.__return_ordering(other, lambda x, y: x > y)

    def __ge__(self, other):
        return self.__return_ordering(other, lambda x, y: x >= y)

    def __str__(self):
        return self._operator_str

    def __repr__(self):
        return f"Operator({self._operator_str})"


class Term(ExpressionElement):

    _value = None

    @staticmethod
    @abstractmethod
    def can_pars(input_string):
        pass

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return f"Term({self._value})"


class Number(Term):

    def __init__(self, input_string):
        if set(input_string).difference('0123456789.'):
            raise ValueError(f"'{input_string}' isn't a number.")
        else:
            self._value = eval(input_string)

    @staticmethod
    def can_pars(input_string):
        result = match(RE_NUMBER, input_string)
        if result:
            return result.group(0) == input_string
        return False


class ExpressionElementFactory:

    def __init__(self, term_types=()):
        invalid_types = [term_type for term_type in term_types if not isinstance(term_type, Term)]
        if invalid_types:
            raise TypeError(f"{invalid_types} should be instance of Term class")
        self._term_types = term_types

    def get_expression_part(self, expression_element):
        if Operator.can_pars(expression_element):
            return Operator(expression_element)
        if Number.can_pars(expression_element):
            return Number(expression_element)
        for term in self._term_types:
            if term.can_pars(expression_element):
                return term(expression_element)
        raise ValueError(f"Can't pars such expression term: '{expression_element}''")


class Expression:

    def __init__(self, string_expression, term_types=()):
        self._expression_element_factory = ExpressionElementFactory(term_types)
        self._expression_stack = Stack()
        string_expression = string_expression.replace(" ", "")
        self._parsing_string_expression(string_expression)

    def _parsing_string_expression(self, string_expression):
        operators_stack = Stack()
        pattern = f"([//{r'/'.join(EXPRESSION_SPLITTERS)}])"

        for element in split(pattern, string_expression):
            if element:
                if element == OPEN_BRACKET:
                    operators_stack.add(element)
                elif element == CLOSE_BRACKET:
                    self._remove_open_bracket_from(operators_stack)
                else:
                    self._handle_terms(element, operators_stack)

        while operators_stack:
            self._expression_stack.add(operators_stack.get())

    def evaluate(self):
        buffer = Stack()

        while self._expression_stack:
            element = self._expression_stack.get_from_bottom()
            if isinstance(element, Operator):
                method = element
                right_number = buffer.get()
                left_number = buffer.get()
                result = method(left_number, right_number)
                buffer.add(result)
            else:
                buffer.add(element)
        return buffer.get()

    def _remove_open_bracket_from(self, operators_stack):
        while operators_stack:
            operation = operators_stack.get()
            if operation == OPEN_BRACKET:
                return
            self._expression_stack.add(operation)

    def __handle_operators_in_stacks(self, operator, operators_stack):
        top_operator = operators_stack.look_on_top()
        if not top_operator or top_operator in BRACKETS or top_operator <= operator:
            operators_stack.add(operator)
        else:
            self._expression_stack.add(operators_stack.get())
            operators_stack.add(operator)

    def _handle_terms(self, element, operators_stack):
        element = self._expression_element_factory.get_expression_part(element)
        if isinstance(element, Operator):
            self.__handle_operators_in_stacks(element, operators_stack)
        else:
            self._expression_stack.add(element)
