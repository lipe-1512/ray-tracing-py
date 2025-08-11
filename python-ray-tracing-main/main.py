import numpy as np
from phong_with_args import refract
from vectors import Ponto, Vetor
from entidades import Mesh, Esfera, Plane
from camera import Camera
from ray_casting import RayCasting
from fonte_de_luz import Luz

def main():

    esfera_azul = Esfera(
        center=(2, 0, -4),
        radius=1,
        color=(0, 0, 1), # Corrigido para azul
        k_difuso=0.8, k_ambiental=0.4, k_especular=0.8, n_rugosidade=0.8,
        k_reflexao=0.6, k_refracao=5.0, indice_refracao=0.3,
    )

    esfera_vermelha = Esfera(
        center=(2, 0, 4),
        radius=1,
        color=(1, 0, 0), # Corrigido para vermelho
        k_difuso=0.8, k_ambiental=0.5, k_especular=0.6, n_rugosidade=0.8,
        k_reflexao=0.7, k_refracao=0.4, indice_refracao=1.0,
    )

    esfera_branca = Esfera(
        center=(2, -1, 0),    
        radius=1.5,
        color=(1, 1, 1),         
        k_difuso=0.6, k_ambiental=0.8, k_especular=0.9, n_rugosidade=32,          
        k_reflexao=0.2, k_refracao=0, indice_refracao=1.5      
    )
    
    # --- PLANO COM RELIEF MAPPING ---
    plano_chao = Plane(
        point=(0, -3, 0),
        normal=(0, 1, 0),
        color=(0.7, 0.7, 0.8), # Cor de pedra
        k_difuso=0.9,
        k_ambiental=0.1,
        k_especular=0.4,
        n_rugosidade=10.0,
        k_reflexao=0.2,
        # Parâmetros para ativar e controlar o relevo
        use_relief=True,
        relief_scale=0.8,  # Aumente para um relevo mais "alto"
        uv_scale=0.5       # Diminua para "esticar" a textura (ondas maiores)
    )

    ray_casting = RayCasting(hres=700, vres=700)

    camera = Camera(
        target=Ponto(0, -1, 0),
        position=Ponto(-15, 2, 0), # Posição ligeiramente elevada
        up=Vetor(0, 1, 0),
    )

    luzes_da_cena = [
        Luz(-15, 10, -5, [255, 255, 255])
    ]

    # Cena de teste para o relevo
    entidades = [esfera_vermelha, esfera_azul, esfera_branca, plano_chao]

    ray_casting.__generate_image__(entidades, luzes_da_cena, 1, camera)

main()