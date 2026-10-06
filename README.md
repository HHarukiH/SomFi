# SomFi
Wifi pelo Som
# Fundamentos de Telecomunicações: Implementação Acústica da Camada Física

## 1. Introdução ao Modelo OSI e a Camada Física
No Modelo OSI (*Open Systems Interconnection*), a **Camada 1 (Física)** é responsável pela transmissão e recepção do fluxo bruto de bits (0s e 1s) não estruturados através de um meio físico. Ela não entende o significado dos dados, preocupando-se apenas com a mecânica, elétrica ou, neste projeto, com as propriedades acústicas necessárias para fazer um bit viajar do Ponto A ao Ponto B.

Neste projeto desenvolvido em Python (utilizando `sounddevice`, `numpy` e `pygame`), o meio físico não é um cabo de cobre ou fibra ótica, mas sim o ar. O hardware de rede é substituído pelo alto-falante (emissor) e pelo microfone (receptor), provando que os conceitos de telecomunicações são independentes do meio de propagação.

**O que neste projeto pertence estritamente à Camada Física?**
Tudo o que envolve transformar dados em energia e energia de volta em dados. Isso inclui:
* A escolha das frequências (Hertz).
* A conversão de bits em som (Modulação).
* A leitura da energia do ambiente (Limiar de Volume / FFT).
* A temporização (Baud Rate vs. Bit Rate).

> **Nota de Fronteira OSI:** No momento em que o nosso sistema agrupa os bits num "Quadro de 12 bits" e aplica lógicas matemáticas como Paridade ou Soma de Verificação (Checksum) para rejeitar áudios corrompidos, o projeto ultrapassou a Camada 1 e implementou funções da **Camada 2 (Camada de Enlace de Dados - Subcamada MAC)**. A Camada Física entrega o ruído; a Camada de Enlace decide se o ruído faz sentido.

---

## 2. Modulação e Codificação de Linha
Para transmitir os bits pelo ar, a informação digital precisa ser codificada numa onda analógica. O projeto implementa duas abordagens clássicas:

### 2.1. O Método de Batidas (Detecção de Amplitude)
*Equivalente rústico ao OOK (On-Off Keying) ou ASK (Amplitude-Shift Keying).*
A presença de energia (um pico de volume, ou "batida") acima de um limiar pré-definido representa um evento. O tempo decorrido entre os eventos determina se o bit é 0 ou 1. É um método suscetível a ruído ambiente, assim como a modulação AM é sensível a interferências eletromagnéticas.

### 2.2. O Método de Áudio Contínuo (M-FSK)
Para o segundo método, implementou-se a Modulação **M-FSK (Multiple Frequency-Shift Keying)**, especificamente a sua variante **4-FSK**.
Em vez de alternar a amplitude, alteramos a frequência da onda portadora. Como utilizamos 4 frequências distintas (1200, 1600, 2200 e 2800 Hz), cada variação na onda consegue transportar 2 bits por símbolo (Baud).

* `00` = 1200 Hz
* `01` = 1600 Hz
* `10` = 2200 Hz
* `11` = 2800 Hz

Isto ilustra a diferença crucial entre **Baud Rate** (taxa de variação do sinal físico) e **Bit Rate** (taxa de transmissão de dados). Com 4-FSK, o nosso Bit Rate é o dobro do nosso Baud Rate, garantindo maior eficiência e velocidade.

> **A Física dos Harmônicos:** As frequências não foram escolhidas de forma aleatória. Em acústica, um alto-falante emitindo 1200 Hz gera harmônicos naturais em múltiplos exatos (2400 Hz, 3600 Hz, etc.). Se atribuíssemos bits a frequências múltiplas (ex: 1000 Hz e 2000 Hz), o microfone captaria fantasmas, corrompendo a leitura. As frequências escolhidas são matematicamente espaçadas para evitar que os harmônicos de uma se sobreponham à banda principal da outra.

---

## 3. Sincronização de Relógio e Alinhamento de Quadro
O maior desafio da Camada Física não é enviar o sinal, mas garantir que o receptor saiba exatamente quando ler o sinal.

### 3.1. Assíncrono vs. Síncrono
Inicialmente, o projeto utilizou uma abordagem **Assíncrona**, inserindo micro-silêncios entre cada símbolo (técnica conhecida como *Return-to-Zero*). Isso evita a fusão de notas idênticas (ex: ler dois `00` consecutivos), mas desperdiça muito tempo de canal com o silêncio e sofre com a reverberação acústica da sala, que prolonga a nota física.

