
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy as np
import ctypes
import glm
from pathlib import Path


# ============================================================
# GEOMETRIA: CUBO COM 12 TRIANGULOS
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

vertices_desenho = []

for triangulo in indices:
    for indice in triangulo:
        vertices_desenho.append(vertices[indice])

vertices_array = np.array(
    vertices_desenho, dtype=np.float32
)


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

camera_alvo = glm.vec3(0.0, -0.5, 0.0)

# Mantém a distância e o enquadramento inicial da câmera atual
camera_distancia = glm.length(glm.vec3(0.0, 5.5, 11.0))
camera_yaw = 0.0
camera_pitch = 26.565

arrastando_mouse = False
mouse_x_anterior = 0.0
mouse_y_anterior = 0.0

camera_pos = glm.vec3(0.0, 5.0, 11.0)

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

    if not arrastando_mouse:
        return

    diferenca_x = xpos - mouse_x_anterior
    diferenca_y = ypos - mouse_y_anterior

    mouse_x_anterior = xpos
    mouse_y_anterior = ypos

    sensibilidade = 0.25
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
    global visualizacao, projecao

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

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # Carregar shaders da pasta do projeto
    pasta = Path(__file__).resolve().parent

    with open(pasta / "shaders/cubo_vert.glsl", "r", encoding="utf-8") as f:
        vsSource = f.read()

    with open(pasta / "shaders/cubo_frag.glsl", "r", encoding="utf-8") as f:
        fsSource = f.read()

    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

    # Camera em perspectiva
    atualizar_visualizacao()

    atualizar_projecao(800, 600)

    # Localizacao das variaveis uniformes
    modelo_loc = glGetUniformLocation(shaderId, "modelo")
    visualizacao_loc = glGetUniformLocation(
        shaderId, "visualizacao"
    )
    projecao_loc = glGetUniformLocation(shaderId, "projecao")
    cor_loc = glGetUniformLocation(shaderId, "corObjeto")


def atualizar_projecao(largura, altura):
    global projecao

    if altura == 0:
        return

    projecao = glm.perspective(
        glm.radians(45.0),
        largura / altura,
        0.1,
        100.0
    )

    glViewport(0, 0, largura, altura)


def redimensionar_janela(window, largura, altura):
    atualizar_projecao(largura, altura)


# ============================================================
# DESENHAR UM CUBO COM POSICAO, ESCALA E COR
# ============================================================

def desenhar_cubo(posicao, escala, cor):
    modelo = glm.mat4(1.0)

    modelo = glm.translate(
        modelo,
        glm.vec3(*posicao)
    )

    modelo = glm.scale(
        modelo,
        glm.vec3(*escala)
    )

    glUniformMatrix4fv(
        modelo_loc, 1, GL_FALSE, glm.value_ptr(modelo)
    )

    glUniform3f(
        cor_loc, cor[0], cor[1], cor[2]
    )

    glBindVertexArray(vaoId)

    glDrawArrays(
        GL_TRIANGLES, 0, len(vertices_desenho)
    )

    glBindVertexArray(0)


# ============================================================
# CONSTRUCAO DO LABORATORIO
# ============================================================

def desenhar_laboratorio():

    # Chao
    desenhar_cubo(
        (0, -2.5, 0),
        (5, 0.1, 5),
        (0.35, 0.38, 0.40)
    )

    # Parede do fundo
    desenhar_cubo(
        (0, 0, -4.9),
        (5, 2.5, 0.1),
        (0.72, 0.76, 0.80)
    )

    # Parede esquerda
    desenhar_cubo(
        (-4.9, 0, 0),
        (0.1, 2.5, 5),
        (0.55, 0.62, 0.68)
    )

    # Parede direita
    desenhar_cubo(
        (4.9, 0, 0),
        (0.1, 2.5, 5),
        (0.55, 0.62, 0.68)
    )

    # Tampo da bancada
    desenhar_cubo(
        (0, -0.65, -1.0),
        (2.0, 0.15, 1.0),
        (0.45, 0.27, 0.15)
    )

    # Pernas da bancada
    for x in (-1.75, 1.75):
        for z in (-1.8, -0.2):
            desenhar_cubo(
                (x, -1.55, z),
                (0.12, 0.8, 0.12),
                (0.25, 0.27, 0.29)
            )

    # Base do microscopio
    desenhar_cubo(
        (-0.7, -0.42, -1.0),
        (0.4, 0.08, 0.3),
        (0.12, 0.18, 0.22)
    )

    # Coluna do microscopio
    desenhar_cubo(
        (-0.7, -0.05, -1.0),
        (0.08, 0.32, 0.08),
        (0.15, 0.20, 0.24)
    )

    # Parte superior do microscopio
    desenhar_cubo(
        (-0.7, 0.22, -1.0),
        (0.25, 0.08, 0.12),
        (0.18, 0.25, 0.30)
    )

    # Ocular
    desenhar_cubo(
        (-0.88, 0.35, -1.0),
        (0.08, 0.12, 0.08),
        (0.08, 0.09, 0.10)
    )

    # Frascos: base e tampa
    for x, cor in [
        (0.3, (0.20, 0.65, 0.85)),
        (0.9, (0.25, 0.75, 0.45)),
        (1.5, (0.85, 0.55, 0.20))
    ]:
        desenhar_cubo(
            (x, -0.35, -1.2),
            (0.18, 0.25, 0.18),
            cor
        )

        desenhar_cubo(
            (x, -0.05, -1.2),
            (0.08, 0.06, 0.08),
            (0.20, 0.22, 0.24)
        )

    # Suporte de tubos de ensaio
    desenhar_cubo(
        (0.5, -0.40, -0.2),
        (0.55, 0.08, 0.25),
        (0.25, 0.18, 0.12)
    )

    # Tubos simplificados
    for x in (0.15, 0.5, 0.85):
        desenhar_cubo(
            (x, -0.20, -0.2),
            (0.09, 0.15, 0.09),
            (0.35, 0.75, 0.85)
        )


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

    desenhar_laboratorio()

    glUseProgram(0)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def mover_camera(window, key, scancode, action, mods):
    global camera_pos, camera_alvo

    if action not in (glfw.PRESS, glfw.REPEAT):
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

    glfw.set_framebuffer_size_callback(
        window, redimensionar_janela
    )

    init()

    glfw.set_mouse_button_callback(window, botao_mouse)
    glfw.set_cursor_pos_callback(window, mover_mouse)
    glfw.set_scroll_callback(window, zoom_camera)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
