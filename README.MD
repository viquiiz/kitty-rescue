# 🐾 Kitty Rescue  

Um jogo 2D desenvolvido em **Python com Pygame**, onde o objetivo é resgatar gatinhos em diferentes pontos do cenário antes que o tempo acabe! Atividade prática desenvolvida na matéria de Linguagem de Programação Aplicada na faculdade de Análise e Desenvolvimento de Sistemas.

---

## Gameplay  
- Controle o personagem principal para explorar o mapa.  
- Pule plataformas e alcance os gatinhos.  
- Ao encostar neles, eles pulam de alegria e são adicionados à contagem de resgatados.  
- O jogo termina quando o tempo acaba, quando o jogador morre ou quando todos os gatos são salvos.  

---

## Funcionalidades  
- Sistema de colisão com blocos e plataformas  
- Animações de personagem e gatinhos (idle, run, jump, fall)  
- Timer e HUD mostrando tempo restante e número de gatos salvos  
- Sons e trilha sonora em estilo retrô 
- Diferentes telas de fim de jogo (vitória, derrota, tentativa parcial)  
- Mecânica de scroll horizontal e vertical para acompanhar o jogador  

---

## Aprendizados  
Durante o desenvolvimento deste projeto, trabalhei com:  
- Estruturação de classes em jogos 2D e orientação a objetos (Player, Cat, Game, Block, Background).  
- Implementação de colisões com máscaras no Pygame.  
- Gerenciamento de loops de jogo, timers e eventos de teclado.  
- Criação de telas finais (game over / vitória).  

---

## Próximos passos  
- Criar fases adicionais com diferentes dificuldades  
- Incluir inimigos no mapa
- Power-ups e itens colecionáveis  
- Sistema de ranking com pontuação final  

---

## Como rodar o jogo  
1. Clone o repositório  
   ```bash
   git clone https://github.com/seuusuario/kitty-rescue.git
   cd kitty-rescue
    ```

2. Instale as dependências

   ```bash
    pip install -r requirements.txt
    ```

3. Execute o jogo
    ```bash
    python main.py
    ```

---

## Créditos dos Assets

- [Background and Characters by craftpix.net](https://craftpix.net/product/forest-pixel-art-environment-asset-set)
- [Sounds by opengameart.org](https://opengameart.org)