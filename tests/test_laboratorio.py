import unittest
import glm

from src.entities.cubo import Cubo
from src.entities.objeto_movel import ObjetoMovel
from src.entities.laboratorio import construir_laboratorio, LIMITE_INTERIOR
from src.game.validacao import Validacao
from src.game.organizador import Organizador
from src.core.camera import Camera


class LaboratorioTests(unittest.TestCase):
    def setUp(self):
        self.cubos, self.objetos = construir_laboratorio()
        self.validacao = Validacao(self.objetos)

    def organizar(self):
        for objeto in self.validacao.obrigatorios:
            objeto.posicionar_base(objeto.destino)

    def test_equipamentos_e_destinos(self):
        nomes = {o.identificador for o in self.validacao.obrigatorios}
        self.assertTrue({'microscopio', 'computador', 'cadeira', 'bequer',
                         'suporte', 'tubo_1', 'tubo_2', 'tubo_3',
                         'frasco_1', 'frasco_2', 'frasco_3'} <= nomes)
        self.assertEqual(self.validacao.corretos, 0)

    def test_posicao_orientacao_e_altura_sao_validadas(self):
        objeto = next(o for o in self.objetos if o.identificador == 'microscopio')
        objeto.posicionar_base(objeto.destino)
        self.assertTrue(self.validacao.correto(objeto))
        objeto.mover_por(glm.vec3(0, -1, 0))
        self.assertFalse(self.validacao.correto(objeto))
        objeto.posicionar_base(objeto.destino)
        objeto.rotacionar(90)
        self.assertFalse(self.validacao.correto(objeto))
        objeto.rotacionar(-90)
        self.assertTrue(self.validacao.correto(objeto))

    def test_experimento_bloqueado_ate_organizar_e_conclui(self):
        self.assertFalse(self.validacao.iniciar_experimento(10))
        self.organizar()
        self.assertEqual(self.validacao.corretos, 11)
        self.assertTrue(self.validacao.iniciar_experimento(10))
        self.assertFalse(self.validacao.iniciar_experimento(11))
        self.validacao.atualizar(12)
        self.assertEqual(self.validacao.estado, 'executando')
        self.validacao.atualizar(16)
        self.assertEqual(self.validacao.estado, 'concluido')

    def test_tubos_dependem_do_suporte(self):
        tubo = next(o for o in self.objetos if o.identificador == 'tubo_1')
        suporte = next(o for o in self.objetos if o.identificador == 'suporte')
        tubo.posicionar_base(tubo.destino)
        self.assertFalse(self.validacao.correto(tubo))
        suporte.posicionar_base(suporte.destino)
        self.assertTrue(self.validacao.correto(tubo))

    def test_rotacao_e_escala_preservam_base_e_limites(self):
        objeto = ObjetoMovel([Cubo((0, 0.2, 0), (0.4, 0.2, 0.1), (1, 1, 1))])
        objeto.rotacionar(90)
        minimo, maximo = objeto.limites()
        self.assertAlmostEqual(maximo.x - minimo.x, 0.2, places=5)
        self.assertAlmostEqual(maximo.z - minimo.z, 0.8, places=5)
        objeto.redimensionar(1.2)
        self.assertAlmostEqual(objeto.limites()[0].y, 0, places=5)
        for _ in range(50):
            objeto.redimensionar(0.5)
        self.assertGreaterEqual(objeto.fator_escala, 0.75)

    def test_retirar_objeto_cancela_experimento(self):
        self.organizar()
        self.validacao.iniciar_experimento(0)
        self.validacao.obrigatorios[0].mover_por(glm.vec3(3, 0, 0))
        self.validacao.atualizar(1)
        self.assertEqual(self.validacao.estado, 'organizacao')

    def test_todos_destinos_sao_livres_e_encaixam(self):
        organizador = Organizador(self.objetos, self.cubos)
        for objeto in self.validacao.obrigatorios:
            objeto.posicionar_base(objeto.destino + glm.vec3(0.15, 0, 0))
            organizador.objeto_arrastado = objeto
            organizador.encerrar_arraste()
            self.assertTrue(self.validacao.correto(objeto), objeto.nome)
            self.assertTrue(organizador._pode_ocupar(objeto), objeto.nome)

    def test_transformacao_na_parede_reverte_sem_deformar(self):
        objeto = next(o for o in self.objetos if o.identificador == 'computador')
        objeto.posicionar_base((LIMITE_INTERIOR - 0.5, -2.4, 0))
        organizador = Organizador(self.objetos, self.cubos)
        base = glm.vec3(objeto.base)
        # Aumentar alem do limite deve ser rejeitado sem alterar o estado.
        objeto.posicionar_base((LIMITE_INTERIOR - 0.49, -2.4, 0))
        base = glm.vec3(objeto.base)
        self.assertFalse(organizador.transformar(objeto, fator=1.25))
        self.assertAlmostEqual(objeto.fator_escala, 1.0)
        self.assertLess(glm.length(objeto.base-base), 0.00001)

    def test_arrastar_microscopio_com_cursor_sobre_marcador(self):
        camera = Camera()
        projecao = glm.perspective(glm.radians(45), 1280 / 800, 0.1, 100)
        organizador = Organizador(self.objetos, self.cubos)
        objeto = self.validacao.por_id['microscopio']
        def tela(posicao):
            p = glm.project(posicao, camera.view_matrix, projecao, glm.vec4(0, 0, 1280, 800))
            return p.x, 800 - p.y
        inicio = tela(objeto.base + glm.vec3(0, 0.3, 0))
        destino = tela(objeto.destino)
        self.assertIs(organizador.selecionar(*inicio, 1280, 800, camera, projecao), objeto)
        self.assertTrue(organizador.iniciar_arraste(objeto, *inicio, 1280, 800, camera, projecao))
        for passo in range(1, 61):
            t = passo / 60
            ponto = [inicio[i] * (1-t) + destino[i]*t for i in range(2)]
            organizador.atualizar_arraste(*ponto, 1280, 800, camera, projecao)
        organizador.encerrar_arraste()
        self.assertTrue(self.validacao.correto(objeto), str(objeto.base))

    def test_arrastar_os_onze_equipamentos_ate_seus_destinos(self):
        camera = Camera()
        projecao = glm.perspective(glm.radians(45), 1280 / 800, 0.1, 100)
        organizador = Organizador(self.objetos, self.cubos)
        def tela(posicao):
            p = glm.project(posicao, camera.view_matrix, projecao, glm.vec4(0, 0, 1280, 800))
            return p.x, 800-p.y
        for objeto in self.validacao.obrigatorios:
            minimo, maximo = objeto.limites()
            inicio = tela((minimo + maximo) / 2)
            destino = tela(objeto.destino)
            self.assertIs(organizador.selecionar(*inicio, 1280, 800, camera, projecao), objeto, objeto.nome)
            self.assertTrue(organizador.iniciar_arraste(objeto, *inicio, 1280, 800, camera, projecao))
            # A cadeira contorna a bancada, respeitando as colisoes dos equipamentos.
            caminho = ([tela(glm.vec3(-3.7, -2.4, 2.1)), tela(glm.vec3(5.4, -2.4, 2.1)),
                         tela(glm.vec3(5.4, -2.4, -3.0)), destino]
                        if objeto.identificador == 'cadeira' else [destino])
            for fim in caminho:
                for passo in range(1, 101):
                    t = passo / 100
                    ponto = [inicio[i]*(1-t) + fim[i]*t for i in range(2)]
                    organizador.atualizar_arraste(*ponto, 1280, 800, camera, projecao)
                inicio = fim
            organizador.encerrar_arraste()
            self.assertTrue(self.validacao.correto(objeto), f'{objeto.nome}: {objeto.base}')

    def test_suporte_deve_estar_organizado_antes_do_encaixe_do_tubo(self):
        tubo = self.validacao.por_id['tubo_1']
        tubo.posicionar_base((tubo.destino.x, -2.4, tubo.destino.z))
        organizador = Organizador(self.objetos, self.cubos)
        organizador.objeto_arrastado = tubo
        organizador.encerrar_arraste()
        self.assertAlmostEqual(tubo.base.y, -2.4, places=4)


if __name__ == '__main__':
    unittest.main()
