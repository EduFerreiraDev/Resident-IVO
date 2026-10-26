import glm
from src.entities.laboratorio import LIMITE_INTERIOR


class Organizador:
    def __init__(self, objetos_moveis):
        self.objetos_moveis = objetos_moveis
        self.mesa = next(
            objeto for objeto in objetos_moveis if objeto.eh_mesa
        )
        self.objeto_arrastado = None
        self.objetos_sobre_mesa = []
        self.deslocamento_cursor_x = 0.0
        self.deslocamento_cursor_z = 0.0

    def selecionar(self, cursor_x, cursor_y, largura, altura, camera, projecao):
        if largura <= 0 or altura <= 0:
            return None

        x_ndc = 2.0 * cursor_x / largura - 1.0
        y_ndc = 1.0 - 2.0 * cursor_y / altura

        inversa = glm.inverse(projecao * camera.view_matrix)

        ponto_perto = inversa * glm.vec4(x_ndc, y_ndc, -1.0, 1.0)
        ponto_longe = inversa * glm.vec4(x_ndc, y_ndc, 1.0, 1.0)

        ponto_perto /= ponto_perto.w
        ponto_longe /= ponto_longe.w

        origem = glm.vec3(camera.pos)
        direcao = glm.normalize(glm.vec3(ponto_longe) - origem)

        objeto_selecionado = None
        menor_distancia = float("inf")

        for objeto in self.objetos_moveis:
            for parte in objeto.partes:
                distancia = self._interseccao_caixa(
                    origem,
                    direcao,
                    parte.posicao - parte.escala,
                    parte.posicao + parte.escala,
                )

                if distancia is not None and distancia < menor_distancia:
                    menor_distancia = distancia
                    objeto_selecionado = objeto

        return objeto_selecionado
    def iniciar_arraste(
        self, objeto, cursor_x, cursor_y, largura, altura, camera, projecao
    ):
        if largura <= 0 or altura <= 0:
            return False

        raio = self._obter_raio(
            cursor_x, cursor_y, largura, altura, camera, projecao
        )
        ponto = self._interseccao_plano(raio, -2.4)

        if ponto is None:
            return False

        x_min, x_max, _, z_min, z_max = self._limites_objeto(objeto)
        centro_x = (x_min + x_max) / 2.0
        centro_z = (z_min + z_max) / 2.0

        self.deslocamento_cursor_x = centro_x - ponto.x
        self.deslocamento_cursor_z = centro_z - ponto.z
        self.objeto_arrastado = objeto
        if objeto.eh_mesa:
            self.objetos_sobre_mesa = self._encontrar_objetos_sobre_mesa()
        else:
            self.objetos_sobre_mesa = []

        return True

    def atualizar_arraste(
        self, cursor_x, cursor_y, largura, altura, camera, projecao
    ):
        if self.objeto_arrastado is None or largura <= 0 or altura <= 0:
            return

        raio = self._obter_raio(
            cursor_x, cursor_y, largura, altura, camera, projecao
        )
        ponto = self._interseccao_plano(raio, -2.4)

        if ponto is None:
            return

        x_min, x_max, y_min, z_min, z_max = self._limites_objeto(
            self.objeto_arrastado
        )

        meia_largura = (x_max - x_min) / 2.0
        meia_profundidade = (z_max - z_min) / 2.0

        centro_x = ponto.x + self.deslocamento_cursor_x
        centro_z = ponto.z + self.deslocamento_cursor_z

        centro_x = max(
            -LIMITE_INTERIOR + meia_largura,
            min(LIMITE_INTERIOR - meia_largura, centro_x),
        )
        centro_z = max(
            -LIMITE_INTERIOR + meia_profundidade,
            min(LIMITE_INTERIOR - meia_profundidade, centro_z),
        )

        novo_x_min = centro_x - meia_largura
        novo_x_max = centro_x + meia_largura
        novo_z_min = centro_z - meia_profundidade
        novo_z_max = centro_z + meia_profundidade

        tampo = self.mesa.tampo
        esta_sobre_bancada = (
            not self.objeto_arrastado.eh_mesa
            and novo_x_min >= tampo.posicao.x - tampo.escala.x
            and novo_x_max <= tampo.posicao.x + tampo.escala.x
            and novo_z_min >= tampo.posicao.z - tampo.escala.z
            and novo_z_max <= tampo.posicao.z + tampo.escala.z
        )

        if self.objeto_arrastado.eh_mesa:
            altura_base = -2.4
        elif esta_sobre_bancada:
            altura_base = tampo.posicao.y + tampo.escala.y
        else:
            altura_base = -2.4

        centro_atual_x = (x_min + x_max) / 2.0
        centro_atual_z = (z_min + z_max) / 2.0

        deslocamento = glm.vec3(
            centro_x - centro_atual_x,
            altura_base - y_min,
            centro_z - centro_atual_z,
        )
        self.objeto_arrastado.mover_por(deslocamento)

        if self.objeto_arrastado.eh_mesa:
            for objeto in self.objetos_sobre_mesa:
                objeto.mover_por(deslocamento)

    def encerrar_arraste(self):
        self.objeto_arrastado = None

    def _encontrar_objetos_sobre_mesa(self):
        tampo = self.mesa.tampo
        topo = tampo.posicao.y + tampo.escala.y
        limite_x_min = tampo.posicao.x - tampo.escala.x
        limite_x_max = tampo.posicao.x + tampo.escala.x
        limite_z_min = tampo.posicao.z - tampo.escala.z
        limite_z_max = tampo.posicao.z + tampo.escala.z
        epsilon = 0.03

        objetos_apoiados = []

        for objeto in self.objetos_moveis:
            if objeto.eh_mesa:
                continue

            x_min, x_max, y_min, z_min, z_max = self._limites_objeto(objeto)
            apoiado_no_tampo = (
                abs(y_min - topo) <= epsilon
                and x_min >= limite_x_min
                and x_max <= limite_x_max
                and z_min >= limite_z_min
                and z_max <= limite_z_max
            )

            if apoiado_no_tampo:
                objetos_apoiados.append(objeto)

        return objetos_apoiados

    @staticmethod
    def _obter_raio(
        cursor_x, cursor_y, largura, altura, camera, projecao
    ):
        x_ndc = 2.0 * cursor_x / largura - 1.0
        y_ndc = 1.0 - 2.0 * cursor_y / altura
        inversa = glm.inverse(projecao * camera.view_matrix)

        ponto_longe = inversa * glm.vec4(x_ndc, y_ndc, 1.0, 1.0)
        ponto_longe /= ponto_longe.w

        origem = glm.vec3(camera.pos)
        direcao = glm.normalize(glm.vec3(ponto_longe) - origem)
        return origem, direcao

    @staticmethod   
    def _interseccao_plano(raio, altura_plano):
        origem, direcao = raio

        if abs(direcao.y) < 1e-8:
            return None

        distancia = (altura_plano - origem.y) / direcao.y
        if distancia < 0.0:
            return None

        return origem + direcao * distancia

    @staticmethod
    def _limites_objeto(objeto):
        return (
            min(parte.posicao.x - parte.escala.x for parte in objeto.partes),
            max(parte.posicao.x + parte.escala.x for parte in objeto.partes),
            min(parte.posicao.y - parte.escala.y for parte in objeto.partes),
            min(parte.posicao.z - parte.escala.z for parte in objeto.partes),
            max(parte.posicao.z + parte.escala.z for parte in objeto.partes),
        )
    

    @staticmethod
    def _interseccao_caixa(origem, direcao, minimo, maximo):
        distancia_perto = 0.0
        distancia_longe = float("inf")

        for eixo in ("x", "y", "z"):
            origem_eixo = getattr(origem, eixo)
            direcao_eixo = getattr(direcao, eixo)
            minimo_eixo = getattr(minimo, eixo)
            maximo_eixo = getattr(maximo, eixo)

            if abs(direcao_eixo) < 1e-8:
                if origem_eixo < minimo_eixo or origem_eixo > maximo_eixo:
                    return None
                continue

            distancia_1 = (minimo_eixo - origem_eixo) / direcao_eixo
            distancia_2 = (maximo_eixo - origem_eixo) / direcao_eixo

            distancia_perto = max(
                distancia_perto,
                min(distancia_1, distancia_2),
            )
            distancia_longe = min(
                distancia_longe,
                max(distancia_1, distancia_2),
            )

            if distancia_perto > distancia_longe:
                return None

        return distancia_perto
