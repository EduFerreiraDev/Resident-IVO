# Resident IVO Implementation Plan

**Goal:** implementar a proposta da Sprint 1 fornecida pelo usuário.
**Architecture:** manter GLFW, OpenGL e os objetos compostos existentes. Separar validação da renderização, adicionando um HUD OpenGL e regiões de destino.
**Tech Stack:** Python, PyOpenGL, GLFW, PyGLM, NumPy; sem novas dependências de execução.
**Spec:** https://docs.google.com/document/d/1WW77BUaxdCZ32K-JfcCN2_Efel3dRnIDzxjKMHuxhcI

## Restrições
- Modelagem simplificada; terror como ambientação; organização como objetivo principal.
- Preservar alterações locais e não enviar commits para o remoto.
- Incluir escala e experimento complementar, conforme pedido de adicionar tudo.

## Tarefas
1. [x] Testar validação por região, orientação, altura e dependência dos tubos; testar bloqueio, execução e cancelamento do experimento.
2. [x] Implementar transformações dos objetos compostos e AABBs após rotação, mantendo sua base.
3. [x] Completar os 11 equipamentos e destinos, bancadas, prateleira e decoração.
4. [x] Integrar seleção persistente, arraste, rotação, escala, encaixe e marcadores; impedir alterações durante o experimento.
5. [x] Adicionar HUD com nomes, instruções, progresso, mensagens e estados do experimento; iluminação de bancada e emissão.
6. [x] Testar lógica, contexto OpenGL, shaders, renderização e fluxo completo. Documentar controles e instalação no README.

## Review Focus
- Rejeitar altura errada, objetos fora do destino e orientação inadequada.
- Não validar tubos sem suporte organizado.
- Não permitir experimento antecipado ou duplicado.
- Preservar limites da sala e evitar sobreposição após transformação.
- Mudança de câmera e janela minimizada não devem deixar arraste ativo nem dividir por zero.

## Decisões de execução
- Implementar em uma cópia de preparação e aplicar os arquivos ao Resident-IVO após verificação, pois ele está fora das pastas autorizadas deste chat.
- Usar atlas de fonte pré-gerado; Pillow somente na preparação, sem dependência adicional para o usuário.

## Verificacao
- 11 testes de unidade passaram, incluindo arraste dos 11 equipamentos.
- Smoke test em contexto OpenGL real passou: shaders, HUD, cena, experimento, cameras e soltura do mouse.
- Imagem renderizada inspecionada visualmente.
- Revisao independente: corrigido estado de orbita preso ao iniciar experimento.
- Corrigidos plano de arraste e classificacao explicita das superficies de apoio.
