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
        source = """user = {"nombre": "Juan", "edad": 30}
print(user["nombre"])

user["email"] = "juan@mail.com"

for k, v in user.items():
    print(k, v)

for k in user.keys():
    print(k)

for v in user.values():
    print(v)

copia = user.copy()
"""

    go_code = translate(source)
    print(go_code)
