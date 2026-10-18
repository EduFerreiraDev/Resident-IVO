class ObjetoMovel:
    def __init__(self, partes, eh_mesa=False, tampo=None):
        self.partes = list(partes)
        self.eh_mesa = eh_mesa
        self.tampo = tampo

    def mover_por(self, deslocamento):
        for parte in self.partes:
            parte.posicao += deslocamento
            parte.atualizar_modelo()