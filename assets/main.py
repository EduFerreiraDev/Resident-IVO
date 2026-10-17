import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy as np
import ctypes
import glm
from pathlib import Path
from  cubo import Cubo


# ============================================================
# GEOMETRIA: CUBO COM 12 TRIANGULOS (8 VERTICES + EBO)
# ============================================================

vertices = [
    (1, 1, 1),
    (-1, 1, 1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, -1)
]

indices = [
    (0, 1, 2), (0, 2, 3),
    (4, 5, 6), (4, 6, 7),
    (0, 1, 5), (0, 5, 4),
    (2, 3, 7), (2, 7, 6),
    (1, 2, 6), (1, 6, 5),
    (0, 3, 7), (0, 7, 4)
]

# Apenas 8 vertices na GPU; os indices dizem como formar os triangulos
vertices_array = np.array(vertices, dtype=np.float32)
indices_array = np.array(indices, dtype=np.uint8).flatten()
total_indices = indices_array.size


# ============================================================
# VARIAVEIS GLOBAIS
# ============================================================

vaoId = 0
shaderId = 0

modelo_loc = -1
visualizacao_loc = -1
projecao_loc = -1
cor_loc = -1

visualizacao = glm.mat4(1.0)
projecao = glm.mat4(1.0)

# Lista de (matriz_modelo, cor) calculada uma unica vez
cubos = []

camera_alvo = glm.vec3(0.0, -0.5, 0.0)

# Mantém a distância e o enquadramento inicial da câmera atual
camera_distancia = glm.length(glm.vec3(0.0, 5.5, 11.0))
camera_yaw = 0.0
camera_pitch = 26.565

arrastando_mouse = False
mouse_x_anterior = 0.0
mouse_y_anterior = 0.0

camera_pos = glm.vec3(0.0, 5.0, 11.0)

modo_primeira_pessoa = False

primeira_pessoa_pos = glm.vec3(0.0, 0.8, 3.5)
primeira_pessoa_yaw = 0.0
primeira_pessoa_pitch = 0.0

def atualizar_visualizacao():
    global visualizacao
    visualizacao = glm.lookAt(
        camera_pos,
        camera_alvo,
        glm.vec3(0.0, 1.0, 0.0)
    )

def atualizar_camera_orbita():
    global camera_pos, camera_pitch

    camera_pitch = max(-85.0, min(85.0, camera_pitch))

    yaw_rad = glm.radians(camera_yaw)
    pitch_rad = glm.radians(camera_pitch)
    distancia_horizontal = camera_distancia * glm.cos(pitch_rad)

    camera_pos = camera_alvo + glm.vec3(
        distancia_horizontal * glm.sin(yaw_rad),
        camera_distancia * glm.sin(pitch_rad),
        distancia_horizontal * glm.cos(yaw_rad)
    )

    atualizar_visualizacao()

def direcao_primeira_pessoa():
    yaw_rad = glm.radians(primeira_pessoa_yaw)
    pitch_rad = glm.radians(primeira_pessoa_pitch)

    return glm.normalize(glm.vec3(
        glm.sin(yaw_rad) * glm.cos(pitch_rad),
        glm.sin(pitch_rad),
        -glm.cos(yaw_rad) * glm.cos(pitch_rad)
    ))


def atualizar_camera_primeira_pessoa():
    global visualizacao

    direcao = direcao_primeira_pessoa()
    visualizacao = glm.lookAt(
        primeira_pessoa_pos,
        primeira_pessoa_pos + direcao,
        glm.vec3(0.0, 1.0, 0.0)
    )

def mover_primeira_pessoa(window, delta_tempo):
    global primeira_pessoa_pos

    if not modo_primeira_pessoa:
        return

    yaw_rad = glm.radians(primeira_pessoa_yaw)

    frente = glm.vec3(
        glm.sin(yaw_rad),
        0.0,
        -glm.cos(yaw_rad)
    )
    direita = glm.vec3(
        glm.cos(yaw_rad),
        0.0,
        glm.sin(yaw_rad)
    )

    deslocamento = glm.vec3(0.0)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        deslocamento += frente
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        deslocamento -= frente
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        deslocamento += direita
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        deslocamento -= direita

    if glm.length(deslocamento) > 0.0:
        velocidade = 3.0
        deslocamento = glm.normalize(deslocamento) * velocidade * delta_tempo
        nova_posicao = primeira_pessoa_pos + deslocamento

        nova_posicao.x = max(-4.5, min(4.5, nova_posicao.x))
        nova_posicao.z = max(-4.5, min(4.5, nova_posicao.z))

        primeira_pessoa_pos = nova_posicao
        atualizar_camera_primeira_pessoa()

def botao_mouse(window, button, action, mods):
    global arrastando_mouse, mouse_x_anterior, mouse_y_anterior

    if button != glfw.MOUSE_BUTTON_LEFT:
        return

    if action == glfw.PRESS:
        arrastando_mouse = True
        mouse_x_anterior, mouse_y_anterior = glfw.get_cursor_pos(window)
    elif action == glfw.RELEASE:
        arrastando_mouse = False


