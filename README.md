# Resident IVO — Laboratório 3D

Aplicação interativa em Python e OpenGL para organizar um laboratório científico com ambientação de terror inspirada em Resident Evil. O projeto trabalha modelagem simplificada, transformações geométricas, câmera, iluminação, materiais e validação de posicionamento.

## Objetivo

Organize os **11 equipamentos** nas regiões indicadas em laranja. Os destinos ficam verdes quando os objetos estão corretos. O painel mostra o progresso, e a faixa inferior informa o objeto selecionado, seu destino, sua orientação e as mensagens da atividade.

| Equipamento | Destino |
| --- | --- |
| Microscópio | Lado esquerdo da bancada central |
| Suporte para tubos | Área dos tubos na bancada central |
| 3 tubos de ensaio | Suporte; organize o suporte primeiro |
| 3 frascos de reagentes | Prateleira ao fundo, da esquerda para a direita |
| Computador | Mesa ao fundo, à direita |
| Cadeira | Em frente à mesa do computador |
| Béquer | Canto frontal direito da bancada central |

Microscópio, suporte, computador e cadeira devem estar orientados a **0 graus**. A validação considera posição horizontal, altura e orientação. O encaixe ajuda quando o cursor se aproxima do destino; colisões impedem sobreposição e transformações fora da sala. A cadeira precisa contornar a bancada. Caixas decorativas podem ser movidas e não contam para o progresso.

## Controles

| Controle | Ação |
| --- | --- |
| `3` | Modo de organização com câmera orbital |
| `1` | Exploração em primeira pessoa |
| Clique esquerdo em um equipamento | Selecionar; a seleção permanece após soltar |
| Clique e arraste no equipamento | Mover; a altura se ajusta aos apoios |
| Clique e arraste no espaço vazio | Orbitar a câmera |
| Roda do mouse | Aproximar ou afastar a câmera orbital |
| Setas | Deslocar a câmera orbital |
| `Q` / `R` | Girar o objeto selecionado em passos de −15° / +15° |
| `Z` / `X` | Diminuir / aumentar a escala do objeto selecionado |
| `G` | Mostrar / ocultar os destinos |
| `H` | Mostrar / ocultar a ajuda de controles |
| `L` | Ligar / desligar a luz do teto |
| `B` | Ligar / desligar a luz da bancada |
| `W`, `A`, `S`, `D` + mouse | Movimentação e visão em primeira pessoa |
| `E` perto do interruptor | Alternar a luz do teto em primeira pessoa |
| `Enter` | Iniciar o experimento após organizar todos os equipamentos |
| `Esc` | Encerrar |

A escala é limitada entre 0,75× e 1,25×. Transformações que causariam colisão são rejeitadas. A câmera de organização omite o teto e a parede frontal para facilitar a visão do interior; na exploração, o laboratório aparece fechado. A ajuda completa de controles aparece em janelas com pelo menos 1000 pixels de largura.

## Experimento virtual

Com os 11 equipamentos organizados, pressione `Enter`. Durante cinco segundos, o líquido do béquer muda de cor e emite uma luz verde pulsante. A interface informa o andamento e a conclusão. A manipulação fica bloqueada durante e após o experimento, mas é possível continuar observando a cena e alternando as câmeras. Reinicie a aplicação para uma nova atividade.

Essa é uma representação visual simples, sem simulação química ou física realista.

## Ambientação e iluminação

A sala tem 16 × 16 unidades, com mais espaco de circulacao. As paredes combinam pintura clara envelhecida, azulejos esverdeados, rejunte escuro, descascados, manchas de umidade e escorridos. O revestimento e gerado pelo shader em coordenadas do mundo, mantendo sua escala nas diferentes paredes sem arquivos de textura adicionais.

O cenário contém bancadas, prateleira, armários, computador, microscópio, recipientes, cadeira, luminária e decoração. A atmosfera combina tons frios, marcas no piso, luz vermelha de emergência, neblina, lâmpada do teto com falhas e lanterna na exploração. A bancada possui iluminação direcionada independente, e o béquer usa brilho especular para se diferenciar dos materiais foscos.

## Executar

É necessário Python 3.10 ou superior e suporte a **OpenGL 3.3** no computador.

Na pasta do projeto:

```bash
python -m pip install -r requirements.txt
python main.py
```

O atlas de texto em `assets/ui/fonte.bin` já está incluído. A aplicação não precisa de Pillow ou outra biblioteca de interface.

## Verificação

Testes das regras, das transformações, das colisões e do arraste por coordenadas de tela:

```bash
python -B -m unittest discover -s tests -v
```

Verificação adicional com um contexto OpenGL real e janela invisível:

```bash
python -B tests/smoke_opengl.py
```

Esse teste verifica a compilação dos shaders, a renderização do cenário e do painel, o fluxo do experimento e as trocas de câmera. Ele grava `preview.ppm` para inspeção visual e requer uma sessão gráfica com OpenGL disponível.

## Referência do trabalho

[Documento da Sprint 1 — Trabalho de Computação Gráfica](https://docs.google.com/document/d/1WW77BUaxdCZ32K-JfcCN2_Efel3dRnIDzxjKMHuxhcI/edit)

Resident Evil é a referência de atmosfera. O objetivo da atividade é preparar e organizar o laboratório.
