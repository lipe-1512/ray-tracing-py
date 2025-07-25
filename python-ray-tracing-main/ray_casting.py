import cv2 as cv
import numpy as np
from camera import Camera, Ray


class RayCasting:

    def __init__(self, hres, vres):
        self.hres = hres
        self.vres = vres
        self.image = np.zeros((self.vres, self.hres, 3), dtype=np.uint8)
        self.total_pixels = self.vres * self.hres
        self.processed_pixels = 0

    def __generate_image__(self, targets, luzes, distancia, camera: Camera):
        u = camera.u
        v = camera.v
        w = camera.w

        for i in range(self.vres): #p/ cada pixel da tela (i, j), gera um raio partindo da câmera 
            for j in range(self.hres):
                ray = Ray(
                    origin=camera.position, #origem é sempre a pos da cam
                    direction=(
                        w.__mul_escalar__(distancia) # aponta da câmera para o target
                        + v.__mul_escalar__(2 * 0.5 * (j / self.hres - 0.5)) #vetor horizontal da câmera
                        + u.__mul_escalar__(2 * 0.5 * (i / self.vres - 0.5)) #vetor vertical da câmera
                    ),
                )
                color = camera.__intersect__(ray, targets, luzes) #pega a cor de um objeto que o raio colidir
                self.image[i, j] = color
                self.processed_pixels += 1
                
            print(f"Carregando: {self.processed_pixels / self.total_pixels * 100:.2f}%")

        cv.imshow("imagem", self.image)
        cv.waitKey(0)
        cv.destroyAllWindows("i")
 