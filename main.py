import sys
sys.path.insert(0, './generated')

from antlr4 import *
from generated.Python3Lexer import Python3Lexer
from generated.Python3Parser import Python3Parser
from translator.visitor import PythonToGoVisitor


def translate(source: str) -> str:
    input_stream = InputStream(source)
    lexer        = Python3Lexer(input_stream)
    stream       = CommonTokenStream(lexer)
    parser       = Python3Parser(stream)
    tree         = parser.file_input()

    visitor = PythonToGoVisitor()
    return visitor.visit(tree)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            source = f.read()
    else:
        source = """# Bug 1: in con strings
nombre = "Julian"
if "ul" in nombre:
    print("substring OK")

words = ["hola", "mundo"]
if "hola" in words:
    print("lista OK")

# Bug 2: unpacking de slice
point = [10, 20]
x, y = point
print(x, y)

# Bug 3: declared_vars scope entre funciones
def foo():
    z = 1
    z = 2
    return z

def bar():
    z = 99
    return z

# Bug 4: try/except/raise
try:
    x = int("abc")
except ValueError as e:
    print("error de conversion")

# Bug 5: clases
class Animal:
    def __init__(self, nombre, sonido):
        self.nombre = nombre
        self.sonido = sonido

    def hablar(self):
        print(f"{self.nombre} dice {self.sonido}")

a = Animal("Perro", "Guau")
a.hablar()

# Bug 6: match/case
val = 2
match val:
    case 1:
        print("uno")
    case 2:
        print("dos")
    case _:
        print("otro")
"""

    go_code = translate(source)
    print(go_code)
