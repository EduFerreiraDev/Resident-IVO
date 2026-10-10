import glfw
from OpenGL.GL import *

# Função para configurações iniciais
def init():
    glClearColor(1, 1, 1, 1)

# Função para atualizar a renderização
def render():
    glClear(GL_COLOR_BUFFER_BIT)

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