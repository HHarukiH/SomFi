# 📡 Sistema de Comunicação Acústica

**Disciplina:** Redes de Computadores  
**Instituição:** Universidade Tecnológica Federal do Paraná (UTFPR) - Campo Mourão  
**Equipe:** Vinicius, [Nome do Colega]

Este projeto implementa um software capaz de atuar como Emissor e Receptor de dados digitais utilizando o meio acústico (ondas sonoras). O sistema foi desenvolvido em Python e opera a transmissão e a recepção de quadros de bits em tempo real.

---

## 1. Fundamentação Teórica

### O Modelo ISO/OSI e a Camada Física
O Modelo OSI é uma arquitetura dividida em 7 camadas (Física, Enlace, Rede, Transporte, Sessão, Apresentação e Aplicação) que padroniza a comunicação entre sistemas. 

A nossa implementação atua primordialmente na **Camada Física**, responsável pela transmissão de bits brutos sobre o meio de comunicação. Para isso, lidamos diretamente com:
*   **Sinais Analógicos e Dados Digitais:** A transmissão ocorre através de ondas sonoras no ar (sinal analógico contínuo). O software realiza a modulação para inserir dados digitais (zeros e uns) nessa onda, e o processo inverso de digitalização na recepção, utilizando uma taxa de amostragem de 44.100 Hz.
*   **Largura de Banda e Modulação:** A capacidade do canal acústico é gerida alterando as propriedades do som. No Método 1, a modulação baseia-se na variação de tempo (cadência). No Método 2, utilizamos a Modulação por Deslocamento de Frequência (FSK), alocando diferentes frequências para representar agrupamentos de bits.
*   **Ruído:** O tratamento da interferência física do ambiente, como reverberação e sons de fundo, que causam distorção na leitura da amplitude ou da frequência.

### Transição para a Camada de Enlace e Detecção de Erros
Para poder estruturar melhor o projeto, tivemos que implementar características que já pertencem à **Camada de Enlace**. Apenas transmitir sinais no ar não é suficiente; o sistema precisa agrupar os bits em quadros organizados para delimitar início e fim, e garantir a integridade da mensagem contra ruídos.

Implementamos duas técnicas de detecção de erros:
1.  **Paridade Par (Método 1):** Utiliza um quadro de 9 bits. O transmissor conta os bits `1` presentes nos 8 bits de dados e adiciona um 9º bit (0 ou 1) para garantir que a soma total de bits `1` no quadro seja um número par. O receptor realiza a mesma contagem para validar a integridade.
2.  **Soma Simples / Checksum (Método 2):** Os bits da carga de dados são somados, e o valor numérico dessa soma é convertido num byte final (8 bits) anexado ao final do quadro. O receptor recalcula a soma dos dados e compara com este byte final.

---

## 2. Engenharia e Arquitetura das Soluções

### Método 1: Transceptor de Impactos (Padronizado)
Este método utiliza impactos sonoros com cadência padronizada: o Bit 0 é representado por 1 batida e o Bit 1 por 2 batidas consecutivas.

*   **Transmissor:** Para evitar a geração de eco, o transmissor sintetiza um impacto matemático utilizando uma onda senoidal aguda (1500 Hz) multiplicada por um envelope de decaimento exponencial rápido (50 milissegundos). Isso produz um sinal acústico seco e de alta precisão.
*   **Receptor:** O sistema capta o áudio e avalia o percentil 95 da amplitude em blocos de 1024 amostras, comparando com um limiar de volume pré-calibrado (0.08). 
*   **Sincronização e Janelas de Tempo:** Para evitar leituras duplicadas causadas por reverberação, aplicamos um tempo de ignorância condicional (*debounce*) de 0.20 segundos após qualquer impacto. Uma janela de 0.55s é mantida aberta para aguardar a segunda batida (que define o Bit 1). O registro do bit é efetivado após 0.80s de silêncio contínuo.

### Método 2: Modulação 16-FSK Dinâmica (Livre Escolha)
Para alcançar uma maior taxa de transmissão, projetamos um motor síncrono utilizando modulação 16-FSK. Agrupamos os bits em blocos de 4 (simbolizando 16 estados possíveis) e mapeamos cada bloco para uma frequência específica (de 800 Hz a 3800 Hz, em intervalos de 200 Hz). O receptor utiliza a Transformada Rápida de Fourier (FFT) para identificar o pico de frequência dominante a cada janela de escuta.