A evolução do projeto migrou para uma abordagem **Síncrona Contínua** (*Non-Return-to-Zero*). Os dados são enviados sem pausas, exigindo uma temporização perfeita (cronômetro) entre emissor e receptor.

### 3.2. O Problema do "Clock Drift" (Desvio de Relógio)
Se o emissor envia uma nota a cada 0.10 segundos, o receptor precisa ler a cada 0.10 segundos. No entanto, o hardware de áudio do computador tira "amostras" (blocos) em intervalos quebrados (ex: a cada 23 ms). Com o tempo, a leitura do receptor desalinha-se da emissão, lendo a transição entre duas notas (ruído) em vez do centro da onda. A isto chama-se **Clock Drift**.

### 3.3. O Preâmbulo (Sync Word) e a Analogia dos "15 Volts"
Para resolver o Clock Drift, o emissor transmite um "Tom de START" (3500 Hz) para zerar o cronômetro do receptor antes dos dados.

**O Dilema Teórico:** Num sistema digital elétrico onde 5V é "0" e 10V é "1", utilizar um tom alienígena de 3500 Hz não seria o equivalente a enviar 15V apenas para iniciar o sistema? Isso existe na realidade?
Sim e não. Em telecomunicações reais, existem duas formas de resolver isto:

1. **Sinalização Fora de Banda (Out-of-Band):** É exatamente o que fizemos. Utiliza-se um canal ou frequência completamente separado da banda de dados apenas para controle. Era comum nas antigas redes telefónicas analógicas.
2. **Sinalização Dentro da Banda (In-Band):** É como as placas de rede Ethernet e Wi-Fi modernas operam. Como não podem inventar "15 Volts", elas utilizam os próprios níveis de tensão válidos, enviando um Preâmbulo de transições repetidas e previsíveis (ex: `10101010`). O hardware receptor utiliza um circuito chamado PLL (*Phase-Locked Loop*) para ajustar o seu relógio ao ritmo dessas subidas e descidas de tensão. No final do preâmbulo, envia-se um SFD (*Start Frame Delimiter*) que avisa: *"O relógio está sincronizado, a partir de agora são os dados reais"*.

No nosso projeto acústico via software, simular um PLL exigiria um processamento de DSP brutal em tempo real. Adotar o "tom de 15 Volts" (3500 Hz) atua como uma simplificação de engenharia eficiente para garantir o **Alinhamento de Quadro** num sistema não determinístico como um Sistema Operativo moderno.

---

## 4. Detecção de Erros (Transição para a Camada de Enlace)
Devido às interferências do meio físico (ruído ambiente, vento, distorção do microfone), a Camada Física frequentemente entrega bits invertidos. O projeto implementou lógicas da Camada de Enlace para validar a integridade (*Integrity Check*) dos quadros:

* **Paridade Par (Método 1):** O 9º bit do quadro garante que o número total de bits 1 seja sempre par. Permite detetar a inversão de um único bit.
* **Checksum / Soma Lógica (Método 2):** Os últimos 4 bits do quadro contêm o valor numérico em binário representando a quantidade total de bits 1 presentes na carga de dados de 8 bits. É uma versão simplificada do CRC (*Cyclic Redundancy Check*) utilizado no protocolo Ethernet.

---

## 5. DSP: A Interface com o Sistema Operacional
Como não possuímos hardware decodificador dedicado (chips ASIC), a função do receptor foi emulada utilizando **DSP** (*Digital Signal Processing*) através do processador central (CPU).
O sinal acústico entra pela placa de som e é transformado através da biblioteca `numpy` utilizando a **FFT** (*Fast Fourier Transform*). A FFT analisa um bloco de som bruto no domínio do tempo e converte-o para o domínio da frequência, permitindo ao software atuar como um seletor de banda ultrarrápido, isolando os 1200 Hz do ruído de uma porta a bater.

---

## 6. Conclusão
O desenvolvimento deste projeto ilustra com precisão os desafios de engenharia ocultos sob as especificações teóricas de rede. A transição de uma comunicação reativa (baseada em amplitude e limites de silêncio) para uma transmissão 4-FSK síncrona exigiu a aplicação prática de conceitos como temporização de bloco, resolução espectral (FFT), e tolerância de guarda de frequências, provando que um sistema robusto depende de um casamento perfeito entre as regras da física no mundo real e a lógica matemática no software.