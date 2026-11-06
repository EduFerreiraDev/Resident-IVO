import math
import glm


class ObjetoMovel:
    def __init__(self, partes, eh_mesa=False, tampo=None, identificador='',
                 nome='Caixa', destino=None, instrucao='', orientacao=None,
                 depende_de=None):
        self.partes = list(partes)
        self.eh_mesa = eh_mesa
        self.tampo = tampo
        self.identificador = identificador
        self.nome = nome
        self.destino = glm.vec3(destino) if destino is not None else None
        self.instrucao = instrucao
        self.orientacao = orientacao
        self.depende_de = depende_de
        self.angulo = 0.0
        self.fator_escala = 1.0
        minimo, maximo = self.limites()
        self._origem_inicial = glm.vec3((minimo.x + maximo.x) / 2, minimo.y,
                                      (minimo.z + maximo.z) / 2)
        self._formas = [(glm.vec3(p.posicao - self._origem_inicial),
                         glm.vec3(p.escala)) for p in self.partes]

    def limites(self):
        limites = [p.limites() for p in self.partes]
        return (glm.vec3(*(min(a[i] for a, b in limites) for i in range(3))),
                glm.vec3(*(max(b[i] for a, b in limites) for i in range(3))))

    @property
    def base(self):
        minimo, maximo = self.limites()
        return glm.vec3((minimo.x + maximo.x) / 2, minimo.y,
                        (minimo.z + maximo.z) / 2)

    def posicionar_base(self, posicao):
        self.mover_por(glm.vec3(posicao) - self.base)

    def _transformar(self, base):
        rad = math.radians(self.angulo)
        c, s = math.cos(rad), math.sin(rad)
        for parte, (local, escala) in zip(self.partes, self._formas):
            local = local * self.fator_escala
            parte.posicao = base + glm.vec3(c * local.x + s * local.z,
                                            local.y, -s * local.x + c * local.z)
            parte.escala = escala * self.fator_escala
            parte.rotacao = self.angulo
            parte.atualizar_modelo()

    def rotacionar(self, graus):
        base = self.base
        self.angulo = (self.angulo + graus) % 360
        self._transformar(base)

    def redimensionar(self, fator):
        base = self.base
        self.fator_escala = max(0.75, min(1.25, self.fator_escala * fator))
        self._transformar(base)

    def mover_por(self, deslocamento):
        for parte in self.partes:
            parte.posicao += deslocamento
            parte.atualizar_modelo()
