#version 330 core

layout (location = 0) in vec3 posicao;

void main()
{
    gl_Position = vec4(posicao, 1.0);
}