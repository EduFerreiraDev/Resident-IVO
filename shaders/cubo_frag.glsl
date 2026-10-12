#version 330 core

uniform vec3 corObjeto;

out vec4 corFinal;

void main()
{
    corFinal = vec4(corObjeto, 1.0);
}