import glm
from src.game.colisao import resolver_movimento

class Camera:
    def __init__(self):
        self.modo_primeira_pessoa = False

        # Câmera Orbital
        self.alvo = glm.vec3(0.0, -0.5, 0.0)
        self.distancia = glm.length(glm.vec3(0.0, 5.5, 11.0))
        self.yaw = 0.0
        self.pitch = 26.565
        self.pos = glm.vec3(0.0, 5.0, 11.0)

        # Câmera Primeira Pessoa
        self.fp_pos = glm.vec3(0.0, 0.8, 3.5)
        self.fp_yaw = 0.0
        self.fp_pitch = 0.0

        self.view_matrix = glm.mat4(1.0)
        self.atualizar_orbita()

    def atualizar_view(self):
        if self.modo_primeira_pessoa:
            direcao = self.direcao_fp()
            self.view_matrix = glm.lookAt(self.fp_pos, self.fp_pos + direcao, glm.vec3(0.0, 1.0, 0.0))
        else:
            self.view_matrix = glm.lookAt(self.pos, self.alvo, glm.vec3(0.0, 1.0, 0.0))

    def atualizar_orbita(self):
        self.pitch = max(-85.0, min(85.0, self.pitch))
        yaw_rad = glm.radians(self.yaw)
        pitch_rad = glm.radians(self.pitch)
        dist_h = self.distancia * glm.cos(pitch_rad)

        self.pos = self.alvo + glm.vec3(
            dist_h * glm.sin(yaw_rad),
            self.distancia * glm.sin(pitch_rad),
            dist_h * glm.cos(yaw_rad)
        )
        self.atualizar_view()

    def direcao_fp(self):
        yaw_rad = glm.radians(self.fp_yaw)
        pitch_rad = glm.radians(self.fp_pitch)
        return glm.normalize(glm.vec3(
            glm.sin(yaw_rad) * glm.cos(pitch_rad),
            glm.sin(pitch_rad),
            -glm.cos(yaw_rad) * glm.cos(pitch_rad)
        ))

    def mover_fp(self, window, delta_tempo, glfw, objetos_colisao):
        if not self.modo_primeira_pessoa:
            return

        yaw_rad = glm.radians(self.fp_yaw)
        frente = glm.vec3(glm.sin(yaw_rad), 0.0, -glm.cos(yaw_rad))
        direita = glm.vec3(glm.cos(yaw_rad), 0.0, glm.sin(yaw_rad))
        deslocamento = glm.vec3(0.0)

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS: deslocamento += frente
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS: deslocamento -= frente
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS: deslocamento += direita
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS: deslocamento -= direita

        if glm.length(deslocamento) > 0.0:
            velocidade = 3.0
            deslocamento = glm.normalize(deslocamento) * velocidade * delta_tempo
            nova_pos = resolver_movimento(self.fp_pos, deslocamento, objetos_colisao)
            nova_pos.x = max(-4.5, min(4.5, nova_pos.x))
            nova_pos.z = max(-4.5, min(4.5, nova_pos.z))
            self.fp_pos = nova_pos
            self.atualizar_view()