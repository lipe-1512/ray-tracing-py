
from vectors import Ponto 

class Esfera: #Representa uma esfera 3D
    
    # definição da esfera e seus parametros, adicionando os coeficientes do material para a Terceira Entrega
    def __init__( 
        self,
        center, 
        radius, 
        color,
        k_difuso=0.0,  # Coeficiente difuso (>= 0 e <= 1)
        k_especular=0.0,  # Coeficiente especular (>= 0 e <= 1)
        k_ambiental=0.0,  # Coeficiente ambiental (>= 0 e <= 1)
        k_reflexao=0.0,  # Coeficiente de reflexão (>= 0 e <= 1)
        k_transmissao=0.0,  # Coeficiente de transmissão (>= 0 e <= 1)
        n_rugosidade=0.0,  # Coeficiente de rugosidade (> 0)
        k_refracao=0.0,               
        indice_refracao=0.0,          
        ): 
        # inicializando a esfera
        self.center = center 
        self.radius = radius 
        self.color = color
        self.k_difuso = k_difuso  
        self.k_especular = k_especular  
        self.k_ambiental = k_ambiental  
        self.k_reflexao = k_reflexao  
        self.k_transmissao = k_transmissao  
        self.n_rugosidade = n_rugosidade
        self.k_refracao = k_refracao       
        self.indice_refracao = indice_refracao     

    def __get_normal_vector_to_intersection_point__(self, intersection_point):
        """
        Calcula o vetor normal à superfície da esfera no ponto de interseção fornecido, que
        é perpendicular à superfície da esfera no ponto de interseção e aponta para fora do centro da esfera.
        """
        return [
            intersection_point.x - self.center.x, # Componente x do vetor normal no ponto de interseção
            intersection_point.y - self.center.y, # Componente y do vetor normal no ponto de interseção
            intersection_point.z - self.center.z, # Componente z do vetor normal no ponto de interseção
        ]
    
    def __intersect_line__(self, line_point, line_vector): #determina se um raio interceptou a esfera, e retorna o ponto de interseção mais próximo da câmera ou seja resolve a equação do 2º grau: a·t² + b·t + c = 0

        a = sum(i * j for i, j in zip(line_vector, line_vector)) #produto escalar do vetor com ele mesmo: |v|² = v·v = x² + y² + z²

        b = 2 * sum( #b é o dobro do produto escalar entre o vetor direção do raio e o vetor que vai do centro da esfera até a origem do raio
            i * j
            for i, j in zip(
                line_vector, (p - c for p, c in zip(line_point, self.center))
            )
        )

        #diferença entre o quadrado da distância do ponto inicial ao centro da esfera e o quadrado do raio. Indica se o ponto está dentro (-), na superfície (0) ou fora (+) da esfera.
        c = sum((p - c) ** 2 for p, c in zip(line_point, self.center)) - self.radius**2

        discriminant = b**2 - 4 * a * c #delta que indica se a eq quadrática tem solução real, ou seja se o raio intersecta a esfera.

        if discriminant <= 0: #se delta <= 0 não há interseção real
            return None
        
        #se delta > 0 ent calculamos as possiveis soluções
        t1 = (-b + discriminant**0.5) / (2 * a)
        t2 = (-b - discriminant**0.5) / (2 * a)

        
        # Lógica mais robusta para encontrar a interseção correta e na frente da câmera.
        epsilon = 0.0001
        
        # Pega a menor e a maior solução
        t_min = min(t1, t2)
        t_max = max(t1, t2)

        # Verifica se a menor solução (mais próxima) é válida (na frente do raio)
        if t_min > epsilon:
            return tuple(p + t_min * v for p, v in zip(line_point, line_vector))
        
        # Se a mais próxima não for válida, verifica a mais distante (caso o raio comece de dentro da esfera)
        if t_max > epsilon:
            return tuple(p + t_max * v for p, v in zip(line_point, line_vector))
        
        # Se nenhuma for válida, não há interseção.
        return None
    
class Plane: #representa um plano 3D
    # definição do plano e seus parametros, adicionando os coeficientes do material para a Terceira Entrega
    def __init__(
        self, 
        point, 
        normal, 
        color,
        k_difuso=0.0,  # Coeficiente difuso (>= 0 e <= 1)
        k_especular=0.0,  # Coeficiente especular (>= 0 e <= 1)
        k_ambiental=0.0,  # Coeficiente ambiental (>= 0 e <= 1)
        k_transmissao=0.0,  # Coeficiente de transmissão (>= 0 e <= 1)
        n_rugosidade=0.0,  # Coeficiente de rugosidade (> 0)
        k_reflexao=0.0,  # Coeficiente de reflexão (>= 0 e <= 1)
        k_refracao=0.0,                
        indice_refracao=0.0,           
        ): 
        # inicializando o plano
        self.point = point
        self.normal = normal
        self.color = color
        self.k_difuso = k_difuso
        self.k_especular = k_especular
        self.k_ambiental = k_ambiental
        self.k_reflexao = k_reflexao
        self.k_transmissao = k_transmissao
        self.n_rugosidade = n_rugosidade
        self.k_refracao = k_refracao       
        self.indice_refracao = indice_refracao     
