#version 330 core

layout (location = 0) in vec3 posicao;

uniform mat4 modelo;
uniform mat4 visualizacao;
uniform mat4 projecao;

void main()
{
    gl_Position = projecao * visualizacao * modelo * vec4(posicao, 1.0);
}