def mover_mouse(window, xpos, ypos):
    global mouse_x_anterior, mouse_y_anterior
    global camera_yaw, camera_pitch
    global primeira_pessoa_yaw, primeira_pessoa_pitch

    diferenca_x = xpos - mouse_x_anterior
    diferenca_y = ypos - mouse_y_anterior

    mouse_x_anterior = xpos
    mouse_y_anterior = ypos

    sensibilidade = 0.25

    if modo_primeira_pessoa:
        primeira_pessoa_yaw += diferenca_x * sensibilidade
        primeira_pessoa_pitch -= diferenca_y * sensibilidade
        primeira_pessoa_pitch = max(
            -89.0, min(89.0, primeira_pessoa_pitch)
        )
        atualizar_camera_primeira_pessoa()
        return

    if not arrastando_mouse:
        return

    camera_yaw -= diferenca_x * sensibilidade
    camera_pitch -= diferenca_y * sensibilidade

    atualizar_camera_orbita()

# ============================================================
# INICIALIZACAO
# ============================================================

def init():
    global vaoId, shaderId
    global modelo_loc, visualizacao_loc
    global projecao_loc, cor_loc

    glClearColor(0.12, 0.16, 0.20, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Criacao do VAO
    vaoId = glGenVertexArrays(1)
    glBindVertexArray(vaoId)

    # Criacao do VBO
    vboId = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vboId)

    glBufferData(
        GL_ARRAY_BUFFER,
        vertices_array.nbytes,
        vertices_array,
        GL_STATIC_DRAW
    )

    glVertexAttribPointer(
        0, 3, GL_FLOAT, GL_FALSE,
        3 * 4, ctypes.c_void_p(0)
    )
    glEnableVertexAttribArray(0)

    # Criacao do EBO (fica guardado dentro do VAO,
    # por isso NAO desvincular antes do VAO)
    eboId = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, eboId)

    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER,
        indices_array.nbytes,
        indices_array,
        GL_STATIC_DRAW
    )

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # Carregar shaders da pasta do projeto
    pasta = Path(__file__).resolve().parent

    with open(pasta / "C:/PROGRAMAÇÃO/vscode/Python/CG/trab_CG/cubo_vert.glsl", "r", encoding="utf-8") as f:
        vsSource = f.read()

    with open(pasta / "C:/PROGRAMAÇÃO/vscode/Python/CG/trab_CG/cubo_frag.glsl", "r", encoding="utf-8") as f:
        fsSource = f.read()

    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

    # Camera em perspectiva (posicao calculada pela orbita)
    atualizar_camera_orbita()

    # Localizacao das variaveis uniformes
    modelo_loc = glGetUniformLocation(shaderId, "modelo")
    visualizacao_loc = glGetUniformLocation(
        shaderId, "visualizacao"
    )
    projecao_loc = glGetUniformLocation(shaderId, "projecao")
    cor_loc = glGetUniformLocation(shaderId, "corObjeto")

    # A cena e estatica: monta as matrizes uma unica vez
    construir_laboratorio()


def atualizar_projecao(largura, altura):
    global projecao

    if altura == 0:
        return

    campo_visao = 55.0 if modo_primeira_pessoa else 45.0

    projecao = glm.perspective(
        glm.radians(campo_visao),
        largura / altura,
        0.1,
        100.0
    )

    glViewport(0, 0, largura, altura)


def redimensionar_janela(window, largura, altura):
    atualizar_projecao(largura, altura)


# ============================================================
# REGISTRAR UM CUBO COM POSICAO, ESCALA E COR
# (a matriz modelo e calculada uma vez, nao a cada frame)
# ============================================================


def desenhar_cubos():
    for cubo in cubos:
        cubo.desenhar(modelo_loc, cor_loc, total_indices)


# ============================================================
# CONSTRUCAO DO LABORATORIO
# ============================================================

