"""HUD em OpenGL: atlas pre-gerado, sem biblioteca de interface adicional."""
import ctypes
from pathlib import Path
import struct
import unicodedata

import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class Interface:
    def __init__(self):
        self.programa = compileProgram(compileShader('''#version 330 core
            layout(location=0) in vec2 ponto;
            layout(location=1) in vec2 uv;
            layout(location=2) in vec4 cor;
            uniform vec2 janela;
            out vec2 textura; out vec4 tinta;
            void main() {
                gl_Position=vec4(ponto.x/janela.x*2.-1.,1.-ponto.y/janela.y*2.,0,1);
                textura=uv; tinta=cor;
            }''', GL_VERTEX_SHADER), compileShader('''#version 330 core
            uniform sampler2D atlas;
            in vec2 textura; in vec4 tinta; out vec4 saida;
            void main() {
                float a = textura.x < 0. ? 1. : texture(atlas,textura).r;
                saida=vec4(tinta.rgb,tinta.a*a);
            }''', GL_FRAGMENT_SHADER))
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        for indice, tamanho, inicio in [(0, 2, 0), (1, 2, 8), (2, 4, 16)]:
            glEnableVertexAttribArray(indice)
            glVertexAttribPointer(indice, tamanho, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(inicio))
        self.textura = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textura)
        dados = (Path(__file__).resolve().parents[2] / 'assets/ui/fonte.bin').read_bytes()
        largura, altura = struct.unpack('<II', dados[:8])
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R8, largura, altura, 0, GL_RED,
                     GL_UNSIGNED_BYTE, dados[8:])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.vertices = []

    def quad(self, x, y, w, h, cor, uv=(-1, -1, -1, -1)):
        u, v, u2, v2 = uv
        for px, py, tx, ty in [(x, y, u, v), (x+w, y, u2, v), (x+w, y+h, u2, v2),
                                (x, y, u, v), (x+w, y+h, u2, v2), (x, y+h, u, v2)]:
            self.vertices.extend((px, py, tx, ty, *cor))

    def texto(self, x, y, texto, cor=(0.83, 0.90, 0.87, 1), limite=44):
        texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()
        for i, letra in enumerate(texto[:limite]):
            codigo = max(0, min(95, ord(letra) - 32))
            coluna, linha = codigo % 16, codigo // 16
            self.quad(x + i * 8, y, 9, 18, cor,
                      (coluna/16, linha/6, (coluna+1)/16, (linha+1)/6))

    def desenhar(self, largura, altura, validacao, selecionado, teto, bancada, ajuda, agora):
        if largura <= 0 or altura <= 0:
            return
        self.vertices = []
        cor_verde = (0.32, 0.9, 0.64, 1)
        cor_alerta = (1, 0.69, 0.35, 1)
        self.quad(16, 16, 304, 324, (0.025, 0.055, 0.065, 0.94))
        self.quad(16, 16, 4, 324, cor_verde)
        self.texto(30, 27, 'RESIDENT IVO / LABORATORIO', cor_verde)
        self.texto(30, 53, 'Organize os equipamentos')
        corretos, total = validacao.corretos, len(validacao.obrigatorios)
        self.texto(30, 76, f'Objetos corretos: {corretos}/{total}')
        self.quad(30, 102, 274, 5, (0.15, 0.23, 0.23, 1))
        self.quad(30, 102, 274 * corretos / max(1, total), 5, cor_verde)
        for i, objeto in enumerate(validacao.obrigatorios):
            correto = validacao.correto(objeto)
            self.texto(30, 119 + i * 18, ('[OK] ' if correto else '[  ] ') + objeto.nome,
                       cor_verde if correto else (0.65, 0.72, 0.72, 1), limite=34)

        self.quad(16, altura - 116, largura - 32, 100, (0.025, 0.055, 0.065, 0.94))
        nome = selecionado.nome if selecionado else 'nenhum (clique em um equipamento)'
        self.texto(30, altura-108, f'Selecionado: {nome}', cor_verde, limite=(largura-65)//8)
        if selecionado:
            self.texto(30, altura-86, selecionado.instrucao or 'Objeto decorativo: nao conta para a organizacao.',
                       limite=(largura-65)//8)
            self.texto(30, altura-64, f'Rotacao: {selecionado.angulo:.0f} graus | Escala: {selecionado.fator_escala:.2f}x')
        self.texto(30, altura-42, validacao.mensagem, cor_alerta, limite=(largura-65)//8)

        if ajuda and largura >= 1000:
            self.quad(largura-346, 16, 330, 238, (0.025, 0.055, 0.065, 0.94))
            linhas = ['CONTROLES / H: ocultar ajuda',
                      '3: organizar | 1: explorar',
                      'Clique e arraste: mover objeto',
                      'Arraste no vazio: orbitar camera',
                      'Roda: zoom | Setas: mover camera',
                      'Q/R: girar -/+ 15 graus',
                      'Z/X: diminuir/aumentar escala',
                      'G: mostrar/ocultar destinos',
                      'L: luz do teto | B: luz bancada',
                      'Enter: iniciar experimento',
                      'WASD + mouse: explorar | Esc: sair']
            for i, linha in enumerate(linhas):
                self.texto(largura-332, 26+i*20, linha, limite=39)
        self.texto(largura-312, altura-145,
                   f'Teto: {"ON" if teto else "OFF"} | Bancada: {"ON" if bancada else "OFF"}', limite=36)
        if validacao.estado == 'executando':
            self.quad(340, 30, max(0, largura-700) * validacao.progresso(agora), 8, cor_verde)
        glUseProgram(self.programa)
        glUniform2f(glGetUniformLocation(self.programa, 'janela'), largura, altura)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.textura)
        glUniform1i(glGetUniformLocation(self.programa, 'atlas'), 0)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        dados = np.array(self.vertices, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, dados.nbytes, dados, GL_STREAM_DRAW)
        glDrawArrays(GL_TRIANGLES, 0, dados.size // 8)
        glBindVertexArray(0)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

    def fechar(self):
        glDeleteTextures([self.textura])
        glDeleteBuffers(1, [self.vbo])
        glDeleteVertexArrays(1, [self.vao])
        glDeleteProgram(self.programa)
