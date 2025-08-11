import cv2 as cv
import numpy as np
from vectors import Ponto, Vetor
from phong_with_args import phong, clamp
from fonte_de_luz import Luz
from ray import Ray
from entidades import Esfera

class Camera:
    def __init__(self, target: "Ponto", position: "Ponto", up: "Vetor", vres: int = 300, hres: int = 300):
        #inicializa a câmera c/ pos, alvo e vetor up
        self.position = position
        self.target = target
        self.up = up

        #vetor w aponta p/ o alvo (target)
        self.w: "Vetor" = self.target.__sub__(self.position)
        #vetor v é o "right", ortogonal a w e up
        self.v: "Vetor" = self.up.__cross__(self.w)

        #normaliza os vetores p/ serem unitários
        self.w = self.w.__normalize__()
        self.v = self.v.__normalize__()

        #vetor u é o "up" real, corrigido p/ o sistema de coords
        self.u: "Vetor" = self.w.__cross__(self.v).__mul_escalar__(-1)
        self.u = self.u.__normalize__()

        self.vres = vres
        self.hres = hres

    def __intersect__(self, ray: "Ray", targets: list, luzes: list) -> list:
        #começa c/ dist infinita p/ achar o obj mais próximo
        smallest_distance = float("inf")
        closest_target = None
        intersection_point = None

        #loop em tds os objs da cena
        for target in targets:
            origin_tuple = (ray.origin.x, ray.origin.y, ray.origin.z)
            direction_tuple = (ray.direction.x, ray.direction.y, ray.direction.z)
            #checa se o raio bate no obj
            intersection = target.__intersect_line__(origin_tuple, direction_tuple)
            if intersection:
                p_intersec = Ponto(intersection[0], intersection[1], intersection[2])
                distance = ray.origin.__distance__(p_intersec)
                #se for o obj mais perto até agr, salva ele
                if distance < smallest_distance and distance > 1e-4:
                    smallest_distance, closest_target, intersection_point = distance, target, p_intersec

        #se acertou algum obj, decide a cor
        if closest_target:
            #checa se o obj é transparente (sem cor difusa/ambiente)
            is_transparent = hasattr(closest_target, 'k_difuso') and closest_target.k_difuso == 0 and closest_target.k_ambiental == 0
            
            if is_transparent:
                #se for transparente, entra na lógica do "portal" c/ distorção
                
                #pega os vetores de visão (V) e a normal (N) no ponto
                V = ray.origin.__sub__(intersection_point).__normalize__(); V_np = np.array([V.x, V.y, V.z])
                if isinstance(closest_target, Esfera):
                    N = intersection_point.__sub__(closest_target.center).__normalize__()
                else: N = Vetor(0,1,0)
                N_np = np.array([N.x, N.y, N.z])
                
                #aqui vc pode controlar a força da distorção do vidro
                forca_distorcao = 0.3 
                #calc o fator de distorção usando o indice de refracao do obj
                fator_distorcao = (1.0 - closest_target.indice_refracao) * forca_distorcao
                offset_np = N_np * fator_distorcao
                offset_vetor = Vetor(offset_np[0], offset_np[1], offset_np[2])
                #cria a nova direção do raio, já distorcida
                direcao_distorcida_vetor = ray.direction + offset_vetor
                
                #cria o novo raio q "passou" pelo portal
                new_ray_origin = intersection_point + (direcao_distorcida_vetor.__mul_escalar__(0.0001))
                new_ray = Ray(new_ray_origin, direcao_distorcida_vetor)
                #lista de objs sem o portal, p/ não bater nele de novo
                new_targets = [t for t in targets if t is not closest_target]
                #recursão: chama a func de novo p/ pegar a cor do fundo
                cor_de_fundo = self.__intersect__(new_ray, new_targets, luzes)
                cor_de_fundo = np.array(cor_de_fundo, dtype=float)
                
                #calc o brilho especular (reflexo da luz no vidro)
                cor_brilho = np.array([0.,0.,0.])
                for luz in luzes:
                    L = Ponto(luz.x, luz.y, luz.z).__sub__(intersection_point).__normalize__(); L_np = np.array([L.x, L.y, L.z])
                    N_dot_L = max(0, np.dot(N_np, L_np))
                    R = (2 * N_np * N_dot_L) - L_np; R_dot_V = max(0, np.dot(R, V_np))
                    I_especular = np.array(luz.I) * closest_target.k_especular * (R_dot_V ** closest_target.n_rugosidade)
                    cor_brilho += I_especular
                
                #calc o efeito de borda (mais opaco/escuro nas bordas)
                facing_ratio = np.dot(V_np, N_np)
                fresnel_effect = (1.0 - abs(facing_ratio)) ** 5
                cor_borda = np.array([50.0, 50.0, 50.0])

                #mistura a cor de fundo c/ a cor da borda
                cor_renderizada = cor_de_fundo * (1.0 - fresnel_effect) + cor_borda * fresnel_effect
                #soma o brilho por cima de td
                cor_final_np = cor_renderizada + cor_brilho
                #retorna a cor final, garantindo q tá entre 0-255
                return [clamp(0, int(c), 255) for c in cor_final_np]

            else:
                #se for opaco, chama a func phong normal p/ calcular a cor
                return phong(closest_target, luzes, intersection_point, ray.origin, targets, 0, 0)
        
        #se não acertou nada, retorna a cor de fundo (preto)
        return [0, 0, 0]
