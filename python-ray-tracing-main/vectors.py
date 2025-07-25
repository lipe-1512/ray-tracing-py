import math 

class Ponto:
    """Representa um ponto 3D"""

    def __init__(self, x, y, z): #inicialização do ponto com as três coordenadas.
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __add__(self, p):
        return Ponto(self.x + p.x, self.y + p.y, self.z + p.z)

    def __sub__(self, p):
        vetor_resultado = Vetor(self.x - p.x, self.y - p.y, self.z - p.z)
        return vetor_resultado

    def __distance__(self, p): #distância euclidiana entre dois pontos no espaço na forma raiz((x2 - x1)² + (y2 - y1)² + (z2 - z1)²)
        return ((self.x - p.x) ** 2 + (self.y - p.y) ** 2 + (self.z - p.z) ** 2) ** 0.5

    def __print__(self): #mostra as coordenadas do ponto no formato (x, y, z).
        print(f"({self.x}, {self.y}, {self.z})")


class Vetor(Ponto):
    """Representa um vetor"""

    def __add__(self, v):
        """A soma de dois vetores resulta em um novo vetor."""
        return Vetor(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v):
        """A subtração de dois vetores resulta em um novo vetor."""
        return Vetor(self.x - v.x, self.y - v.y, self.z - v.z)

    def __mul__(self, p): #prod interno 
        return self.x * p.x + self.y * p.y + self.z * p.z

    def __mul_escalar__(self, escalar): #mult escalar 
        return Vetor(self.x * escalar, self.y * escalar, self.z * escalar)

    def __cross__(self, p): #prod vetorial
        return Vetor( #este é perpendicular aos param
            self.y * p.z - self.z * p.y,
            self.z * p.x - self.x * p.z,
            self.x * p.y - self.y * p.x,
        )

    def __magnitude__(self): #seu módulo sera dado pela raiz de suas coordenadas
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def __normalize__(self): #divide seu modulo por ele mesmo para normalizar (tornar tam 1 mantendo todo o resto)

        if self.__magnitude__() == 0: #proteção da div/0 com vetor nulo
            return Vetor(0, 0, 0)
        
        return Vetor(
            self.x / self.__magnitude__(),
            self.y / self.__magnitude__(),
            self.z / self.__magnitude__(),
        )

    def __angle__(self, p: "Vetor"): #o angulo entre os vetores em rad
        return math.acos((self * p) / (self.__magnitude__() * p.__magnitude__()))
