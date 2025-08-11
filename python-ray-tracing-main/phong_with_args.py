import math
import numpy as np
from entidades import Esfera, Plane, Mesh
from vectors import Ponto, Vetor
from fonte_de_luz import Luz
from ray import Ray

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

def refract(I, N, eta):
    cos_i = -np.dot(I, N)
    k = 1.0 - eta**2 * (1.0 - cos_i**2)
    if k < 0:
        return None
    else:
        return eta * I + (eta * cos_i - np.sqrt(k)) * N

def phong(entidade, luzes, ponto_intersec, camera_position, entidades, profundidade_reflexao, profundidade_refracao):
    if profundidade_reflexao >= 5 or profundidade_refracao >= 5:
        return [0, 0, 0]

    Ia = np.array([50.0, 50.0, 50.0])
    V = camera_position.__sub__(ponto_intersec).__normalize__()
    V_np = np.array([V.x, V.y, V.z])
    I = -V_np

    # --- LÓGICA DE CÁLCULO DA NORMAL (COM RELIEF MAPPING) ---
    if isinstance(entidade, Plane) and entidade.use_relief:
        delta = ponto_intersec - entidade.point
        u = delta.__mul__(entidade.tangent)
        v = delta.__mul__(entidade.bitangent)
        eps = 0.001
        
        h_base = entidade.get_height(u, v)
        h_u = entidade.get_height(u + eps, v)
        h_v = entidade.get_height(u, v + eps)
        
        dp_du = entidade.tangent + entidade.normal.__mul_escalar__((h_u - h_base) / eps * entidade.relief_scale)
        dp_dv = entidade.bitangent + entidade.normal.__mul_escalar__((h_v - h_base) / eps * entidade.relief_scale)
        
        N_vetor = dp_du.__cross__(dp_dv).__normalize__()
    else:
        # Lógica de normal padrão para outros objetos
        if isinstance(entidade, Esfera):
            N_vetor = ponto_intersec.__sub__(entidade.center).__normalize__()
        elif isinstance(entidade, Plane):
            N_vetor = entidade.normal
        else: 
            N_vetor = entidade.normal_to_intersection_point.__normalize__()
            
    N = np.array([N_vetor.x, N_vetor.y, N_vetor.z])
    # -----------------------------------------------------------------

    entidade.color = np.array(entidade.color)
    
    is_dielectric = entidade.k_difuso == 0 and entidade.k_ambiental == 0 and entidade.k_refracao > 0
    
    if is_dielectric:
        cos_i = np.dot(I, N)
        n1, n2 = 1.0, entidade.indice_refracao
        if cos_i < 0:
            n1, n2 = n2, 1.0
        
        r0 = ((n1 - n2) / (n1 + n2))**2
        reflectance = r0 + (1 - r0) * ((1 - abs(cos_i)) ** 5)
        refractance = 1.0 - reflectance
        
        cor_refratada = np.array([0.,0.,0.])
        ocorreu_TIR = False

        if refractance > 0:
            eta = n1 / n2
            normal_calculo = N if cos_i > 0 else -N
            direcao_refratada = refract(I, normal_calculo, eta)
            
            if direcao_refratada is not None:
                epsilon = 1e-4
                offset_vetor = Vetor(*normal_calculo).__mul_escalar__(-epsilon)
                origem_refratada = ponto_intersec + offset_vetor
                raio_refratado = Ray(origem_refratada, Vetor(*direcao_refratada))
                cor = find_closest_intersection(raio_refratado, entidades, luzes, profundidade_reflexao, profundidade_refracao + 1)
                if cor: cor_refratada = np.array(cor)
            else:
                ocorreu_TIR = True

        cor_refletida = np.array([0.,0.,0.])
        if reflectance > 0 or ocorreu_TIR:
            epsilon = 1e-4
            direcao_refletida = I - (2 * cos_i * N)
            origem_refletida = ponto_intersec + Vetor(*N).__mul_escalar__(epsilon)
            raio_refletido = Ray(origem_refletida, Vetor(*direcao_refletida))
            new_targets = [t for t in entidades if t is not entidade]
            cor = find_closest_intersection(raio_refletido, new_targets, luzes, profundidade_reflexao + 1, profundidade_refracao)
            if cor: cor_refletida = np.array(cor)
        
        cor_especular = np.array([0.0, 0.0, 0.0])
        for luz in luzes:
            L_np = np.array(list(Ponto(luz.x, luz.y, luz.z).__sub__(ponto_intersec).__normalize__()))
            N_dot_L = clamp(0, np.dot(N, L_np), 1)
            R = (2 * N * N_dot_L) - L_np
            R_dot_V = clamp(0, np.dot(R, V_np), 1)
            cor_especular += np.array(luz.I) * entidade.k_especular * (R_dot_V**entidade.n_rugosidade)

        if ocorreu_TIR:
            cor_final_np = cor_refletida + cor_especular
        else:
            cor_final_np = (cor_refratada * entidade.color * refractance) + (cor_refletida * reflectance) + cor_especular
    
    else:
        cor_local = Ia * entidade.k_ambiental * entidade.color
        for luz in luzes:
            L = Ponto(luz.x, luz.y, luz.z).__sub__(ponto_intersec).__normalize__()
            L_np = np.array([L.x, L.y, L.z])
            em_sombra=False
            for obj_sombra in entidades:
                is_transparent_shadow = hasattr(obj_sombra, 'k_difuso') and obj_sombra.k_difuso == 0 and obj_sombra.k_ambiental == 0
                if is_transparent_shadow:
                    continue
                if obj_sombra is not entidade:
                    epsilon_sombra = 1e-4
                    origem_sombra = ponto_intersec + Vetor(*N).__mul_escalar__(epsilon_sombra)
                    raio_sombra = Ray(origem_sombra, L)
                    distancia_luz = ponto_intersec.__distance__(Ponto(luz.x, luz.y, luz.z))
                    intersecao_sombra = obj_sombra.__intersect_line__(tuple(origem_sombra), tuple(raio_sombra.direction))
                    if intersecao_sombra:
                        ponto_sombra = Ponto(*intersecao_sombra)
                        if origem_sombra.__distance__(ponto_sombra) < distancia_luz:
                            em_sombra = True; break
            
            if not em_sombra:
                N_dot_L = clamp(0, np.dot(N, L_np), 1)
                I_difusa = np.array(luz.I) * entidade.color * entidade.k_difuso * N_dot_L
                R = (2 * N * N_dot_L) - L_np; R_dot_V = clamp(0, np.dot(R, V_np), 1)
                I_especular = np.array(luz.I) * entidade.k_especular * (R_dot_V**entidade.n_rugosidade)
                cor_local += I_difusa + I_especular
        
        cor_refletida = np.array([0.0, 0.0, 0.0])
        if entidade.k_reflexao > 0:
            epsilon = 1e-4
            direcao_refletida = I - (2 * np.dot(I, N) * N)
            origem_refletida = ponto_intersec + Vetor(*N).__mul_escalar__(epsilon)
            raio_refletido = Ray(origem_refletida, Vetor(*direcao_refletida))
            new_targets = [t for t in entidades if t is not entidade]
            cor = find_closest_intersection(raio_refletido, new_targets, luzes, profundidade_reflexao + 1, profundidade_refracao)
            if cor: cor_refletida = np.array(cor)
        
        cor_final_np = cor_local * (1.0 - entidade.k_reflexao) + cor_refletida * entidade.k_reflexao

    return [clamp(0, int(c), 255) for c in cor_final_np]

def find_closest_intersection(ray, entidades, luzes, profundidade_reflexao, profundidade_refracao):
    min_distance = float("inf")
    entidade_atingida, ponto_de_intersecao = None, None
    for entidade in entidades:
        origem_tupla = (ray.origin.x, ray.origin.y, ray.origin.z)
        direcao_tupla = (ray.direction.x, ray.direction.y, ray.direction.z)
        intersection = entidade.__intersect_line__(origem_tupla, direcao_tupla)
        if intersection:
            p_intersec = Ponto(intersection[0], intersection[1], intersection[2])
            distance = ray.origin.__distance__(p_intersec)
            if distance < min_distance and distance > 1e-4:
                min_distance, entidade_atingida, ponto_de_intersecao = distance, entidade, p_intersec
    if entidade_atingida:
        return phong(entidade_atingida, luzes, ponto_de_intersecao, ray.origin, entidades, profundidade_reflexao, profundidade_refracao)
    return [0, 0, 0]