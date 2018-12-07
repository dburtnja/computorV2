

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


class Expression:
    _OPERATORS = {
        ')': -1,
        '(': 0,
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3,
    }

    def __init__(self, string_expression):
        self._expression_stack = Stack()

        self._parsing_string_expression(string_expression)

    def _parsing_string_expression(self, string_expression):
        operators_stack = Stack()

        for element in string_expression:
            if element not in self._OPERATORS:
                self._expression_stack.add(element)
            elif element == ')':
                while True:
                    temp_element = operators_stack.get()
                    if temp_element == '(':
                        break
                    else:
                        self._expression_stack.add(temp_element)
            elif element == '(':
                operators_stack.add(element)
            elif self._OPERATORS.get(operators_stack.look_on_top(), -1) > self._OPERATORS[element]:
                self._expression_stack.add(operators_stack.get())
                operators_stack.add(element)
            else:
                operators_stack.add(element)
        while operators_stack.is_not_empty():
            self._expression_stack.add(operators_stack.get())
        print(operators_stack, self._expression_stack)

    def evaluate(self):
        buffer = Stack()

        while self._expression_stack.is_not_empty():
            element = self._expression_stack.get_from_bottom()
            if element in self._OPERATORS:
                left_number = buffer.get()
                right_number = buffer.get()
                buffer.add(eval(f"{left_number}{element}{right_number}"))
            else:
                buffer.add(element)
        return buffer.get()


e = Expression('(5+2)*(2+(1+1))')

print(e.evaluate())