*   **Estrutura do Quadro (Protocolo de 264 bits):**
    Para enviar caracteres ASCII sequenciais, estruturamos o envio de dados num quadro com tamanho dinâmico, contendo os seguintes limites máximos:
    1.  **Cabeçalho (8 bits iniciais):** Determina numericamente a quantidade de bits que compõem a mensagem. O receptor lê este valor para saber exatamente quando deve parar de escutar dados.
    2.  **Dados (Até 248 bits):** O conteúdo útil transmitido, suportando um máximo de 31 caracteres ASCII por envio (31 x 8 = 248).
    3.  **Soma de Verificação (8 bits finais):** O checksum da mensagem.
    
    A capacidade total máxima por envio é de 264 bits (8 de tamanho + 248 de dados + 8 de soma).
*   **Taxa de Transmissão Prática:** O transmissor emite 1 símbolo (4 bits) a cada 0.20 segundos. A taxa de transmissão atinge a marca teórica e prática de **20 bps (bits por segundo)**.

---

## 3. Divisão de Tarefas

O desenvolvimento do software, bem como a produção dos materiais exigidos para a entrega (vídeo e relatório), foram divididos estrategicamente entre os dois membros da equipe ao longo de três fases estruturais:

**Fase 1: Idealização, Arquitetura Base e Interface Gráfica**
*   **Responsável:** Vinicius
*   **Atribuições:** Iniciou a estruturação do projeto criando a espinha dorsal da arquitetura do software. Foi o responsável por idealizar e desenvolver a interface gráfica central (GUI) utilizando a biblioteca `pygame`, projetando o painel de inspeção forense de bits e a renderização em tempo real das grelhas de dados. Concebeu a arquitetura do "Método 2" (16-FSK Dinâmico), definindo a estrutura do protocolo da Camada de Enlace que fatiaria a mensagem em Cabeçalho (Tamanho), Carga Útil (Dados ASCII) e Rodapé (Checksum). Criou também o mapeamento do menu e a lógica de transição fluida entre os módulos de Transmissão e Recepção.

**Fase 2: Desenvolvimento dos Motores de Áudio e Algoritmos de Erro**
*   **Responsável:** [Nome do Colega]
*   **Atribuições:** Assumiu o desenvolvimento braçal e a pesquisa matemática para os primeiros protótipos dos motores acústicos (`prog` a `prog5`). Realizou a implementação base das bibliotecas `sounddevice` e `numpy` para leitura e geração de áudio. Escreveu os algoritmos primários para a extração de espectros de frequência utilizando a Transformada Rápida de Fourier (FFT), definindo o mapeamento dos 16 símbolos do FSK. Além disso, implementou os códigos vitais de verificação de integridade exigidos, programando o cálculo lógico da Paridade Par (para o Método 1) e o algoritmo de Checksum (para o Método 2).

**Fase 3: Calibração da Física do Som, Vídeo e Documentação Científica**
*   **Responsáveis:** Vinicius e [Nome do Colega]
*   **Atribuições:** Vinicius assumiu a etapa final de polimento físico e entregas burocráticas. Foi o responsável por alinhar os protótipos de áudio com a física do mundo real, programando o filtro de ruído por percentil 95, o bloqueio de arranque (*grace period*) e o *debounce* acústico de 0.20s para ignorar eco. Sintetizou matematicamente o som do transmissor do Método 1 (onda de 1500Hz com decaimento exponencial) para garantir a interoperabilidade exigida pelo vídeo de referência do professor. Foi também o autor integral da elaboração deste Relatório Técnico/README (Tarefa B). Na etapa de audiovisual (Tarefa C), Vinicius foi o responsável por gravar todo o material do Vídeo de Demonstração, enquanto [Nome do Colega] assumiu a edição final do vídeo, garantindo que as simulações de sucesso e falha ficassem claras antes de o incorporar ao repositório.

---

## 4. Desafios, Problemas e Soluções