#-----------------------------------------------------------------------------
    
    def __intersect_line__(self, line_point, line_vector): #calcula o ponto de interseção entre uma linha (definida por um ponto e um vetor direção) e o plano
            
            d = tuple(p - lp for p, lp in zip(self.point, line_point)) #vetor d que vai do ponto da linha até o ponto do plano 
            
            denominator = sum(n * lv for n, lv in zip(self.normal, line_vector)) #prod escalar entre o vetor normal do plano e o vetor direção da linha 

            if denominator == 0: #produto escalar zero a linha é paralela ao plano e não há interseção
                return None
            
            t = sum(n * dp for n, dp in zip(self.normal, d)) / denominator #calcula o "quanto andar" (parâmetro t) para alcançar o plano ao longo do vetor da linha

            # <<< MUDANÇA AQUI >>>
            # Verifica se a interseção ocorre NA FRENTE do raio. Se t for negativo, a interseção está atrás.
            if t > 0.0001:
                return tuple(lp + t * lv for lp, lv in zip(line_point, line_vector)) #achar as coordenadas exatas do ponto de interseção
            
            return None # Se t for negativo ou muito pequeno, não há interseção válida.

#----------------------------SEGUNDA ENTREGA ADICIONAIS--------------------------------------------------------------------------

class Mesh: #representa uma malha
    # definição da malha e seus parametros, adicionando os coeficientes do material para a Terceira Entrega
    def __init__(
        self,
        triangle_quantity: int,
        vertices_quantity: int,
        vertices: list[Ponto],
        triangle_tuple_vertices: list[tuple[int, int, int]],
        triangle_normals: list,
        vertex_normals: list,
        color,
        k_difuso=0.0,  # Coeficiente difuso (>= 0 e <= 1)
        k_especular=0.0,  # Coeficiente especular (>= 0 e <= 1)
        k_ambiental=0.0,  # Coeficiente ambiental (>= 0 e <= 1)
        k_reflexao=0.0,  # Coeficiente de reflexão (>= 0 e <= 1)
        k_transmissao=0.0,  # Coeficiente de transmissão (>= 0 e <= 1)
        n_rugosidade=0.0,  # Coeficiente de rugosidade (> 0)
        k_refracao=0.0,                
        indice_refracao=0.0,           
        normal_to_intersection_point=None,  # Vetor normal no ponto de interseção
    ):
        self.triangle_quantity = triangle_quantity
        self.vertices_quantity = vertices_quantity
        self.vertices = vertices
        self.triangle_tuple_vertices = triangle_tuple_vertices #lista de tuplas com índices de vértices que formam os triângulos
        self.triangle_normals = triangle_normals #uma normal (vetor perpendicular) para cada triângulo
        self.vertex_normals = vertex_normals
        self.normal_to_intersection_point = None
        self.k_difuso = k_difuso
        self.k_especular = k_especular
        self.k_ambiental = k_ambiental
        self.k_reflexao = k_reflexao
        self.k_transmissao = k_transmissao
        self.n_rugosidade = n_rugosidade
        self.k_refracao = k_refracao       
        self.indice_refracao = indice_refracao     

        self.color = color
        self.k_difuso = k_difuso
        self.k_especular = k_especular
        self.n_rugosidade = n_rugosidade
        self.k_ambiental = k_ambiental
        self.normal_to_intersection_point = normal_to_intersection_point

    def __point_in_triangle__(self, point, triangle_vertices): #Verifica se um ponto esta dentro de um triangulo usando coord baricentrica

        #Cria vetores entre os vértices do triângulo
        v0 = triangle_vertices[2].__sub__(triangle_vertices[0])  # C - A
        v1 = triangle_vertices[1].__sub__(triangle_vertices[0])  # B - A
        v2 = point.__sub__(triangle_vertices[0])                 # P - A sendo P o ponto que quero testar


        #produtos escalares p/ sistema linear dizer quanto o vetor do ponto "aponta" na direção de cada lado
        d00 = v0.__mul__(v0)      #AC ⋅ AC
        d01 = v0.__mul__(v1)      #AC ⋅ AB
        d11 = v1.__mul__(v1)      #AB ⋅ AB
        d20 = v2.__mul__(v0)      #AP ⋅ AC
        d21 = v2.__mul__(v1)      #AP ⋅ AB

        #denominador da equação baricêntrica
        denom = d00 * d11 - d01 * d01

        #resolve para as coordenadas baricêntricas v e w
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1.0 - v - w

        return (v >= 0) and (w >= 0) and (u >= 0) #Se são n-negativos ent assumimos q o ponto está dentro/borda do triângulo

    def __intersect_line__(self, line_point, line_vector): #Calcula a interseção de o ponto de interseção entre a malha e uma linha (para pintar o pixel)
        for index, triangle in enumerate(self.triangle_tuple_vertices):

            triangle_vertices = [self.vertices[i] for i in triangle] #pego os vertices de cada tringulo da malha
            triangle_normal = self.triangle_normals[index]

            plane = Plane(triangle_vertices[0], triangle_normal, self.color) #defino um plano no triângulo (dentro dele)

            intersection_point = plane.__intersect_line__(line_point, line_vector) #vejo se tem interseção do raio com o plano

            if intersection_point is not None:
                intersection_point = Ponto(  #se tiver converto p ponto
                    intersection_point[0], intersection_point[1], intersection_point[2]
                )
                #vê se o ponto está dentro do triângulo e o devolve caso sim
                if self.__point_in_triangle__(intersection_point, triangle_vertices):
                    self.normal_to_intersection_point = triangle_normal # normal do triângulo que foi atingido
                    return (
                        intersection_point.x,
                        intersection_point.y,
                        intersection_point.z,
                    )
        return None