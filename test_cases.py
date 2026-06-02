"""
Casos de prueba para el traductor Python → Go.
Cada caso es un dict con:
  - name:   nombre del caso
  - source: código Python a traducir
"""

TEST_CASES = [

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Operadores de asignación
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "assign_operators",
        "source": """\
x = 10
x += 3
x -= 1
x *= 2
x /= 4
x //= 3
x **= 2
x %= 5
print(x)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Operadores aritméticos
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "arithmetic_operators",
        "source": """\
a = 7 + 3
b = 7 - 3
c = 7 * 3
d = 7 / 3
e = 7 // 3
f = 7 % 3
g = 2 ** 8
print(a, b, c, d, e, f, g)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Operadores booleanos y relacionales con precedencia
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "boolean_relational_operators",
        "source": """\
a = True
b = False
c = not a
d = a and b
e = a or b
f = 3 < 5
g = 3 > 5
h = 3 <= 3
i = 3 >= 4
j = 3 == 3
k = 3 != 4
result = (1 + 2 * 3 > 4) and not (5 <= 4 or 6 == 7)
print(c, d, e, f, g, h, i, j, k, result)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Comentarios de una línea y multilínea
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "comments",
        "source": """\
# Este es un comentario de una línea
x = 1  # comentario inline

'''
Este es un comentario
multilínea con triple comilla simple
'''

\"\"\"
También multilínea
con triple comilla doble
\"\"\"

print(x)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Strings: comilla simple, doble y triple
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "strings",
        "source": """\
s1 = 'hola mundo'
s2 = "hello world"
s3 = '''string
multilínea
triple simple'''
s4 = \"\"\"otro string
multilínea
triple doble\"\"\"
print(s1, s2, s3, s4)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Operaciones con strings (* y +)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "string_operations",
        "source": """\
s = "hola"
t = s + " mundo"
r = s * 3
print(t, r)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 7. print: varargs, sep, end, f-strings
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "print_variants",
        "source": """\
nombre = "Julian"
edad = 25
print("hola", "mundo")
print("a", "b", "c", sep="-")
print("sin salto", end="")
print(f"Me llamo {nombre} y tengo {edad} años")
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 8. input
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "input_basic",
        "source": """\
nombre = input("¿Cómo te llamas? ")
print("Hola,", nombre)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 9. len para listas y strings
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "len_usage",
        "source": """\
s = "hola mundo"
lst = [1, 2, 3, 4, 5]
print(len(s))
print(len(lst))
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 10. Slicing: parcial, total, índices negativos
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "slicing",
        "source": """\
lst = [10, 20, 30, 40, 50]
s = "abcdef"
print(lst[1:3])
print(lst[:3])
print(lst[2:])
print(lst[:])
print(lst[-1])
print(lst[-2])
print(s[1:4])
print(s[::2])
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 11. List comprehension (simple y con condición)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "list_comprehension",
        "source": """\
cuadrados = [x * x for x in range(5)]
pares = [x for x in range(10) if x % 2 == 0]
print(cuadrados)
print(pares)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 12. List comprehension anidada
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "nested_list_comprehension",
        "source": """\
matriz = [[i * j for j in range(1, 4)] for i in range(1, 4)]
print(matriz)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 13. Append de listas con + y .append()
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "list_append",
        "source": """\
a = [1, 2, 3]
b = a + [4, 5]
a.append(6)
print(a)
print(b)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 14. Listas anidadas
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "nested_lists",
        "source": """\
matriz = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(matriz[0][1])
print(matriz[2][2])
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 15. Funciones básicas
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "functions_basic",
        "source": """\
def suma(a, b):
    return a + b

def saludar(nombre):
    print("Hola,", nombre)

resultado = suma(3, 4)
saludar("mundo")
print(resultado)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 16. Funciones con valor por defecto y *args
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "functions_defaults_args",
        "source": """\
def potencia(base, exp=2):
    return base ** exp

def suma_todos(*nums):
    total = 0
    for n in nums:
        total += n
    return total

print(potencia(3))
print(potencia(2, 10))
print(suma_todos(1, 2, 3, 4, 5))
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 17. Bucle while
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "while_loop",
        "source": """\
n = 0
while n < 5:
    print(n)
    n += 1
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 18. Bucle for genérico con break y continue
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "for_break_continue",
        "source": """\
for i in range(10):
    if i == 3:
        continue
    if i == 7:
        break
    print(i)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 19. Condicionales if / elif / else
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "conditionals",
        "source": """\
x = 42
if x < 0:
    print("negativo")
elif x == 0:
    print("cero")
elif x < 10:
    print("pequeño")
else:
    print("grande")
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 20. Asignación múltiple (a, b = 0, 1) y swap
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "multiple_assignment",
        "source": """\
a, b = 0, 1
print(a, b)
a, b = b, a
print(a, b)
x, y, z = 10, 20, 30
print(x, y, z)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 21. for w in words / if word in words
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "for_in_and_in_operator",
        "source": """\
words = ["hola", "mundo", "Python"]
for w in words:
    print(w)

if "Python" in words:
    print("encontrado")

nombre = "Julian"
if "ul" in nombre:
    print("substring encontrado")
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 22. Diccionarios y métodos básicos
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "dictionaries",
        "source": """\
users = {"alice": 30, "bob": 25, "carol": 35}
print(users["alice"])
users["dave"] = 28

for k, v in users.items():
    print(k, v)

for k in users.keys():
    print(k)

copia = users.copy()
print(copia)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 23. range con start, stop y step
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "range_variants",
        "source": """\
for i in range(5):
    print(i)

for i in range(2, 8):
    print(i)

for i in range(0, 20, 3):
    print(i)

for i in range(10, 0, -2):
    print(i)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 24. enumerate
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "enumerate_usage",
        "source": """\
frutas = ["manzana", "pera", "uva"]
for i, fruta in enumerate(frutas):
    print(i, fruta)

for i, fruta in enumerate(frutas, start=1):
    print(i, fruta)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 25. Clases, objetos y métodos
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "classes_basic",
        "source": """\
class Rectangulo:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

    def area(self):
        return self.ancho * self.alto

    def perimetro(self):
        return 2 * (self.ancho + self.alto)

    def __str__(self):
        return f"Rectangulo({self.ancho}x{self.alto})"

r = Rectangulo(4, 5)
print(r.area())
print(r.perimetro())
print(r)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 26. Herencia en clases
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "classes_inheritance",
        "source": """\
class Animal:
    def __init__(self, nombre):
        self.nombre = nombre

    def hablar(self):
        print("...")

class Perro(Animal):
    def __init__(self, nombre):
        self.nombre = nombre

    def hablar(self):
        print(self.nombre, "dice: Guau!")

class Gato(Animal):
    def hablar(self):
        print(self.nombre, "dice: Miau!")

p = Perro("Rex")
p.hablar()
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 27. match / case (switch)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "match_case",
        "source": """\
val = 2
match val:
    case 1:
        print("uno")
    case 2:
        print("dos")
    case 3 | 4:
        print("tres o cuatro")
    case _:
        print("otro")

comando = "salir"
match comando:
    case "iniciar":
        print("iniciando")
    case "salir":
        print("saliendo")
    case _:
        print("comando desconocido")
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 28. Excepciones: try / except / raise
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "exceptions",
        "source": """\
try:
    x = int("abc")
except ValueError as e:
    print("error de conversion:", e)

try:
    resultado = 10 / 0
except ZeroDivisionError:
    print("division por cero")

def validar(n):
    if n < 0:
        raise ValueError("n no puede ser negativo")
    return n

try:
    validar(-1)
except ValueError as e:
    print("capturado:", e)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 29. try / except / finally
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "try_finally",
        "source": """\
try:
    x = int("42")
    print("parseado:", x)
except ValueError:
    print("error")
finally:
    print("bloque finally ejecutado")
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 30. Unpacking
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "unpacking",
        "source": """\
point = [10, 20]
x, y = point
print(x, y)

coordenadas = (1, 2, 3)
a, b, c = coordenadas
print(a, b, c)

primero, *resto = [1, 2, 3, 4, 5]
print(primero)
print(resto)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 31. Docstrings
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "docstrings",
        "source": """\
def calcular_area(base, altura):
    \"\"\"
    Calcula el área de un triángulo.

    Args:
        base: La base del triángulo.
        altura: La altura del triángulo.

    Returns:
        El área como float.
    \"\"\"
    return 0.5 * base * altura

print(calcular_area(4, 6))
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 32. Funciones lambda
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "lambdas",
        "source": """\
doble = lambda x: x * 2
suma = lambda a, b: a + b
identidad = lambda x: x

print(doble(5))
print(suma(3, 4))

numeros = [3, 1, 4, 1, 5, 9, 2, 6]
numeros.sort(key=lambda x: -x)
print(numeros)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 33. else en bucles for y while
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "loop_else",
        "source": """\
for i in range(5):
    if i == 10:
        break
else:
    print("for completado sin break")

n = 0
while n < 3:
    n += 1
else:
    print("while completado sin break")
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 34. Generadores con yield
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "generators",
        "source": """\
def contar(n):
    for i in range(n):
        yield i

for val in contar(5):
    print(val)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 35. Scope de variables entre funciones
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "function_scope",
        "source": """\
def foo():
    z = 1
    z = 2
    return z

def bar():
    z = 99
    return z

print(foo())
print(bar())
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 36. Referencias en listas (no copia)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "list_references",
        "source": """\
a = [1, 2, 3]
b = a
b.append(4)
print(a)
print(b)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 37. Función con retorno múltiple
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "multiple_return",
        "source": """\
def minmax(lista):
    return min(lista), max(lista)

mi, ma = minmax([3, 1, 4, 1, 5, 9, 2])
print(mi, ma)
""",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # 38. Combinación compleja (integración)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "integration_complex",
        "source": """\
class Pila:
    def __init__(self):
        self.datos = []

    def push(self, val):
        self.datos.append(val)

    def pop(self):
        if len(self.datos) == 0:
            raise ValueError("pila vacía")
        return self.datos[-1]

    def esta_vacia(self):
        return len(self.datos) == 0

p = Pila()
for i in range(1, 6):
    p.push(i)

try:
    while not p.esta_vacia():
        print(p.pop())
except ValueError as e:
    print("Error:", e)
""",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Runner mínimo
# ─────────────────────────────────────────────────────────────────────────────

import sys
sys.path.insert(0, './generated')

from antlr4 import InputStream, CommonTokenStream
from generated.Python3Lexer import Python3Lexer
from generated.Python3Parser import Python3Parser
from translator.visitor import PythonToGoVisitor


def translate(source: str) -> str:
    input_stream = InputStream(source)
    lexer  = Python3Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Python3Parser(stream)
    tree   = parser.file_input()
    visitor = PythonToGoVisitor()
    return visitor.visit(tree)


def run_tests(names=None):
    """
    Ejecuta los casos de prueba e imprime el Go generado.
    Si `names` es una lista de strings, solo ejecuta esos casos.
    """
    selected = TEST_CASES if not names else [t for t in TEST_CASES if t["name"] in names]

    passed = 0
    failed = 0
    for tc in selected:
        print(f"\n{'='*60}")
        print(f"TEST: {tc['name']}")
        print(f"{'='*60}")
        try:
            result = translate(tc["source"])
            print(result)
            passed += 1
        except Exception as ex:
            print(f"[ERROR] {ex}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Resultado: {passed} OK  |  {failed} ERRORES  |  total {passed+failed}")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Sin argumentos → ejecuta todos los casos.
    # Con argumentos → ejecuta solo los cases nombrados.
    # Ej: python test_cases.py assign_operators lambdas
    names = sys.argv[1:] or None
    run_tests(names)
