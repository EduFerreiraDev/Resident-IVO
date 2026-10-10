import glfw
from OpenGL.GL import *
import numpy as np
import ctypes

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
    (0, 1, 2),  
    (0, 2, 3),
    (4, 5, 6),
    (4, 6, 7),
    (0, 1, 5),
    (0, 5, 4),
    (2, 3, 7),
    (2, 7, 6),
    (1, 2, 6),
    (1, 6, 5),
    (0, 3, 7),
    (0, 7, 4)
]

vertices_desenho = []

for triangulo in indices:
    for indice in triangulo:
        vertices_desenho.append(vertices[indice])

vertices_array = np.array(vertices_desenho, dtype=np.float32)
vaoId = 0

# Função para configurações iniciais
def init():
    global vaoId
    glClearColor(1, 1, 1, 1)

    vaoId = glGenVertexArrays(1)
    glBindVertexArray(vaoId)

    vboId = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vboId)
    glBufferData(GL_ARRAY_BUFFER, vertices_array.nbytes, vertices_array, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3*4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

# Função para atualizar a renderização
def render():
    glClear(GL_COLOR_BUFFER_BIT)

    glBindVertexArray(vaoId)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices_desenho))

    glBindVertexArray(0)

# Função Principal
def main():
    glfw.init()
    window = glfw.create_window(800, 600, "Resident IVO", None, None)
    glfw.make_context_current(window)
    init()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()