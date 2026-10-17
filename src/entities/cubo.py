import ctypes
import glm
from OpenGL.GL import *


class Cubo:

    def __init__(self, posicao, escala, cor, colisivel=False):
        self.posicao = glm.vec3(*posicao)
        self.escala = glm.vec3(*escala)
        self.cor = tuple(cor)
        self.colisivel = colisivel

        modelo = glm.mat4(1.0)
        modelo = glm.translate(modelo, self.posicao)
        modelo = glm.scale(modelo, self.escala)

        self.modelo = modelo

    def desenhar(self, modelo_loc, cor_loc, total_indices):

        glUniformMatrix4fv(
            modelo_loc,
            1,
            GL_FALSE,
            glm.value_ptr(self.modelo)
        )

        glUniform3f(
            cor_loc,
            self.cor[0],
            self.cor[1],
            self.cor[2]
        )

        glDrawElements(
            GL_TRIANGLES,
            total_indices,
            GL_UNSIGNED_BYTE,
            ctypes.c_void_p(0)
        )
