import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy as np
import ctypes
import glm
from pathlib import Path

from src.core.camera import Camera
from src.entities.laboratorio import construir_laboratorio

vertices = [
    (1, 1, 1), (-1, 1, 1), (-1, -1, 1), (1, -1, 1),
    (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1)
]
indices = [
    (0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7),
    (0, 1, 5), (0, 5, 4), (2, 3, 7), (2, 7, 6),
    (1, 2, 6), (1, 6, 5), (0, 3, 7), (0, 7, 4)
]

vertices_array = np.array(vertices, dtype=np.float32)
indices_array = np.array(indices, dtype=np.uint8).flatten()
total_indices = indices_array.size

# Variáveis globais de controle
vaoId, shaderId = 0, 0
modelo_loc, visualizacao_loc, projecao_loc, cor_loc = -1, -1, -1, -1
projecao = glm.mat4(1.0)
cubos = []
camera = Camera()

arrastando_mouse = False
mouse_x_anterior, mouse_y_anterior = 0.0, 0.0

def configurar_cursor(window, modo_primeira_pessoa):
    global mouse_x_anterior, mouse_y_anterior

    modo_cursor = (
        glfw.CURSOR_DISABLED
        if modo_primeira_pessoa
        else glfw.CURSOR_NORMAL
    )
    glfw.set_input_mode(window, glfw.CURSOR, modo_cursor)
    mouse_x_anterior, mouse_y_anterior = glfw.get_cursor_pos(window)

def mouse_button_callback(window, button, action, mods):
    global arrastando_mouse, mouse_x_anterior, mouse_y_anterior
    if button != glfw.MOUSE_BUTTON_LEFT: return
    if action == glfw.PRESS:
        arrastando_mouse = True
        mouse_x_anterior, mouse_y_anterior = glfw.get_cursor_pos(window)
    elif action == glfw.RELEASE:
        arrastando_mouse = False

def cursor_position_callback(window, xpos, ypos):
    global mouse_x_anterior, mouse_y_anterior
    diferenca_x = xpos - mouse_x_anterior
    diferenca_y = ypos - mouse_y_anterior
    mouse_x_anterior, mouse_y_anterior = xpos, ypos
    sensibilidade = 0.25

    if camera.modo_primeira_pessoa:
        camera.fp_yaw += diferenca_x * sensibilidade
        camera.fp_pitch = max(-89.0, min(89.0, camera.fp_pitch - diferenca_y * sensibilidade))
        camera.atualizar_view()
        return

    if not arrastando_mouse: return
    camera.yaw -= diferenca_x * sensibilidade
    camera.pitch -= diferenca_y * sensibilidade
    camera.atualizar_orbita()

def key_callback(window, key, scancode, action, mods):
    if action not in (glfw.PRESS, glfw.REPEAT): return

    if key == glfw.KEY_1:
        if not camera.modo_primeira_pessoa:
            camera.modo_primeira_pessoa = True
        configurar_cursor(window, True)
        camera.atualizar_view()
        atualizar_projecao(*glfw.get_framebuffer_size(window))
        return
    if key == glfw.KEY_3:
        if camera.modo_primeira_pessoa:
            camera.modo_primeira_pessoa = False
            configurar_cursor(window, False)
        camera.atualizar_view()
        atualizar_projecao(*glfw.get_framebuffer_size(window))
        return

    passo = 0.25
    movimentos = {
        glfw.KEY_LEFT: glm.vec3(-passo, 0.0, 0.0),
        glfw.KEY_RIGHT: glm.vec3(passo, 0.0, 0.0),
        glfw.KEY_UP: glm.vec3(0.0, passo, 0.0),
        glfw.KEY_DOWN: glm.vec3(0.0, -passo, 0.0),
    }
    if key in movimentos:
        camera.pos += movimentos[key]
        camera.alvo += movimentos[key]
        camera.atualizar_view()

def scroll_callback(window, xoffset, yoffset):
    if camera.modo_primeira_pessoa or yoffset == 0: return
    fator = 0.9 if yoffset > 0 else 1.1
    camera.distancia = max(3.0, min(30.0, camera.distancia * fator))
    camera.atualizar_orbita()

def atualizar_projecao(largura, altura):
    global projecao
    if altura == 0: return
    fov = 55.0 if camera.modo_primeira_pessoa else 45.0
    projecao = glm.perspective(glm.radians(fov), largura / altura, 0.1, 100.0)
    glViewport(0, 0, largura, altura)

def init():
    global vaoId, shaderId, modelo_loc, visualizacao_loc, projecao_loc, cor_loc, cubos

    glClearColor(0.12, 0.16, 0.20, 1.0)
    glEnable(GL_DEPTH_TEST)

    vaoId = glGenVertexArrays(1)
    glBindVertexArray(vaoId)

    vboId = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vboId)
    glBufferData(GL_ARRAY_BUFFER, vertices_array.nbytes, vertices_array, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    eboId = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, eboId)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_array.nbytes, indices_array, GL_STATIC_DRAW)
    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # Carregar Shaders da pasta shaders/
    root_dir = Path(__file__).resolve().parent
    with open(root_dir / "shaders/cubo_vert.glsl", "r", encoding="utf-8") as f: vs_src = f.read()
    with open(root_dir / "shaders/cubo_frag.glsl", "r", encoding="utf-8") as f: fs_src = f.read()

    vsId = gls.compileShader(vs_src, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fs_src, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

    modelo_loc = glGetUniformLocation(shaderId, "modelo")
    visualizacao_loc = glGetUniformLocation(shaderId, "visualizacao")
    projecao_loc = glGetUniformLocation(shaderId, "projecao")
    cor_loc = glGetUniformLocation(shaderId, "corObjeto")

    cubos = construir_laboratorio()

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(shaderId)

    glUniformMatrix4fv(visualizacao_loc, 1, GL_FALSE, glm.value_ptr(camera.view_matrix))
    glUniformMatrix4fv(projecao_loc, 1, GL_FALSE, glm.value_ptr(projecao))

    glBindVertexArray(vaoId)
    for cubo in cubos:
        cubo.desenhar(modelo_loc, cor_loc, total_indices)
    glBindVertexArray(0)
    glUseProgram(0)

def main():
    if not glfw.init(): raise RuntimeError("Erro ao inicializar GLFW")
    window = glfw.create_window(800, 600, "Laboratorio 3D - Resident IVO", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Erro ao criar janela")

    glfw.make_context_current(window)
    configurar_cursor(window, camera.modo_primeira_pessoa)
    glfw.swap_interval(1)

    glfw.set_framebuffer_size_callback(window, lambda w, sw, sh: atualizar_projecao(sw, sh))
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)

    init()
    atualizar_projecao(*glfw.get_framebuffer_size(window))

    ultimo_tempo = glfw.get_time()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        agora = glfw.get_time()
        delta_tempo = agora - ultimo_tempo
        ultimo_tempo = agora

        camera.mover_fp(window, delta_tempo, glfw, cubos)
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()