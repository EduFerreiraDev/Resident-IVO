from src.entities.cubo import Cubo
from src.entities.objeto_movel import ObjetoMovel

MEIA_SALA = 8.0
LIMITE_INTERIOR = MEIA_SALA - 0.5
POSICAO_INTERRUPTOR = (MEIA_SALA - 0.28, -0.4, -1.15)
POSICAO_ALERTA = (MEIA_SALA - 0.25, 1.75, -2.5)

def construir_laboratorio():
    cubos = []
    objetos_moveis = []

    # Chão e paredes; a parede do fundo tem uma abertura para a janela.
    cubos.append(Cubo((0, -2.5, 0), (MEIA_SALA, 0.1, MEIA_SALA), (0.35, 0.38, 0.40)))
    fundo = -MEIA_SALA + 0.1
    centro_lateral = (MEIA_SALA + 2.0) / 2.0
    meia_lateral = (MEIA_SALA - 2.0) / 2.0
    cor_parede = (0.72, 0.76, 0.80)
    cubos.extend([
        Cubo((-centro_lateral, 0, fundo), (meia_lateral, 2.5, 0.1), cor_parede, parede=True),
        Cubo((centro_lateral, 0, fundo), (meia_lateral, 2.5, 0.1), cor_parede, parede=True),
        Cubo((0, -1.75, fundo), (2.0, 0.75, 0.1), cor_parede, parede=True),
        Cubo((0, 2.0, fundo), (2.0, 0.5, 0.1), cor_parede, parede=True),
        Cubo((-MEIA_SALA + 0.1, 0, 0), (0.1, 2.5, MEIA_SALA), cor_parede, parede=True),
        Cubo((MEIA_SALA - 0.1, 0, 0), (0.1, 2.5, MEIA_SALA), cor_parede, parede=True),
    ])

    # Vidro e moldura, ligeiramente à frente da parede para ficarem visíveis.
    frente_janela = fundo + 0.12
    cubos.extend([
        Cubo((0, 0.25, frente_janela), (1.9, 1.45, 0.02), (0.38, 0.68, 0.78)),
        Cubo((-1.95, 0.25, frente_janela + 0.03), (0.07, 1.55, 0.07), (0.22, 0.28, 0.32)),
        Cubo((1.95, 0.25, frente_janela + 0.03), (0.07, 1.55, 0.07), (0.22, 0.28, 0.32)),
        Cubo((0, -1.25, frente_janela + 0.03), (2.02, 0.07, 0.07), (0.22, 0.28, 0.32)),
        Cubo((0, 1.75, frente_janela + 0.03), (2.02, 0.07, 0.07), (0.22, 0.28, 0.32)),
        Cubo((0, 0.25, frente_janela + 0.04), (0.05, 1.45, 0.05), (0.22, 0.28, 0.32)),
    ])

    # Porta de contenção e sinalizador de emergência na parede direita.
    cubos.extend([
        Cubo((MEIA_SALA - 0.22, -0.55, -2.5), (0.035, 1.85, 1.05), (0.12, 0.17, 0.19)),
        Cubo((MEIA_SALA - 0.28, -0.55, -2.5), (0.04, 1.9, 0.08), (0.46, 0.28, 0.17)),
        Cubo((MEIA_SALA - 0.28, -0.55, -3.55), (0.04, 1.9, 0.08), (0.46, 0.28, 0.17)),
        Cubo((MEIA_SALA - 0.32, -0.4, -1.85), (0.07, 0.07, 0.08), (0.65, 0.65, 0.58)),
        Cubo((MEIA_SALA - 0.32, 1.75, -2.5), (0.09, 0.14, 0.22), (1.0, 0.08, 0.05)),

        # Interruptor da lâmpada do teto
        Cubo(
            POSICAO_INTERRUPTOR,
            (0.04, 0.12, 0.09),
            (0.18, 0.18, 0.16)
),
    ])

    # Armários de pesquisa, prateleiras e caixas abandonadas.
    for z in (0.7, 2.5, 4.3):
        cubos.extend([
            Cubo((-6.25, -0.65, z), (0.55, 1.75, 0.75), (0.22, 0.28, 0.29), colisivel=True),
            Cubo((-5.67, -0.65, z), (0.04, 1.6, 0.68), (0.31, 0.36, 0.35)),
            Cubo((-5.60, -0.65, z), (0.04, 0.05, 0.62), (0.42, 0.25, 0.17)),
        ])

    for x, z in ((4.8, 3.8), (5.3, 4.5), (-4.4, -3.8)):
        caixa = Cubo(
            (x, -2.05, z),
            (0.48, 0.35, 0.48),
            (0.29, 0.24, 0.19),
            colisivel=True,
        )
        cubos.append(caixa)
        objetos_moveis.append(ObjetoMovel([caixa]))

    # Marcas no piso e uma luminária fria suspensa.
    for x, z in ((-2.5, 3.4), (3.2, -3.7), (4.1, 1.8)):
        cubos.append(Cubo((x, -2.385, z), (0.7, 0.008, 0.3), (0.24, 0.13, 0.12), colisao_ativa = False))
    cubos.extend([
        Cubo((0, 2.35, 0.0), (1.1, 0.08, 0.24), (0.18, 0.22, 0.24)),
        Cubo((0, 2.25, 0.0), (0.85, 0.025, 0.15), (0.45, 0.62, 0.62)),
    ])

    # Mesa: tampo e pernas são movidos como um único objeto
    tampo_mesa = Cubo(
        (0, -0.65, -1.0),
        (2.0, 0.15, 1.0),
        (0.45, 0.27, 0.15),
        colisivel=True,
    )
    partes_mesa = [tampo_mesa]
    tampo_mesa.apoio = True

    for x in (-1.75, 1.75):
        for z in (-1.8, -0.2):
            partes_mesa.append(
                Cubo((x, -1.55, z), (0.12, 0.8, 0.12), (0.25, 0.27, 0.29))
            )

    cubos.extend(partes_mesa)
    objetos_moveis.append(
        ObjetoMovel(partes_mesa, eh_mesa=True, tampo=tampo_mesa)
    )

    # Microscópio: quatro peças que se movem juntas
    microscopio = [
        Cubo((-3.0, -2.3, -1.0), (0.4, 0.08, 0.3), (0.12, 0.18, 0.22)),
        Cubo((-3.0, -1.89, -1.0), (0.08, 0.32, 0.08), (0.15, 0.20, 0.24)),
        Cubo((-3.0, -1.6, -1.0), (0.25, 0.08, 0.12), (0.18, 0.25, 0.30)),
        Cubo((-3.18, -1.47, -1.0), (0.08, 0.12, 0.08), (0.08, 0.09, 0.10)),
    ]
    cubos.extend(microscopio)
    objetos_moveis.append(ObjetoMovel(
        microscopio, identificador='microscopio', nome='Microscopio',
        destino=(-1.15, -0.5, -1.1), orientacao=0,
        instrucao='Bancada central, lado esquerdo. Orientacao: 0 graus.'))

    # Frascos: corpo e tampa de cada um se movem juntos
    frascos = [
        (0.3, (0.20, 0.65, 0.85)),
        (0.9, (0.25, 0.75, 0.45)),
        (1.5, (0.85, 0.55, 0.20)),
    ]

    for numero, (x, cor) in enumerate(frascos, 1):
        partes_frasco = [
            Cubo((x, -2.3, 2.0), (0.18, 0.25, 0.18), cor),
            Cubo((x, -2.0, 2.0), (0.08, 0.06, 0.08), (0.20, 0.22, 0.24)),
        ]
        cubos.extend(partes_frasco)
        objetos_moveis.append(ObjetoMovel(
            partes_frasco, identificador=f'frasco_{numero}',
            nome=f'Frasco de reagente {numero}',
            destino=(-6.2 + (numero - 1) * 0.6, -0.9, -4.5),
            instrucao=f'Prateleira ao fundo, posicao {numero} da esquerda para a direita.'))

    # Suporte e tubos podem ser organizados individualmente.
    suporte_tubos = [
        Cubo((2.6, -2.3, -0.2), (0.55, 0.08, 0.25), (0.25, 0.18, 0.12))
    ]

    suporte_tubos.extend([
        Cubo((2.1, -2.13, -0.2), (0.04, 0.15, 0.24), (0.3, 0.28, 0.2)),
        Cubo((3.1, -2.13, -0.2), (0.04, 0.15, 0.24), (0.3, 0.28, 0.2)),
    ])

    cubos.extend(suporte_tubos)
    objetos_moveis.append(ObjetoMovel(
        suporte_tubos, identificador='suporte', nome='Suporte para tubos',
        destino=(0.65, -0.5, -1.35), orientacao=0,
        instrucao='Bancada central, area dos tubos. Orientacao: 0 graus.'))

    def equipamento(identificador, nome, base, destino, formas, instrucao,
                    orientacao=None, depende_de=None):
        partes = [Cubo(tuple(base[i] + local[i] for i in range(3)), tamanho, cor)
                  for local, tamanho, cor in formas]
        cubos.extend(partes)
        objetos_moveis.append(ObjetoMovel(
            partes, identificador=identificador, nome=nome, destino=destino,
            instrucao=instrucao, orientacao=orientacao, depende_de=depende_de))

    for numero in range(1, 4):
        equipamento(f'tubo_{numero}', f'Tubo de ensaio {numero}',
                    (-2.0 + numero * 0.45, -2.4, 2.8),
                    (0.65 + (numero - 2) * 0.32, -0.34, -1.35), [
                        ((0, 0.22, 0), (0.085, 0.22, 0.085), (0.25, 0.72, 0.8)),
                        ((0, 0.10, 0), (0.09, 0.10, 0.09), (0.3, 0.85, 0.45)),
                    ], 'Coloque no suporte da bancada; organize o suporte primeiro.',
                    depende_de='suporte')

    # Prateleira de reagentes e mesa do computador: superficies fixas.
    cubos.extend([
        Cubo((-5.6, -1.0, -4.5), (1.15, 0.1, 0.6), (0.26, 0.30, 0.30), colisivel=True, apoio=True),
        Cubo((-6.65, -1.7, -4.5), (0.08, 0.7, 0.5), (0.22, 0.25, 0.26)),
        Cubo((-4.55, -1.7, -4.5), (0.08, 0.7, 0.5), (0.22, 0.25, 0.26)),
        Cubo((3.8, -0.65, -4.6), (1.35, 0.15, 0.75), (0.30, 0.33, 0.32), colisivel=True, apoio=True),
    ])
    for x in (2.65, 4.95):
        for z in (-5.15, -4.05):
            cubos.append(Cubo((x, -1.5, z), (0.10, 0.9, 0.10), (0.22, 0.25, 0.24)))

    equipamento('computador', 'Computador', (3.6, -2.4, 1.1), (3.8, -0.5, -4.6), [
        ((0, 0.06, 0), (0.45, 0.06, 0.28), (0.15, 0.17, 0.19)),
        ((0, 0.28, -0.12), (0.08, 0.2, 0.08), (0.22, 0.25, 0.27)),
        ((0, 0.65, -0.12), (0.48, 0.3, 0.07), (0.12, 0.17, 0.18)),
        ((0, 0.65, -0.04), (0.41, 0.23, 0.012), (0.15, 0.65, 0.48)),
        ((0, 0.13, 0.3), (0.43, 0.04, 0.15), (0.20, 0.23, 0.25)),
    ], 'Mesa ao fundo, lado direito. Tela voltada para a sala: 0 graus.', orientacao=0)

    equipamento('cadeira', 'Cadeira', (-3.7, -2.4, 3.7), (3.8, -2.4, -3.0), [
        ((0, 0.85, 0), (0.42, 0.10, 0.42), (0.21, 0.27, 0.25)),
        ((0, 1.3, 0.36), (0.42, 0.45, 0.08), (0.25, 0.30, 0.28)),
        *(( (x, 0.4, z), (0.06, 0.4, 0.06), (0.34, 0.37, 0.38))
          for x in (-0.33, 0.33) for z in (-0.33, 0.33)),
    ], 'Em frente a mesa do computador, voltada para a tela: 0 graus.', orientacao=0)

    equipamento('bequer', 'Bequer', (2.8, -2.4, 3.0), (1.35, -0.5, -0.25), [
        ((0, 0.04, 0), (0.24, 0.04, 0.24), (0.3, 0.65, 0.7)),
        *(( (x, 0.28, 0), (0.025, 0.24, 0.24), (0.4, 0.7, 0.73)) for x in (-0.22, 0.22)),
        *(( (0, 0.28, z), (0.2, 0.24, 0.025), (0.4, 0.7, 0.73)) for z in (-0.22, 0.22)),
        ((0, 0.15, 0), (0.19, 0.08, 0.19), (0.18, 0.35, 0.65)),
    ], 'Bancada central, canto frontal direito. Recipiente do experimento.')

    for objeto in objetos_moveis:
        if not objeto.eh_mesa:
            objeto.posicionar_base((objeto.base.x, -2.4, objeto.base.z))

    # Fechamento visivel na exploracao; omitido no modo de organizacao orbital.
    for posicao, escala in [((0, 0, MEIA_SALA - 0.1), (MEIA_SALA, 2.5, 0.1)),
                             ((0, 2.5, 0), (MEIA_SALA, 0.1, MEIA_SALA))]:
        cubo = Cubo(posicao, escala, cor_parede, parede=posicao[1] == 0)
        cubo.ocultar_orbital = True
        cubos.append(cubo)

    return cubos, objetos_moveis
