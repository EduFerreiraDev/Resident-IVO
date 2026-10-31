#version 330 core

uniform vec3 corObjeto;
uniform vec3 posicaoCamera;
uniform vec3 direcaoCamera;
uniform bool primeiraPessoa;
uniform float tempo;
uniform bool lampadaLigada;
uniform vec3 posicaoLampada;

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

    //Iluminação da lampada do teto
    if(lampadaLigada) {

        //oscilação da lampada
        float piscada = 0.85 + 0.15 * sin(tempo * 8.0) + 0.10 * sin(tempo * 17.0);
        
        //apagões ocasionais
        float falha = step(
            0.18,
            sin(tempo * 5.0) * sin(tempo * 11.0)
        );

        float intensidade = piscada * falha;

        //Distância entre a lâmpda e o objeto
        float distanciaLampada = length(posicaoMundo - posicaoLampada);

        //A luza perde intensidade com a distância
        float atenuacao = 1.0 / (1.0 + 0.18 * distanciaLampada + 0.12 * distanciaLampada * distanciaLampada);

        //cor amarelada da lâmpada
        vec3 corLampada = vec3(1.0, 0.72, 0.38);

        luz += corLampada * intensidade * atenuacao * 2.5;
        
    }

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
