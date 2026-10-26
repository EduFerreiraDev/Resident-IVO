#version 330 core

uniform vec3 corObjeto;
uniform vec3 posicaoCamera;
uniform vec3 direcaoCamera;
uniform bool primeiraPessoa;
uniform float tempo;

in vec3 posicaoMundo;

out vec4 corFinal;

void main()
{
    vec3 normal = normalize(cross(dFdx(posicaoMundo), dFdy(posicaoMundo)));
    vec3 luzFria = normalize(vec3(-0.45, 0.85, 0.35));
    float difusa = abs(dot(normal, luzFria));
    float iluminacao = 0.18 + 0.38 * difusa;

    // Luz de emergência piscando junto à porta lateral.
    vec3 alerta = vec3(6.75, 1.75, -2.5);
    float distanciaAlerta = length(posicaoMundo - alerta);
    float pulso = 0.75 + 0.25 * sin(tempo * 3.0);
    float vermelho = pulso * 2.0 / (1.0 + distanciaAlerta * distanciaAlerta * 0.18);

    vec3 luz = vec3(0.72, 0.85, 1.0) * iluminacao;
    luz += vec3(1.0, 0.10, 0.07) * vermelho;

    if (primeiraPessoa) {
        vec3 paraPonto = posicaoMundo - posicaoCamera;
        float distancia = length(paraPonto);
        float cone = smoothstep(0.75, 0.92, dot(normalize(paraPonto), normalize(direcaoCamera)));
        float lanterna = cone * 2.2 / (1.0 + distancia * distancia * 0.045);
        luz += vec3(0.85, 0.90, 1.0) * lanterna;
    }

    vec3 cor = corObjeto * luz;
    float neblina = 1.0 - exp(-0.007 * pow(length(posicaoMundo - posicaoCamera), 2.0));
    cor = mix(cor, vec3(0.035, 0.045, 0.06), clamp(neblina, 0.0, 0.65));
    corFinal = vec4(cor, 1.0);
}
