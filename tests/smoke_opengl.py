"""Teste com contexto real e janela invisivel; executar separadamente."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import glfw
from OpenGL.GL import glGetError, glReadPixels, GL_RGB, GL_UNSIGNED_BYTE
import main


assert glfw.init(), 'GLFW nao iniciou'
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
window = glfw.create_window(1280, 800, 'Verificacao Resident IVO', None, None)
assert window, 'Contexto OpenGL 3.3 indisponivel'
try:
    glfw.make_context_current(window)
    main.init()
    main.atualizar_projecao(1280, 800)
    main.render(window)
    assert glGetError() == 0, 'Erro na renderizacao inicial'
    pixels = glReadPixels(0, 0, 1280, 800, GL_RGB, GL_UNSIGNED_BYTE)
    # PPM permite verificar a imagem sem adicionar uma dependencia ao projeto.
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('preview.ppm')
    caminho.write_bytes(b'P6\n1280 800\n255\n' + bytes(pixels))
    for objeto in main.validacao.obrigatorios:
        objeto.posicionar_base(objeto.destino)
    assert main.validacao.organizado
    main.arrastando_mouse = True
    main.key_callback(window, glfw.KEY_ENTER, 0, glfw.PRESS, 0)
    main.mouse_button_callback(window, glfw.MOUSE_BUTTON_LEFT, glfw.RELEASE, 0)
    assert not main.arrastando_mouse, 'Soltar mouse deve encerrar orbita ao iniciar experimento'
    assert main.validacao.estado == 'executando'
    main.render(window)
    main.validacao.inicio -= 6
    main.render(window)
    assert main.validacao.estado == 'concluido'
    main.key_callback(window, glfw.KEY_1, 0, glfw.PRESS, 0)
    main.render(window)
    main.key_callback(window, glfw.KEY_3, 0, glfw.PRESS, 0)
    main.render(window)
    assert glGetError() == 0, 'Erro apos experimento ou troca de camera'
    print('OK: shaders, HUD, cena, experimento e cameras em contexto OpenGL real.')
finally:
    if main.interface:
        main.interface.fechar()
    glfw.destroy_window(window)
    glfw.terminate()
