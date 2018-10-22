from pyparsing import nestedExpr


class Variable:
    # _name = None
    # _value = None

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __str__(self):
        return self._value


class Function:

    def __init__(self, name, value):
        self._name = name
        self._value = value

    @staticmethod
    def is_function(string):
        return True


class Computor:
    # _variables = None

    def __init__(self):
        self._simple_parser = nestedExpr()
        self._variables = set()

    def run(self):
        input_string = None

        while input_string != "q":
            input_string = input("> ")
            if Function.is_function(input_string):
                self._variables.add(Function())
            print(input_string)


if __name__ == '__main__':
    computor = Computor()
    computor.run()
