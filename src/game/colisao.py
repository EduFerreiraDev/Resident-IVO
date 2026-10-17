import glm


def _resolver_eixo(posicao, eixo, eixo_fixo, deslocamento, objetos, raio):
    atual = getattr(posicao, eixo)
    candidato = atual + deslocamento

    for objeto in objetos:
        if not objeto.colisivel:
            continue

        if abs(getattr(posicao, eixo_fixo) - getattr(objeto.posicao, eixo_fixo)) >= (
            getattr(objeto.escala, eixo_fixo) + raio
        ):
            continue

        limite_minimo = getattr(objeto.posicao, eixo) - getattr(objeto.escala, eixo) - raio
        limite_maximo = getattr(objeto.posicao, eixo) + getattr(objeto.escala, eixo) + raio

        if deslocamento > 0 and atual <= limite_minimo < candidato:
            candidato = limite_minimo
        elif deslocamento < 0 and atual >= limite_maximo > candidato:
            candidato = limite_maximo

    return candidato


def resolver_movimento(posicao, deslocamento, objetos, raio=0.25):
    nova_posicao = glm.vec3(posicao)

    nova_posicao.x = _resolver_eixo(
        nova_posicao, "x", "z", deslocamento.x, objetos, raio
    )
    nova_posicao.z = _resolver_eixo(
        nova_posicao, "z", "x", deslocamento.z, objetos, raio
    )

    nova_posicao.y += deslocamento.y
    return nova_posicao