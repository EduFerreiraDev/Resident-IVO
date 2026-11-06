#version 330 core

uniform vec3 corObjeto;
uniform vec3 posicaoCamera;
uniform vec3 direcaoCamera;
uniform bool primeiraPessoa;
uniform float tempo;
uniform bool lampadaLigada;
uniform vec3 posicaoLampada;
uniform bool luzBancada;
uniform float forcaExperimento;
uniform float emissao;
uniform float brilhoMaterial;
uniform bool paredeDesgastada;
uniform vec3 posicaoAlerta;

in vec3 posicaoMundo;

out vec4 corFinal;

float hashParede(vec2 p)
{
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float ruidoParede(vec2 p)
{
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hashParede(i), hashParede(i + vec2(1, 0)), f.x),
               mix(hashParede(i + vec2(0, 1)), hashParede(i + vec2(1, 1)), f.x), f.y);
}

float manchasParede(vec2 p)
{
    return 0.57 * ruidoParede(p) + 0.28 * ruidoParede(p * 2.13 + 7.7)
         + 0.15 * ruidoParede(p * 4.27 + 19.3);
}

vec3 materialParede(vec3 ponto, vec3 normal)
{
    // Coordenadas do mundo mantem o tamanho do revestimento entre paineis.
    vec2 uv = abs(normal.x) > abs(normal.z) ? ponto.zy : ponto.xy;
    uv.y += 2.4;
    float irregular = manchasParede(uv * 1.6);
    float poros = ruidoParede(uv * 65.0);
    float descascado = smoothstep(0.60, 0.73, irregular);
    vec3 tinta = vec3(0.74, 0.76, 0.69) * (0.88 + 0.15 * poros);
    tinta = mix(tinta, vec3(0.40, 0.36, 0.28), descascado * 0.85);

    // Azulejos de laboratorio na metade inferior, com rejunte escurecido.
    float faixaAzulejo = 1.0 - smoothstep(2.05, 2.08, uv.y);
    vec2 grade = uv / vec2(0.65, 0.45);
    vec2 celula = fract(grade);
    vec2 borda = min(celula, 1.0 - celula);
    vec2 aa = max(fwidth(grade), vec2(0.002));
    float interior = smoothstep(0.012, 0.012 + aa.x, borda.x)
                   * smoothstep(0.018, 0.018 + aa.y, borda.y);
    float variacao = hashParede(floor(grade));
    vec3 azulejo = vec3(0.39, 0.54, 0.48) * (0.86 + 0.22 * variacao);
    azulejo *= 0.86 + 0.20 * poros;
    azulejo = mix(vec3(0.15, 0.19, 0.16), azulejo, interior);
    tinta = mix(tinta, azulejo, faixaAzulejo);

    // Umidade na base e escorridos verticais, sem animar a textura.
    float umidade = (1.0 - smoothstep(0.08, 1.45, uv.y))
                  * smoothstep(0.30, 0.72, manchasParede(vec2(uv.x * 1.4, uv.y * 0.6)));
    float escorrido = smoothstep(0.54, 0.78,
        manchasParede(vec2(uv.x * 8.0, uv.y * 0.28))) * 0.42;
    tinta = mix(tinta, vec3(0.18, 0.22, 0.15), clamp(umidade * 0.8 + escorrido, 0.0, 0.8));
    float ferrugem = smoothstep(0.66, 0.80, manchasParede(uv * vec2(3.0, 0.7) + 42.0));
    tinta = mix(tinta, vec3(0.38, 0.24, 0.13), ferrugem * 0.55);
    return tinta;
}

void main()
{
    vec3 normal = normalize(cross(dFdx(posicaoMundo), dFdy(posicaoMundo)));
    vec3 luzFria = normalize(vec3(-0.45, 0.85, 0.35));
    float difusa = abs(dot(normal, luzFria));
    float iluminacao = 0.18 + 0.38 * difusa;

    // Luz de emergência piscando junto à porta lateral.
    vec3 alerta = posicaoAlerta;
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

    // Luz de tarefa dirigida sobre a bancada central.
    if (luzBancada) {
        vec3 origem = vec3(0.0, 2.15, -1.0);
        vec3 raio = posicaoMundo - origem;
        float cone = smoothstep(0.55, 0.85, dot(normalize(raio), vec3(0,-1,0)));
        luz += vec3(0.65, 0.95, 0.87) * cone * 3.0 / (1.0 + dot(raio,raio)*0.14);
    }
    // Reacao visual, sem simulacao quimica: luz pulsante no recipiente.
    vec3 reacao = posicaoMundo - vec3(1.35, -0.2, -0.25);
    luz += vec3(0.2, 1.0, 0.45) * forcaExperimento
           * (1.1 + 0.25 * sin(tempo * 6.0)) / (1.0 + dot(reacao,reacao));
    vec3 visao = normalize(posicaoCamera - posicaoMundo);
    float especular = pow(abs(dot(normal, normalize(luzFria + visao))), 32.0);
    vec3 albedo = paredeDesgastada ? materialParede(posicaoMundo, normal) : corObjeto;
    float brilho = paredeDesgastada ? 0.04 : brilhoMaterial;
    vec3 cor = albedo * (luz + emissao) + vec3(0.65, 0.8, 0.85) * brilho * especular;
    float neblina = 1.0 - exp(-0.007 * pow(length(posicaoMundo - posicaoCamera), 2.0));
    cor = mix(cor, vec3(0.035, 0.045, 0.06), clamp(neblina, 0.0, 0.65));
    corFinal = vec4(cor, 1.0);
}
