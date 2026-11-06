import glm


class Validacao:
    DURACAO = 5.0

    def __init__(self, objetos):
        self.obrigatorios = [o for o in objetos if o.destino is not None]
        self.por_id = {o.identificador: o for o in self.obrigatorios}
        self.estado = 'organizacao'
        self.inicio = None
        self.mensagem = 'Organize os equipamentos nas areas indicadas. H: ajuda.'

    def correto(self, objeto):
        if objeto.destino is None:
            return False
        if objeto.depende_de and not self.correto(self.por_id[objeto.depende_de]):
            return False
        delta = objeto.base - objeto.destino
        tolerancia = 0.12 if objeto.identificador.startswith('tubo_') else 0.23
        if abs(delta.x) > tolerancia or abs(delta.z) > tolerancia or abs(delta.y) > 0.08:
            return False
        if objeto.orientacao is not None:
            erro = abs((objeto.angulo - objeto.orientacao + 180) % 360 - 180)
            if erro > 20:
                return False
        return True

    @property
    def corretos(self):
        return sum(self.correto(o) for o in self.obrigatorios)

    @property
    def organizado(self):
        return bool(self.obrigatorios) and self.corretos == len(self.obrigatorios)

    def iniciar_experimento(self, agora):
        if self.estado != 'organizacao':
            return False
        if not self.organizado:
            self.mensagem = 'Experimento bloqueado: organize todos os equipamentos.'
            return False
        self.inicio = agora
        self.estado = 'executando'
        self.mensagem = 'Experimento em andamento. Aguarde a reacao no bequer.'
        return True

    def atualizar(self, agora):
        if self.estado == 'executando':
            if not self.organizado:
                self.estado = 'organizacao'
                self.inicio = None
                self.mensagem = 'Experimento cancelado: equipamento fora do lugar.'
            elif agora - self.inicio >= self.DURACAO:
                self.estado = 'concluido'
                self.mensagem = 'Experimento concluido! Laboratorio preparado com sucesso.'

    def progresso(self, agora):
        if self.inicio is None:
            return 0.0
        return max(0.0, min(1.0, (agora - self.inicio) / self.DURACAO))
