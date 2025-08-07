from vectors import Ponto, Vetor


class Ray:
    """Class Representing a Ray in 3D Space
    Args:
        origin, direction
    """

    def __init__(self, origin: "Ponto", direction: "Vetor"):
        """Initialize the Ray"""
        self.origin = origin
        self.direction = direction

    def __str__(self):
        """Return the string representation of the Ray"""
        return f"Ray({self.origin}, {self.direction})"

    def __repr__(self):
        """Return the string representation of the Ray"""
        return self.__str__()

    def get_point(self, t: float) -> "Ponto":
        """Return the point at t distance from the origin"""
        return self.origin + (self.direction.__mul_escalar__(t))

    def __add__(self, other: "Ray") -> "Ray":
        """Return the sum of two rays"""
        return Ray(
            self.origin.__add__(other.origin), self.direction.__add__(other.direction)
        )

    def __sub__(self, other: "Ray") -> "Ray":
        """Return the subtraction of two rays"""
        return Ray(
            self.origin.__sub__(other.origin), self.direction.__sub__(other.direction)
        )

    def __mul__(self, other: float) -> "Ray":
        """Return the multiplication of a ray by a scalar"""
        return Ray(self.origin.__mul__(other), self.direction.__mul__(other))

    def __truediv__(self, other: float) -> "Ray":
        """Return the division of a ray by a scalar"""
        return Ray(self.origin.__truediv__(other), self.direction.__truediv__(other))