A implementação da comunicação via som ambiente gerou desafios de instabilidade física e processamento de sinal:
1.  **Falsos Positivos de Arranque:** O ruído físico do utilizador a clicar no rato para ativar o receptor causava um pico de amplitude lido erroneamente como um bit. *Solução:* Implementação de um bloqueio de arranque (grace period), configurando a máquina de estados para descartar todo e qualquer input de áudio no primeiro 1 segundo de ativação.
2.  **Reverberação no Método 1:** O eco das batidas nas paredes do ambiente ultrapassava o limiar mínimo de amplitude, gerando bits duplicados. *Solução:* Aumento do *debounce* interno para 0.20s e alteração do filtro de volume para o percentil 95 (`np.percentile`), isolando transientes reais do ruído de fundo.
3.  **Sincronização no Método 2 (Perda de Quadros):** A gravação do áudio FSK necessita de um momento exato de partida para a leitura da FFT. Inícios assíncronos corrompiam a decodificação dos bytes. *Solução:* Introdução de um tom de pré-sincronismo (Preâmbulo) de 4000 Hz. O receptor permanece pausado e só inicia os cronômetros de leitura fracionada após a detecção estrita desse tom específico.

---

## 5. Declaração do Uso de Inteligência Artificial

A ferramenta de Inteligência Artificial Google Gemini foi utilizada ativamente ao longo de todo o ciclo de vida do software, atuando como parceira de depuração (*debugging*) e mentora em processamento de sinais. O uso ocorreu de forma linear e progressiva nas seguintes fases:

*   **Fase 1: Prototipagem e Bibliotecas de Áudio:** No início do projeto, a IA foi utilizada para compreender o funcionamento assíncrono da biblioteca `sounddevice`. Como a leitura do microfone precisava ocorrer em tempo real sem congelar a interface gráfica, a IA auxiliou na estruturação correta das funções de *callback* e na leitura de blocos de áudio (`indata`) utilizando o `numpy`.
*   **Fase 2: Refatoração e Implementação da FFT:** Quando os scripts iniciais de modulação foram finalizados pela equipe, utilizamos a IA para refatorar e unificar os códigos num padrão limpo. Neste ponto, a IA explicou a aplicação prática da Transformada Rápida de Fourier (`np.fft.rfft`), gerando os trechos matemáticos exatos para converter os blocos de áudio do domínio do tempo para o domínio da frequência, permitindo a identificação dos picos em Hz.
*   **Fase 3: Arquitetura do Protocolo 16-FSK (Camada de Enlace):** Para o Método 2, a IA foi consultada para desenhar a lógica de fatiamento de dados. Ela auxiliou a programar as rotinas que quebram uma *string* ASCII em bits, agrupam esses bits de 4 em 4 (símbolos) e concatenam os bytes de cabeçalho (tamanho) e rodapé (checksum) no array de áudio final, formatando corretamente as transições de frequência.
*   **Fase 4: Integração de UI e Exportação de Arquivos:** A IA gerou as lógicas matemáticas para o alinhamento visual dos elementos na interface Pygame (como o desenho das chaves de agrupamento de bits na tela). Adicionalmente, forneceu o *snippet* de integração entre `numpy`, `scipy.io.wavfile` e a janela nativa do `tkinter` para permitir a exportação dos arrays flutuantes de som para arquivos `.wav` de 16-bits.
*   **Fase 5: Calibração da Física do Ambiente e Sintetização:** Na etapa final, a IA foi vital para adaptar o código à física do mundo real. Para o Método 1, a IA formulou a equação matemática que sintetiza um "estalo" perfeito (onda senoidal multiplicada por decaimento exponencial). Em seguida, auxiliou na criação do *Grace Period* (bloqueio de escuta de 1 segundo ao clicar no Play) e na substituição de limiares absolutos por limites baseados no percentil 95 (`np.percentile`), permitindo que o microfone ignorasse os ecos acústicos da sala e o som físico do clique do rato.

---

## 6. Conclusão

O desenvolvimento prático da Camada Física acústica demonstrou os limites e a volatilidade de um meio de transmissão não guiado. Diferente da comunicação digital isolada em cabos, o canal sonoro sofre interferência constante, exigindo compensações críticas de software. A principal observação técnica é que aumentar a sensibilidade de escuta amplifica o ruído de fundo na mesma proporção que o sinal útil. O projeto validou a necessidade de mecanismos de controle (como margens de distanciamento de frequências no FSK e algoritmos de detecção de erros) para estabilizar a leitura de dados, comprovando empiricamente os desafios superados por protocolos industriais de comunicação em ambientes ruidosos.

---
## Licença
Este software está licenciado sob a licença Open-Source **MIT License**. Detalhes podem ser encontrados nos cabeçalhos dos arquivos de código-fonte e no arquivo LICENSE do repositório.