from src.entities.cubo import Cubo

def construir_laboratorio():
    cubos = []

    # Chão e Paredes
    cubos.append(Cubo((0, -2.5, 0), (5, 0.1, 5), (0.35, 0.38, 0.40)))
    cubos.append(Cubo((0, 0, -4.9), (5, 2.5, 0.1), (0.72, 0.76, 0.80)))
    cubos.append(Cubo((-4.9, 0, 0), (0.1, 2.5, 5), (0.55, 0.62, 0.68)))
    cubos.append(Cubo((4.9, 0, 0), (0.1, 2.5, 5), (0.55, 0.62, 0.68)))

    # Bancada
    cubos.append(Cubo((0, -0.65, -1.0), (2.0, 0.15, 1.0), (0.45, 0.27, 0.15)))
    for x in (-1.75, 1.75):
        for z in (-1.8, -0.2):
            cubos.append(Cubo((x, -1.55, z), (0.12, 0.8, 0.12), (0.25, 0.27, 0.29)))

    # Microscópio
    cubos.append(Cubo((-0.7, -0.42, -1.0), (0.4, 0.08, 0.3), (0.12, 0.18, 0.22)))
    cubos.append(Cubo((-0.7, -0.05, -1.0), (0.08, 0.32, 0.08), (0.15, 0.20, 0.24)))
    cubos.append(Cubo((-0.7, 0.22, -1.0), (0.25, 0.08, 0.12), (0.18, 0.25, 0.30)))
    cubos.append(Cubo((-0.88, 0.35, -1.0), (0.08, 0.12, 0.08), (0.08, 0.09, 0.10)))

    # Frascos
    for x, cor in [(0.3, (0.20, 0.65, 0.85)), (0.9, (0.25, 0.75, 0.45)), (1.5, (0.85, 0.55, 0.20))]:
        cubos.append(Cubo((x, -0.35, -1.2), (0.18, 0.25, 0.18), cor))
        cubos.append(Cubo((x, -0.05, -1.2), (0.08, 0.06, 0.08), (0.20, 0.22, 0.24)))

    # Tubos de ensaio e suporte
    cubos.append(Cubo((0.5, -0.40, -0.2), (0.55, 0.08, 0.25), (0.25, 0.18, 0.12)))
    for x in (0.15, 0.5, 0.85):
        cubos.append(Cubo((x, -0.20, -0.2), (0.09, 0.15, 0.09), (0.35, 0.75, 0.85)))

    return cubos