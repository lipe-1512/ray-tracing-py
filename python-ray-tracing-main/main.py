import numpy as np
from phong_with_args import refract
from vectors import Ponto, Vetor
from entidades import Mesh, Esfera, Plane
from camera import Camera
from ray_casting import RayCasting
from fonte_de_luz import Luz

def main():

    esfera_azul = Esfera(
        center=Ponto(2, 0, -4),
        radius=1,
        color=(1, 0, 0),
        k_difuso=0.8,
        k_ambiental=0.4,
        k_especular=0.8,
        n_rugosidade=0.8,
        k_reflexao=0.6,
        k_refracao=5.0,
        indice_refracao=0.3,
    )

    esfera_vermelha = Esfera(
        center=Ponto(2, 0, 4),
        radius=1,
        color=(0, 0, 1),
        k_difuso=0.8,
        k_ambiental=0.5,
        k_especular=0.6,
        n_rugosidade=0.8,
        k_reflexao=0.7,
        k_refracao=0.4,
        indice_refracao=1.0,
    )


    esfera_verde = Esfera(
        center=Ponto(2, 0, 0),
        radius=2,
        color=(0, 1, 0),
        k_difuso=0.8,
        k_ambiental=0.5,
        k_especular=0.6,
        n_rugosidade=0.8,
        k_reflexao=0.7,
        k_refracao=0.3,
        indice_refracao=1.0,
    )

    esfera_amarela = Esfera(
        center=Ponto(8, 2, 0), #(zoom, cima baixo, esq e dir)
        radius=5,
        color=(0, 1, 1),
        k_difuso=0.8,
        k_ambiental=0.5,
        k_especular=0.6,
        n_rugosidade=0.8,
        k_reflexao=0.7,
        k_refracao=0.8,
        indice_refracao=1.0,
    )

    esfera_white= Esfera(
        center=Ponto(2, 4, 4), #(zoom, cima baixo, esq e dir)
        radius=1,
        color=(0.8, 1, 1),
        k_difuso=0.8,
        k_ambiental=0.5,
        k_especular=0.6,
        n_rugosidade=1,
        k_reflexao=0.7,
        k_refracao=0.3,
        indice_refracao=1.0,
    )

    esfera_verde2= Esfera(
        center=Ponto(-2, -2, 2), #(zoom, cima baixo, esq e dir)
        radius=1,
        color=(0.5, 1, 0.3),
        k_difuso=0.8,
        k_ambiental=0.5,
        k_especular=0.6,
        n_rugosidade=1,
        k_reflexao=0.7,
        k_refracao=0.3,
        indice_refracao=1.0,
    )

    A = Ponto(5, -3, -5)
    B = Ponto(0, -3, -5)
    C = Ponto(0, -3, 5)
    D = Ponto(5, -3, 5)
    #--
    E = Ponto(0,3,5)
    F = Ponto(0,3,-5)
    G = Ponto(5,3,-5)
    H = Ponto(5,3,5)

    # Normais para os dois triângulos da malha
    normal1 = (B - A).__cross__(C - A).__normalize__()
    normal2 = (C - A).__cross__(D - A).__normalize__()

    mesh_baixo = Mesh(
        triangle_quantity=2,
        vertices_quantity=4,
        vertices=[A, B, C, D],
        triangle_normals=[normal1, normal2],
        color=(0.4, 0.7, 1.0), 
        triangle_tuple_vertices=[(0, 1, 2), (0, 2, 3)],
        vertex_normals=[],
        k_difuso=1,
        k_ambiental=1,
        k_especular=0.6,
        n_rugosidade=8.0,
        k_reflexao=0.3,
        k_refracao=0,
        indice_refracao=0,
    )

    normal3 = (H - E).__cross__(D - E).__normalize__()
    normal4 = (D - E).__cross__(C - E).__normalize__()

    mesh_dir = Mesh(
        triangle_quantity=2,
        vertices_quantity=4,
        vertices=[E, H, D, C],
        triangle_normals=[normal3, normal4],
        color=(1.0, 0.7, 0.4),
        triangle_tuple_vertices=[(0, 1, 2), (0, 2, 3)],
        vertex_normals=[],
        k_difuso=1,
        k_ambiental=1,
        k_especular=0.5,
        n_rugosidade=8.0,
        k_reflexao=0.3,
        k_refracao=0,
        indice_refracao=0,
    )

    normal5 = (F - G).__cross__(B - G).__normalize__()
    normal6 = (B - G).__cross__(A - G).__normalize__()

    mesh_esq = Mesh(
        triangle_quantity=2,
        vertices_quantity=4,
        vertices=[G, F, B, A],  
        triangle_normals=[normal5, normal6],
        color=(0.4, 1.0, 0.7),
        triangle_tuple_vertices=[(0, 1, 2), (0, 2, 3)],
        vertex_normals=[],
        k_difuso=1,
        k_ambiental=1,
        k_especular=0.5,
        n_rugosidade=8.0,
        k_reflexao=0.3,
        k_refracao=0,
        indice_refracao=0,
    )

    normal7 = (A - G).__cross__(H - G).__normalize__()
    normal8 = (H - G).__cross__(D - G).__normalize__()

    mesh_tras = Mesh(
        triangle_quantity=2,
        vertices_quantity=4,
        vertices=[G, F, A, D],  
        triangle_normals=[normal7, normal8],
        color=(0.4, 1.0, 0.7),
        triangle_tuple_vertices=[(0, 1, 2), (0, 2, 3)],
        vertex_normals=[],
        k_difuso=1,
        k_ambiental=1,
        k_especular=0.5,
        n_rugosidade=8.0,
        k_reflexao=0.3,
        k_refracao=0,
        indice_refracao=0,
    )

    esfera_branca = Esfera(
        center=Ponto(15, -2, 0),    
        radius=1.5,
        color=(1, 1, 1),         
        k_difuso=0.6,             
        k_ambiental=0.8,          
        k_especular=0.9,         
        n_rugosidade=32,          
        k_reflexao=0.2,         
        k_refracao=0,           
        indice_refracao=1.5      
    )
    esfera_roxa = Esfera(
        center=Ponto(15, 2, 0),    
        radius=1.5,
        color=(1, 0, 0.5),          
        k_difuso=0.6,             
        k_ambiental=0.8,          
        k_especular=0.9,         
        n_rugosidade=32,          
        k_reflexao=0.2,          
        k_refracao=0,           
        indice_refracao=1.5       
    )

    esfera_transparente = Esfera(
        center=Ponto(12, 0, 0),      
        radius=2,
        color=(1, 1, 1),            

        # --- Parâmetros Chave para Transparência ---
        k_difuso=0,              
        k_ambiental=0,           
        k_especular=0.9,           
        n_rugosidade=32,           
        k_reflexao=0.8,             

        # --- Parâmetros para Refração ---
        k_refracao=0.9,             
        indice_refracao=0.5         
    )

    # result = refract(np.array([0.707107, -0.707107]), np.array([0, 1]), 9, 10)


    ray_casting = RayCasting(hres=700, vres=700)

    #(zoom, cima baixo, esq e dir)
    camera1 = Camera(
        target=Ponto(10, 0, 0),
        position=Ponto(-15, 0, 0),
        up=Vetor(0, 1, 0),
    )

    camera2 = Camera(
        target=Ponto(10, 0, 0),
        position=Ponto(-10, 0, 0),
        up=Vetor(0, 1, 0),
    )

    luzes_da_cena = [
        #Luz(0, 10, -5, [255, 255, 255]),
        Luz(-15, 10, 0, [255, 255, 255])
    ]


    #Exemplo 1 (3 esferas ao lado uma da outra com uma malha no lado esquerdo apenas)
    entidades1 = [esfera_vermelha, esfera_azul, mesh_dir, esfera_verde]

    #Exemplo 2 (3 esferas, 2 ao lado uma da outra com malhas nos lado esq, dir e abaixo e uma esfera grandona atrás)
    entidades2 = [esfera_vermelha, esfera_azul, esfera_amarela, mesh_dir, mesh_esq, mesh_baixo]

    #Exemplo 3 (4 esferas, 3 pequenas e 1 maior onde há reflexão mútua entre si)
    entidades3 = [esfera_vermelha, esfera_azul, esfera_amarela, esfera_white]

    #Exemplo 4 (3 esferas, 2 ao lado uma da outra com malhas nos lado esq, dir e abaixo e uma esfera grandona atrás)
    entidades4 = [esfera_vermelha, esfera_azul, mesh_dir, mesh_esq, mesh_baixo, mesh_tras, esfera_transparente]

    #Exemplo 5 (3 esferas, 2 opacas e 1 de vidro, mostrando o poder da refração)
    entidades5 = [esfera_transparente, esfera_branca, esfera_roxa]

    ray_casting.__generate_image__(entidades5, luzes_da_cena, 1, camera2)

main()
