
# Correção Postural com Visão Computacional

*Projeto criado para disciplina de Inteligência Artificial do curso de Análise de Sistemas - SENAC-RS, ministrada pelo Prof. Pablo De Chiaro*

Quando foi mencionado que o projeto final da disciplina deveria solucionar uma *dor*, talvez eu tenha interpretado isso de maneira um pouco literal demais: sempre trabalhei em escritório e **sempre** sofri com dores no pescoço. Desde que o *home office* se tornou uma realidade, a situação piorou (e muito), mesmo investindo em equipamentos ergonômicos e utilizando soluções vexatórias, como o uso contínuo de colar cervical. 

Com isso em mente, desenvolvi o presente projeto utilizando técnicas de visão computacional para monitorar a postura de um usuário em tempo real, gerando alertas para correção. Basicamente, o sistema processa os quadros de vídeo capturados por uma câmera, detecta os pontos-chave do corpo e calcula os ângulos das articulações para avaliar se a postura está correta ou incorreta.

## Requisitos

Antes de rodar o projeto, instale as dependências necessárias:

```bash

pip  install  -r  requirements.txt

```

### Conteúdo do arquivo `requirements.txt`:

  

```text

numpy==1.26.4

opencv-python==4.10.0.84

mediapipe==0.10.18

playsound==1.2.2

```

⚠️ **IMPORTANTE:**

-  **mediapipe**: Requer a instalação do  [ **Microsoft Visual C++ Redistributable for Visual Studio 2015-2022**](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-160).

-  **playsound**: Pode ser necessária a instalação do **wheel** para funcionar corretamente. Caso haja algum erro durante a instalação, execute o comando abaixo e tente novamente:

```bash

pip install wheel

```

## Funções


-   **`calcular_angulo(ponto1, ponto2, ponto3)`**: recebe três pontos no plano 2D e calcula o ângulo utilizado para verificar a inclinação dos ombros e do pescoço.
-   **`desenhar_angulo(frame, ponto1, ponto2, ponto3, angulo, cor)`**: Desenha o ângulo na tela.
-   **`feedback_postura(angulo_ombro, limite_ombro_min, limite_ombro_max, angulo_pescoco, limite_pescoco_min, limite_pescoco_max)`**: Fornece o feedback sobre a postura, exibindo seu status e dados, disparando o alerta sonoro, se necessário.

  ### Como Funciona

**1.  Processamento de Posições e Cálculo de Ângulos**: 
-   O código usa `resultados.pose_landmarks` para acessar os pontos-chave do corpo detectados pelo MediaPipe.
    
-   Extração dos pontos de interesse:
    
    -   **Ombro esquerdo** e **ombro direito**: Usados para calcular a posição do tronco.
    -   **Orelha esquerda** e **orelha direita**: Usados para calcular a posição do pescoço.
-   Cálculo dos ângulos:
    
    -   **`angulo_ombro`**: O ângulo entre os ombros é calculado entre os pontos do ombro esquerdo, ombro direito e um ponto fixo no eixo X (representado por `(ombro_direito[0], 0)`).
    -   **`angulo_pescoco`**: O ângulo entre a orelha esquerda, o ombro esquerdo e um ponto fixo no eixo X (representado por `(ombro_esquerdo[0], 0)`).

**2.  Processo de Calibração**: Durante os primeiros 30 quadros, o código coleta os ângulos dos ombros e pescoço em cada quadro e os armazena nas listas **`calibracao_angulo_ombro`** e **`calibracao_angulo_pescoco`**.

**3.  Detecção de Postura**: Após a calibração, os ângulos de ombro e pescoço são monitorados em tempo real. Se os ângulos saírem dos limites definidos durante a calibração, o sistema considera que a postura está ruim. A variável `margem` pode ser ajustada conforme necessário pelo usuário, representando a tolerância em graus.

**4.  Alerta Sonoro**: Se o usuário permanecer com a postura ruim por um tempo mínimo (definido pela variável `tempo_minimo_postura_ruim`), o sistema dispara um alerta sonoro. O intervalo entre os alertas também pode ser configurado por meio da variável `tempo_minimo_postura_ruim`, também medida em segundos.

## Execução

  

**1.  Verifique se a câmera está conectada**.

**2.  Execute o script `main.py`:**

```bash

python  main.py

```

**3.  Interaja com a aplicação:**

- O programa exibirá a captura de vídeo em tempo real. O usuário deve manter uma postura adequada durante a calibração inicial para garantir melhores resultados.

- Caso a postura esteja incorreta, o programa exibirá um alerta em vermelho na tela e emitirá um som após o usuário permanecer com a postura inadequada por 3 segundos. O sistema possui um intervalo de 10 segundos entre os alertas (configuração padrão).

- Para encerrar o programa, pressione `q` na janela de vídeo.


## Melhorias Futuras

 - Monitoramento simultâneo com uma segunda câmera, para observar a postura do usuário a partir de um ângulo lateral.
 - Extração de dados para Excel e gráficos incrementais usando o Matplotlib, contabilizando as ocorrências por data e gerando gráficos para monitorar a eficácia da aplicação na redução de ocorrências de má-postura.