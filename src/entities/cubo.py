import ctypes
import math
import glm
from OpenGL.GL import *

INDICES_ARESTAS = [
    0, 1, 1, 2, 2, 3, 3, 0,
    4, 5, 5, 6, 6, 7, 7, 4,
    0, 4, 1, 5, 2, 6, 3, 7,
]

class Cubo:
    def __init__(self, posicao, escala, cor, colisivel=False, colisao_ativa=True, apoio=False, parede=False):
        self.posicao = glm.vec3(*posicao)
        self.escala = glm.vec3(*escala)
        self.cor = tuple(cor)
        self.colisivel = colisivel
        self.colisao_ativa = colisao_ativa
        self.apoio = apoio
        self.parede = parede
        self.rotacao = 0.0

        self.atualizar_modelo()

    def atualizar_modelo(self):
        modelo = glm.mat4(1.0)
        modelo = glm.translate(modelo, self.posicao)
        modelo = glm.rotate(modelo, glm.radians(self.rotacao), glm.vec3(0, 1, 0))
        modelo = glm.scale(modelo, self.escala)
        self.modelo = modelo

    def limites(self):
        c = abs(math.cos(math.radians(self.rotacao)))
        s = abs(math.sin(math.radians(self.rotacao)))
        extensao = glm.vec3(c * self.escala.x + s * self.escala.z,
                            self.escala.y,
                            s * self.escala.x + c * self.escala.z)
        return self.posicao - extensao, self.posicao + extensao

    def desenhar(self, modelo_loc, cor_loc, total_indices):
        glUniformMatrix4fv(
            modelo_loc,
            1,
            GL_FALSE,
            glm.value_ptr(self.modelo),
        )

        glUniform3f(
            cor_loc,
            self.cor[0],
            self.cor[1],
            self.cor[2],
        )

        glDrawElements(
            GL_TRIANGLES,
            total_indices,
            GL_UNSIGNED_BYTE,
            ctypes.c_void_p(0),
        )

    def desenhar_contorno(
        self, modelo_loc, cor_loc, buffer_arestas, buffer_triangulos
    ):
        modelo_contorno = glm.scale(self.modelo, glm.vec3(1.01))

        glUniformMatrix4fv(
            modelo_loc,
            1,
            GL_FALSE,
            glm.value_ptr(modelo_contorno),
        )

        glUniform3f(cor_loc, 1.0, 1.0, 1.0)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffer_arestas)
        glDrawElements(
            GL_LINES,
            len(INDICES_ARESTAS),
            GL_UNSIGNED_BYTE,
            ctypes.c_void_p(0),
        )
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffer_triangulos)