def construir_laboratorio():

    # Chao
    cubos.append(Cubo((0, -2.5, 0),(5, 0.1, 5),(0.35, 0.38, 0.40)))

    # Parede do fundo
    cubos.append(Cubo((0, 0, -4.9),(5, 2.5, 0.1),(0.72, 0.76, 0.80)))

    # Parede esquerda
    cubos.append(Cubo((-4.9, 0, 0),(0.1, 2.5, 5),(0.55, 0.62, 0.68)))

    # Parede direita
    cubos.append(Cubo((4.9, 0, 0),(0.1, 2.5, 5),(0.55, 0.62, 0.68)))

    # Tampo da bancada
    cubos.append(Cubo((0, -0.65, -1.0),(2.0, 0.15, 1.0),(0.45, 0.27, 0.15)))

    # Pernas da bancada
    for x in (-1.75, 1.75):
        for z in (-1.8, -0.2):
            cubos.append(Cubo((x, -1.55, z),(0.12, 0.8, 0.12),(0.25, 0.27, 0.29)))

    # Base do microscopio
    cubos.append(Cubo((-0.7, -0.42, -1.0),(0.4, 0.08, 0.3),(0.12, 0.18, 0.22)))

    # Coluna do microscopio
    cubos.append(Cubo((-0.7, -0.05, -1.0),(0.08, 0.32, 0.08),(0.15, 0.20, 0.24)))

    # Parte superior do microscopio
    cubos.append(Cubo((-0.7, 0.22, -1.0),(0.25, 0.08, 0.12),(0.18, 0.25, 0.30)))

    # Ocular
    cubos.append(Cubo((-0.88, 0.35, -1.0),(0.08, 0.12, 0.08),(0.08, 0.09, 0.10)))

    # Frascos: base e tampa
    for x, cor in [
        (0.3, (0.20, 0.65, 0.85)),
        (0.9, (0.25, 0.75, 0.45)),
        (1.5, (0.85, 0.55, 0.20))
    ]:
        cubos.append(Cubo((x, -0.35, -1.2),(0.18, 0.25, 0.18),cor))

        cubos.append(Cubo((x, -0.05, -1.2),(0.08, 0.06, 0.08),(0.20, 0.22, 0.24)))

    # Suporte de tubos de ensaio
    cubos.append(Cubo((0.5, -0.40, -0.2),(0.55, 0.08, 0.25),(0.25, 0.18, 0.12)))

    # Tubos simplificados
    for x in (0.15, 0.5, 0.85):
        cubos.append(Cubo((x, -0.20, -0.2),(0.09, 0.15, 0.09),(0.35, 0.75, 0.85)))


# ============================================================
# RENDERIZACAO
# ============================================================

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUseProgram(shaderId)

    glUniformMatrix4fv(
        visualizacao_loc, 1, GL_FALSE,
        glm.value_ptr(visualizacao)
    )

    glUniformMatrix4fv(
        projecao_loc, 1, GL_FALSE,
        glm.value_ptr(projecao)
    )

    # VAO vinculado uma vez por frame (e nao a cada cubo)
    glBindVertexArray(vaoId)
    desenhar_cubos()
    glBindVertexArray(0)

    glUseProgram(0)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def mover_camera(window, key, scancode, action, mods):
    global camera_pos, camera_alvo

    if action not in (glfw.PRESS, glfw.REPEAT):
        return

    global modo_primeira_pessoa

    if key == glfw.KEY_1:
        modo_primeira_pessoa = True
        atualizar_camera_primeira_pessoa()
        atualizar_projecao(*glfw.get_framebuffer_size(window))
        return

    if key == glfw.KEY_3:
        modo_primeira_pessoa = False
        atualizar_visualizacao()
        atualizar_projecao(*glfw.get_framebuffer_size(window))
        return

    passo = 0.25
    
    movimentos = {
        glfw.KEY_LEFT:  glm.vec3(-passo, 0.0, 0.0),
        glfw.KEY_RIGHT: glm.vec3(passo, 0.0, 0.0),
        glfw.KEY_UP:    glm.vec3(0.0, passo, 0.0),
        glfw.KEY_DOWN:  glm.vec3(0.0, -passo, 0.0),
    }

    deslocamento = movimentos.get(key)
    if deslocamento is not None:
        camera_pos += deslocamento
        camera_alvo += deslocamento
        atualizar_visualizacao()

def zoom_camera(window, xoffset, yoffset):
    global camera_distancia

    if modo_primeira_pessoa:
        return

    if yoffset == 0:
        return

    fator = 0.9 if yoffset > 0 else 1.1
    camera_distancia = max(3.0, min(30.0, camera_distancia * fator))

    atualizar_camera_orbita()

def main():
    if not glfw.init():
        raise RuntimeError("Nao foi possivel inicializar o GLFW.")

    window = glfw.create_window(
        800, 600, "Laboratorio 3D - Sprint 2", None, None
    )

    if not window:
        glfw.terminate()
        raise RuntimeError("Nao foi possivel criar a janela.")

    glfw.make_context_current(window)

    # VSync: limita ao refresh do monitor (evita usar 100% da GPU/CPU)
    glfw.swap_interval(1)

    glfw.set_framebuffer_size_callback(
        window, redimensionar_janela
    )

    init()

    # Usa o tamanho real do framebuffer (correto em telas com escala/HiDPI)
    atualizar_projecao(*glfw.get_framebuffer_size(window))

    glfw.set_mouse_button_callback(window, botao_mouse)
    glfw.set_cursor_pos_callback(window, mover_mouse)
    glfw.set_scroll_callback(window, zoom_camera)
    glfw.set_key_callback(window, mover_camera)

    ultimo_tempo = glfw.get_time()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        agora = glfw.get_time()
        delta_tempo = agora - ultimo_tempo
        ultimo_tempo = agora

        mover_primeira_pessoa(window, delta_tempo)
        render()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()