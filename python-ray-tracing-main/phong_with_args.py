import numpy as np
from entidades import Esfera, Plane, Mesh
from vectors import Ponto, Vetor
from fonte_de_luz import Luz
from ray import Ray

#função p/ garantir q/ um valor fique entre um min e max
def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

#aqui é a Lei de Snell p/ calcular o desvio do raio
def refract(I, N, eta):
    cos_i = -np.dot(I, N)
    k = 1.0 - eta**2 * (1.0 - cos_i**2)
    #se k < 0, deu reflexão interna total, não tem refração
    if k < 0:
        return None
    else:
        return eta * I + (eta * cos_i - np.sqrt(k)) * N

def phong(entidade, luzes, ponto_intersec, camera_position, entidades, profundidade_reflexao, profundidade_refracao):
    #limite de recursão p/ não travar em reflexos infinitos
    if profundidade_reflexao >= 5 or profundidade_refracao >= 5:
        return [0, 0, 0]

    #luz ambiente, uma claridade base na cena
    Ia = np.array([50.0, 50.0, 50.0])
    #V é o vetor p/ a camera, I é o raio incidente
    V = camera_position.__sub__(ponto_intersec).__normalize__()
    V = np.array([V.x, V.y, V.z])
    I = -V

    if isinstance(entidade, Esfera):
        N = ponto_intersec.__sub__(entidade.center).__normalize__()
    elif isinstance(entidade, Plane):
        N = entidade.normal.__normalize__()
    else: 
        N = entidade.normal_to_intersection_point.__normalize__()
    N = np.array([N.x, N.y, N.z])

    entidade.color = np.array(entidade.color)
    
    #LÓGICA PARA MATERIAIS DE VIDRO/TRANSPARENTES---------------------------------------------------------------
    
    is_dielectric = entidade.k_difuso == 0 and entidade.k_ambiental == 0 and entidade.k_refracao > 0 #checa se o material é tipo vidro (transparente)
    
    if is_dielectric:
        #se for vidro, entra na lógica de refração/reflexão
        #cosseno do angulo de incidencia
        cos_i = np.dot(I, N)
        n1, n2 = 1.0, entidade.indice_refracao
        #checa se o raio tá dentro do obj (saindo)
        if cos_i < 0:
            n1, n2 = n2, 1.0
        
        #efeito Fresnel: calc o qto de luz reflete vs refrata
        r0 = ((n1 - n2) / (n1 + n2))**2
        reflectance = r0 + (1 - r0) * ((1 - abs(cos_i)) ** 5)
        refractance = 1.0 - reflectance
        
        cor_refratada = np.array([0.,0.,0.])
        ocorreu_TIR = False

        #---------------Parte da Refração---------------
        #se a luz pode refratar...
        if refractance > 0:
            eta = n1 / n2
            normal_calculo = N if cos_i > 0 else -N
            #chama a func de Snell p/ desviar o raio
            direcao_refratada = refract(I, normal_calculo, eta)
            
            #se não deu reflexão total...
            if direcao_refratada is not None:
                epsilon = 1e-4
                offset_vetor = Vetor(normal_calculo[0], normal_calculo[1], normal_calculo[2]).__mul_escalar__(-epsilon)
                origem_refratada = ponto_intersec + offset_vetor
                #cria o novo raio q entrou no obj
                raio_refratado = Ray(origem_refratada, Vetor(direcao_refratada[0], direcao_refratada[1], direcao_refratada[2]))
                #recursão: lança o raio p/ ver o q tem dentro/atrás
                cor = find_closest_intersection(raio_refratado, entidades, luzes, profundidade_reflexao, profundidade_refracao + 1)
                if cor: cor_refratada = np.array(cor)
            else:
                #avisa q a luz foi 100% refletida
                ocorreu_TIR = True

        #--------------Parte da Reflexão---------------
        cor_refletida = np.array([0.,0.,0.])
        #se reflete algo ou se deu reflexão total...
        if reflectance > 0 or ocorreu_TIR:
            epsilon = 1e-4
            #calc a direção do raio refletido
            direcao_refletida = I - (2 * cos_i * N)
            origem_refletida = ponto_intersec + Vetor(N[0], N[1], N[2]).__mul_escalar__(epsilon)
            raio_refletido = Ray(origem_refletida, Vetor(direcao_refletida[0], direcao_refletida[1], direcao_refletida[2]))
            new_targets = [t for t in entidades if t is not entidade]
            cor = find_closest_intersection(raio_refletido, new_targets, luzes, profundidade_reflexao + 1, profundidade_refracao)
            if cor: cor_refletida = np.array(cor)
        
        #calc só o brilho do vidro
        cor_especular = np.array([0.0, 0.0, 0.0])
        for luz in luzes:
            L = Ponto(luz.x, luz.y, luz.z).__sub__(ponto_intersec).__normalize__(); L_np = np.array([L.x, L.y, L.z])
            N_dot_L = clamp(0, np.dot(N, L_np), 1); R = (2 * N * N_dot_L) - L_np; R_dot_V = clamp(0, np.dot(R, V), 1)
            cor_especular += np.array(luz.I) * entidade.k_especular * (R_dot_V**entidade.n_rugosidade)

        #se deu reflexão total, a cor é só reflexo + brilho
        if ocorreu_TIR:
            cor_final_np = cor_refletida + cor_especular
        else:
            #senão, mistura td: refração, reflexão e brilho
            cor_final_np = (cor_refratada * entidade.color * refractance) + (cor_refletida * reflectance) + cor_especular
    
    else:
        #LÓGICA PARA MATERIAIS OPACOS---------------------------------------------------------------
        #se for opaco, usa a lógica de iluminação padrão
        cor_local = Ia * entidade.k_ambiental * entidade.color
        #loop p/ cada fonte de luz na cena
        for luz in luzes:
            L = Ponto(luz.x, luz.y, luz.z).__sub__(ponto_intersec).__normalize__()
            L_np = np.array([L.x, L.y, L.z])
            em_sombra=False
            #checa se o ponto tá na sombra de outro obj
            for obj_sombra in entidades:
                is_transparent_shadow = hasattr(obj_sombra, 'k_difuso') and obj_sombra.k_difuso == 0 and obj_sombra.k_ambiental == 0
                if is_transparent_shadow:
                    continue
                if obj_sombra is not entidade:
                    epsilon_sombra = 1e-4
                    origem_sombra = ponto_intersec + Vetor(N[0], N[1], N[2]).__mul_escalar__(epsilon_sombra)
                    raio_sombra = Ray(origem_sombra, L)
                    distancia_luz = ponto_intersec.__distance__(Ponto(luz.x, luz.y, luz.z))
                    intersecao_sombra = obj_sombra.__intersect_line__(raio_sombra.origin, raio_sombra.direction)
                    if intersecao_sombra:
                        ponto_sombra = Ponto(intersecao_sombra[0], intersecao_sombra[1], intersecao_sombra[2])
                        if origem_sombra.__distance__(ponto_sombra) < distancia_luz:
                            em_sombra = True; break
            
            if not em_sombra:
                #calc a cor difusa (a cor "base" do obj sob a luz)
                N_dot_L = clamp(0, np.dot(N, L_np), 1)
                I_difusa = np.array(luz.I) * entidade.color * entidade.k_difuso * N_dot_L
                #calc o brilho da superfície
                R = (2 * N * N_dot_L) - L_np; R_dot_V = clamp(0, np.dot(R, V), 1)
                I_especular = np.array(luz.I) * entidade.k_especular * (R_dot_V**entidade.n_rugosidade)
                cor_local += I_difusa + I_especular
        
        #se o obj for reflexivo (espelho), calc o reflexo
        cor_refletida = np.array([0.0, 0.0, 0.0])
        if entidade.k_reflexao > 0:
            epsilon = 1e-4
            direcao_refletida = I - (2 * np.dot(I, N) * N)
            origem_refletida = ponto_intersec + Vetor(N[0], N[1], N[2]).__mul_escalar__(epsilon)
            raio_refletido = Ray(origem_refletida, Vetor(direcao_refletida[0], direcao_refletida[1], direcao_refletida[2]))
            new_targets = [t for t in entidades if t is not entidade]
            cor = find_closest_intersection(raio_refletido, new_targets, luzes, profundidade_reflexao + 1, profundidade_refracao)
            if cor: cor_refletida = np.array(cor)
        
        #mistura a cor local c/ a cor refletida
        cor_final_np = cor_local * (1.0 - entidade.k_reflexao) + cor_refletida * entidade.k_reflexao

    return [clamp(0, int(c), 255) for c in cor_final_np]

#func q dispara um raio e descobre qual o primeiro obj q ele acerta
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
            #acha o obj mais perto (e evita auto-interseção)
            if distance < min_distance and distance > 1e-4:
                min_distance, entidade_atingida, ponto_de_intersecao = distance, entidade, p_intersec
    #se achou algo, chama phong p/ saber a cor
    if entidade_atingida:
        return phong(entidade_atingida, luzes, ponto_de_intersecao, ray.origin, entidades, profundidade_reflexao, profundidade_refracao)
    #se não acertou nada, retorna preto
    return [0, 0, 0]
