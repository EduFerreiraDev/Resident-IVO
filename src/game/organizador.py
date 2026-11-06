import glm
from src.entities.laboratorio import LIMITE_INTERIOR


class Organizador:
    def __init__(self, objetos_moveis, cubos):
        self.objetos_moveis = objetos_moveis
        self.cubos = cubos
        self.mesa = next(
            objeto for objeto in objetos_moveis if objeto.eh_mesa
        )
        self.objeto_arrastado = None
        self.superficies = [c for c in cubos if c.apoio]
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

        origem = glm.vec3(camera.fp_pos if camera.modo_primeira_pessoa else camera.pos)
        direcao = glm.normalize(glm.vec3(ponto_longe) - origem)

        objeto_selecionado = None
        menor_distancia = float("inf")

        for objeto in self.objetos_moveis:
            if objeto.eh_mesa:
                continue
            
            for parte in objeto.partes:
                distancia = self._interseccao_caixa(
                    origem,
                    direcao,
                    *parte.limites(),
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
        ponto = self._interseccao_plano(raio, objeto.base.y)

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

        # Projetar no apoio visivel sob o cursor, em vez de sempre usar o piso.
        candidatos = []
        for superficie in self.superficies:
            alto = superficie.posicao.y + superficie.escala.y
            interseccao = self._interseccao_plano(raio, alto)
            if interseccao is not None and (
                abs(interseccao.x - superficie.posicao.x) + meia_largura <= superficie.escala.x
                and abs(interseccao.z - superficie.posicao.z) + meia_profundidade <= superficie.escala.z
            ):
                candidatos.append(interseccao)
        if candidatos:
            ponto = min(candidatos, key=lambda p: glm.length(p - raio[0]))

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

        apoios = [c for c in self.superficies
                  if novo_x_min >= c.posicao.x - c.escala.x
                  and novo_x_max <= c.posicao.x + c.escala.x
                  and novo_z_min >= c.posicao.z - c.escala.z
                  and novo_z_max <= c.posicao.z + c.escala.z]
        # Tubos podem apoiar no suporte quando este ja esta em seu destino.
        suporte = next((o for o in self.objetos_moveis
                        if o.identificador == 'suporte'), None)
        altura_base = max((c.posicao.y + c.escala.y for c in apoios), default=-2.4)
        if (self.objeto_arrastado.depende_de and suporte is not None
                and glm.length(suporte.base - suporte.destino) < 0.1
                and abs(centro_x - suporte.base.x) < 0.5
                and abs(centro_z - suporte.base.z) < 0.2):
            altura_base = -0.34
        esta_sobre_bancada = altura_base > -2.4

        # Facilitar a precisao: aproximar o cursor da propria marca encaixa o item.
        objeto = self.objeto_arrastado
        if objeto.destino is not None and self._dependencia_pronta(objeto):
            alvo = self._interseccao_plano(raio, objeto.destino.y)
            if alvo is not None and abs(alvo.x - objeto.destino.x) < 0.45 and abs(alvo.z - objeto.destino.z) < 0.45:
                centro_x, centro_z = objeto.destino.x, objeto.destino.z
                altura_base = objeto.destino.y
                esta_sobre_bancada = altura_base > -2.4

        centro_atual_x = (x_min + x_max) / 2.0
        centro_atual_z = (z_min + z_max) / 2.0

        deslocamento = glm.vec3(
            centro_x - centro_atual_x,
            altura_base - y_min,
            centro_z - centro_atual_z,
        )
        deslocamento_aplicado = self._mover_com_colisao(
            self.objeto_arrastado,
            deslocamento,
            permitir_apoiar_na_mesa=esta_sobre_bancada and deslocamento.y > 0,
        )

        if self.objeto_arrastado.eh_mesa:
            for objeto in self.objetos_sobre_mesa:
                objeto.mover_por(deslocamento_aplicado)

    def encerrar_arraste(self):
        objeto = self.objeto_arrastado
        self.objeto_arrastado = None
        if objeto is not None and objeto.destino is not None and self._dependencia_pronta(objeto):
            delta = objeto.base - objeto.destino
            if abs(delta.x) < 0.65 and abs(delta.z) < 0.65:
                anterior = glm.vec3(objeto.base)
                objeto.posicionar_base(objeto.destino)
                if not self._pode_ocupar(objeto):
                    objeto.posicionar_base(anterior)
        return objeto

    def _dependencia_pronta(self, objeto):
        if not objeto.depende_de:
            return True
        suporte = next(o for o in self.objetos_moveis if o.identificador == objeto.depende_de)
        erro = abs((suporte.angulo - (suporte.orientacao or 0) + 180) % 360 - 180)
        return glm.length(suporte.base - suporte.destino) < 0.08 and erro <= 20

    def _pode_ocupar(self, objeto):
        minimo, maximo = objeto.limites()
        if (minimo.x < -LIMITE_INTERIOR or maximo.x > LIMITE_INTERIOR
                or minimo.z < -LIMITE_INTERIOR or maximo.z > LIMITE_INTERIOR
                or minimo.y < -2.401 or maximo.y > 2.39):
            return False
        for parte in objeto.partes:
            a, b = parte.limites()
            for cubo in self.cubos:
                if not cubo.colisao_ativa or any(cubo is p for p in objeto.partes):
                    continue
                c, d = cubo.limites()
                if all(a[i] < d[i] - 0.001 and b[i] > c[i] + 0.001 for i in range(3)):
                    return False
        return True

    def transformar(self, objeto, graus=0, fator=1):
        if objeto is None or objeto.eh_mesa:
            return False
        base = glm.vec3(objeto.base)
        angulo, escala = objeto.angulo, objeto.fator_escala
        objeto.rotacionar(graus)
        objeto.redimensionar(fator)
        if self._pode_ocupar(objeto):
            return True
        objeto.angulo, objeto.fator_escala = angulo, escala
        objeto._transformar(base)
        return False

    def _mover_com_colisao(
        self, objeto, deslocamento, permitir_apoiar_na_mesa
    ):
        aplicado = glm.vec3(0.0)

        eixos = ("y", "x", "z") if deslocamento.y > 0 else ("x", "z", "y")
        for eixo in eixos:
            movimento = getattr(deslocamento, eixo)
            if movimento == 0:
                continue

            permitido = movimento
            eixos_transversais = [
                outro for outro in ("x", "y", "z") if outro != eixo
            ]

            for parte in objeto.partes:
                minimo, maximo = parte.limites()

                for cubo in self.cubos:
                    if not cubo.colisao_ativa:
                        continue
                    if any(cubo is p for p in objeto.partes):
                        continue
                    if permitir_apoiar_na_mesa and (cubo in self.superficies or any(cubo is p for o in self.objetos_moveis if o.identificador == "suporte" for p in o.partes)):
                        continue

                    cubo_minimo, cubo_maximo = cubo.limites()

                    sobrepoe_transversalmente = all(
                        getattr(minimo, outro) < getattr(cubo_maximo, outro)
                        and getattr(maximo, outro) > getattr(cubo_minimo, outro)
                        for outro in eixos_transversais
                    )
                    if not sobrepoe_transversalmente:
                        continue

                    if movimento > 0:
                        distancia = (
                            getattr(cubo_minimo, eixo)
                            - getattr(maximo, eixo)
                        )
                        if 0 <= distancia < permitido:
                            permitido = distancia
                    else:
                        distancia = (
                            getattr(cubo_maximo, eixo)
                            - getattr(minimo, eixo)
                        )
                        if permitido < distancia <= 0:
                            permitido = distancia

            passo = glm.vec3(0.0)
            setattr(passo, eixo, permitido)
            objeto.mover_por(passo)
            setattr(aplicado, eixo, permitido)

        return aplicado

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

        origem = glm.vec3(camera.fp_pos if camera.modo_primeira_pessoa else camera.pos)
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
        minimo, maximo = objeto.limites()
        return minimo.x, maximo.x, minimo.y, minimo.z, maximo.z

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
