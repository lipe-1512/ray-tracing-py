import math
from vectors import Ponto, Vetor

class Esfera: #Representa uma esfera 3D
    def __init__( 
        self,
        center, 
        radius, 
        color,
        k_difuso=0.0, k_especular=0.0, k_ambiental=0.0, k_reflexao=0.0,
        k_transmissao=0.0, n_rugosidade=0.0, k_refracao=0.0, indice_refracao=0.0): 
        
        self.center = center if isinstance(center, Ponto) else Ponto(*center)
        self.radius = radius 
        self.color = color
        self.k_difuso, self.k_especular, self.k_ambiental = k_difuso, k_especular, k_ambiental
        self.k_reflexao, self.k_transmissao, self.n_rugosidade = k_reflexao, k_transmissao, n_rugosidade
        self.k_refracao, self.indice_refracao = k_refracao, indice_refracao

    def __intersect_line__(self, line_point, line_vector):
        lp = Ponto(*line_point); lv = Vetor(*line_vector)
        oc = lp - self.center
        
        a = lv.__mul__(lv)
        b = 2 * oc.__mul__(lv)
        c = oc.__mul__(oc) - self.radius**2
        
        discriminant = b**2 - 4 * a * c
        if discriminant <= 0:
            return None
        
        t1 = (-b + discriminant**0.5) / (2 * a)
        t2 = (-b - discriminant**0.5) / (2 * a)
        
        epsilon = 0.0001
        t_min = min(t1, t2)
        t_max = max(t1, t2)

        if t_min > epsilon:
            p_int = lp + lv.__mul_escalar__(t_min)
            return (p_int.x, p_int.y, p_int.z)
        if t_max > epsilon:
            p_int = lp + lv.__mul_escalar__(t_max)
            return (p_int.x, p_int.y, p_int.z)
        return None
    
class Plane:
    def __init__(
        self, 
        point, 
        normal, 
        color,
        k_difuso=0.0, k_especular=0.0, k_ambiental=0.0,
        k_transmissao=0.0, n_rugosidade=0.0, k_reflexao=0.0,
        k_refracao=0.0, indice_refracao=0.0,
        # Parâmetros do Relief Mapping
        use_relief=False, relief_scale=0.5, uv_scale=1.0):
        
        self.point = Ponto(*point) if isinstance(point, tuple) else point
        self.normal = (Vetor(*normal) if isinstance(normal, tuple) else normal).__normalize__()
        self.color = color
        self.k_difuso, self.k_especular, self.k_ambiental = k_difuso, k_especular, k_ambiental
        self.k_reflexao, self.k_transmissao, self.n_rugosidade = k_reflexao, k_transmissao, n_rugosidade
        self.k_refracao, self.indice_refracao = k_refracao, indice_refracao
        self.use_relief, self.relief_scale, self.uv_scale = use_relief, relief_scale, uv_scale
        
        # Cria base Tangente/Bitangente robusta para qualquer orientação de plano
        if abs(self.normal.x) > abs(self.normal.y):
            self.tangent = Vetor(self.normal.z, 0, -self.normal.x).__normalize__()
        else:
            self.tangent = Vetor(0, -self.normal.z, self.normal.y).__normalize__()
        self.bitangent = self.normal.__cross__(self.tangent)

    def get_height(self, u, v):
        """Mapa de altura procedural para o relevo (ondas)."""
        return 0.5 + 0.5 * math.sin(u * self.uv_scale * 10) * math.cos(v * self.uv_scale * 10)

    def __intersect_line__(self, line_point, line_vector):
            lp = Ponto(*line_point); lv = Vetor(*line_vector)
            denominator = self.normal.__mul__(lv)
            
            if abs(denominator) < 1e-6:
                return None
            
            d = self.point - lp
            t = d.__mul__(self.normal) / denominator

            if t <= 1e-4:
                return None

            P = lp + lv.__mul_escalar__(t)

            if not self.use_relief:
                return (P.x, P.y, P.z)

            # Relief Mapping Simples: desloca o ponto de interseção
            delta = P - self.point
            u = delta.__mul__(self.tangent)
            v = delta.__mul__(self.bitangent)

            height = self.get_height(u, v) * self.relief_scale
            displaced_point = P + self.normal.__mul_escalar__(height)
            return (displaced_point.x, displaced_point.y, displaced_point.z)

class Mesh:
    def __init__(
        self,
        triangle_quantity: int,
        vertices_quantity: int,
        vertices: list[Ponto],
        triangle_tuple_vertices: list[tuple[int, int, int]],
        triangle_normals: list,
        vertex_normals: list,
        color,
        k_difuso=0.0, k_especular=0.0, k_ambiental=0.0, k_reflexao=0.0,
        k_transmissao=0.0, n_rugosidade=0.0, k_refracao=0.0,                
        indice_refracao=0.0, normal_to_intersection_point=None):

        self.triangle_quantity = triangle_quantity
        self.vertices_quantity = vertices_quantity
        self.vertices = vertices
        self.triangle_tuple_vertices = triangle_tuple_vertices
        self.triangle_normals = triangle_normals
        self.vertex_normals = vertex_normals
        self.normal_to_intersection_point = None
        self.color = color
        self.k_difuso, self.k_especular, self.k_ambiental = k_difuso, k_especular, k_ambiental
        self.k_reflexao, self.k_transmissao, self.n_rugosidade = k_reflexao, k_transmissao, n_rugosidade
        self.k_refracao, self.indice_refracao = k_refracao, indice_refracao

    def __point_in_triangle__(self, point, triangle_vertices):
        v0 = triangle_vertices[2].__sub__(triangle_vertices[0])
        v1 = triangle_vertices[1].__sub__(triangle_vertices[0])
        v2 = point.__sub__(triangle_vertices[0])

        d00 = v0.__mul__(v0)
        d01 = v0.__mul__(v1)
        d11 = v1.__mul__(v1)
        d20 = v2.__mul__(v0)
        d21 = v2.__mul__(v1)
        
        denom = d00 * d11 - d01 * d01
        
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1.0 - v - w

        return (v >= 0) and (w >= 0) and (u >= 0)

    def __intersect_line__(self, line_point, line_vector):
        for index, triangle in enumerate(self.triangle_tuple_vertices):
            triangle_vertices = [self.vertices[i] for i in triangle]
            triangle_normal = self.triangle_normals[index]

            plane = Plane(triangle_vertices[0], triangle_normal, self.color)
            intersection_tuple = plane.__intersect_line__(line_point, line_vector)

            if intersection_tuple is not None:
                intersection_point = Ponto(*intersection_tuple)
                if self.__point_in_triangle__(intersection_point, triangle_vertices):
                    self.normal_to_intersection_point = triangle_normal
                    return (intersection_point.x, intersection_point.y, intersection_point.z)
        return None