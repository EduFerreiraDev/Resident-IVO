from src.entities.cubo import Cubo
from src.entities.objeto_movel import ObjetoMovel

MEIA_SALA = 7.0
LIMITE_INTERIOR = MEIA_SALA - 0.5

def construir_laboratorio():
    cubos = []
    objetos_moveis = []

    # Chão e paredes; a parede do fundo tem uma abertura para a janela.
    cubos.append(Cubo((0, -2.5, 0), (MEIA_SALA, 0.1, MEIA_SALA), (0.35, 0.38, 0.40)))
    fundo = -MEIA_SALA + 0.1
    cor_parede = (0.72, 0.76, 0.80)
    cubos.extend([
        Cubo((-4.5, 0, fundo), (2.5, 2.5, 0.1), cor_parede),
        Cubo((4.5, 0, fundo), (2.5, 2.5, 0.1), cor_parede),
        Cubo((0, -1.75, fundo), (2.0, 0.75, 0.1), cor_parede),
        Cubo((0, 2.0, fundo), (2.0, 0.5, 0.1), cor_parede),
        Cubo((-MEIA_SALA + 0.1, 0, 0), (0.1, 2.5, MEIA_SALA), (0.55, 0.62, 0.68)),
        Cubo((MEIA_SALA - 0.1, 0, 0), (0.1, 2.5, MEIA_SALA), (0.55, 0.62, 0.68)),
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
        Cubo((6.78, -0.55, -2.5), (0.035, 1.85, 1.05), (0.12, 0.17, 0.19)),
        Cubo((6.72, -0.55, -2.5), (0.04, 1.9, 0.08), (0.46, 0.28, 0.17)),
        Cubo((6.72, -0.55, -3.55), (0.04, 1.9, 0.08), (0.46, 0.28, 0.17)),
        Cubo((6.68, -0.4, -1.85), (0.07, 0.07, 0.08), (0.65, 0.65, 0.58)),
        Cubo((6.68, 1.75, -2.5), (0.09, 0.14, 0.22), (1.0, 0.08, 0.05)),
    ])

    # Armários de pesquisa, prateleiras e caixas abandonadas.
    for z in (0.7, 2.5, 4.3):
        cubos.extend([
            Cubo((-6.25, -0.65, z), (0.55, 1.75, 0.75), (0.22, 0.28, 0.29), colisivel=True),
            Cubo((-5.67, -0.65, z), (0.04, 1.6, 0.68), (0.31, 0.36, 0.35)),
            Cubo((-5.60, -0.65, z), (0.04, 0.05, 0.62), (0.42, 0.25, 0.17)),
        ])

    for x, z in ((4.8, 3.8), (5.3, 4.5), (-4.4, -3.8)):
        cubos.append(Cubo((x, -2.05, z), (0.48, 0.35, 0.48), (0.29, 0.24, 0.19), colisivel=True))

    # Marcas no piso e uma luminária fria suspensa.
    for x, z in ((-2.5, 3.4), (3.2, -3.7), (4.1, 1.8)):
        cubos.append(Cubo((x, -2.385, z), (0.7, 0.008, 0.3), (0.24, 0.13, 0.12)))
    cubos.extend([
        Cubo((0, 2.35, -2.0), (1.1, 0.08, 0.24), (0.18, 0.22, 0.24)),
        Cubo((0, 2.25, -2.0), (0.85, 0.025, 0.15), (0.45, 0.62, 0.62)),
    ])

    # Mesa: tampo e pernas são movidos como um único objeto
    tampo_mesa = Cubo(
        (0, -0.65, -1.0),
        (2.0, 0.15, 1.0),
        (0.45, 0.27, 0.15),
        colisivel=True,
    )
    partes_mesa = [tampo_mesa]

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
    objetos_moveis.append(ObjetoMovel(microscopio))

    # Frascos: corpo e tampa de cada um se movem juntos
    frascos = [
        (0.3, (0.20, 0.65, 0.85)),
        (0.9, (0.25, 0.75, 0.45)),
        (1.5, (0.85, 0.55, 0.20)),
    ]

    for x, cor in frascos:
        partes_frasco = [
            Cubo((x, -2.3, 2.0), (0.18, 0.25, 0.18), cor),
            Cubo((x, -2.0, 2.0), (0.08, 0.06, 0.08), (0.20, 0.22, 0.24)),
        ]
        cubos.extend(partes_frasco)
        objetos_moveis.append(ObjetoMovel(partes_frasco))

    # Suporte e tubos: movem-se como um único objeto
    suporte_tubos = [
        Cubo((2.6, -2.3, -0.2), (0.55, 0.08, 0.25), (0.25, 0.18, 0.12))
    ]

    for x in (2.25, 2.6, 2.95):
        suporte_tubos.append(
            Cubo((x, -2.1, -0.2), (0.09, 0.15, 0.09), (0.35, 0.75, 0.85))
        )

    cubos.extend(suporte_tubos)
    objetos_moveis.append(ObjetoMovel(suporte_tubos))

    return cubos, objetos_moveis
