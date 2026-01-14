

# RELATORIO PROJETO ALGORITMOS E TECNICAS DE PROGRAMACAO
# UNIVERSIDADE DO MINHO 25/26
# GRUPO 19


# Sistema de Simulacao de Clinica Medica 

Um sistema desenvolvido em Python para gestao e analise de simulacoes clinicas. O sistema disponibiliza uma **Interface Grafica (FreeSimpleGUI)** simples e intuitiva.


## Requisitos

- Python 3.7 ou superior


## Instalacao

1. Instalar os pacotes necessários:
```bash
pip install numpy matplotlib FreeSimpleGUI
```

## Correr a aplicação

-Para carregar o sistema clinico é necessário:

python atpfinal.py


### Estrutura Projeto:

Projeto/
├── atpfinal.py                         # Aplicacao principal, GUI e motor de simulacao
├── data/
│   ├── pessoas.json                    # Dataset para geraçao de perfis de pacientes 
└── README.md                           # Relatorio do projeto


## Introducao
No contexto da unidade curricular de Algoritmos e Tecnicas de Programacao, foi desenvolvido um projeto que consiste na criacao de uma aplicacao em Python destinada a simular o funcionamento de uma clinica medica. Este sistema modela a chegada aleatoria de pacientes, o atendimento por parte dos medicos disponiveis e a duracao das consultas, possibilitando a recolha de diversas estatisticas, tais como o tempo medio de espera, o estado de ocupacao dos medicos e a evolucao das filas de espera.  
O principal objetivo deste trabalho e estudar o comportamento do sistema, analisando a influencia de diferentes parametros, nomeadamente a taxa de chegada dos pacientes, o numero de medicos em servico e a distribuicao dos tempos de consulta.  
Neste relatorio e apresentada a descricao da base de dados utilizada, a arquitetura do sistema implementado, os principais resultados obtidos atraves de representacoes graficas e uma analise critica do desempenho da simulacao.


## Base de Dados
O sistema utiliza um repositorio de dados em formato JSON: pessoas.json, que contem as informacoes dos varios pacientes.
- Dataset Pacientes: pessoas.json 


## Simulação de parâmetros

NUM_MEDICOS = 3           

TAXA_CHEGADA = 10 / 60    # 10 doentes por h -> para min

TEMPO_MEDIO_CONSULTA = 15 

TEMPO_SIMULACAO = 8 * 60  # aprox 8h

DISTRIBUICAO_TEMPO_CONSULTA = "exponential"; "normal"; "uniforme" 


## Interface Grafica, Simple GUI Anexos

A interface grafica do sistema oferece uma navegacao intuitiva atraves de varios botoes, permitindo configurar, executar e analisar a simulacao de forma eficiente, a chegada de pessoas a clinica, a ocupacao medica, o tempo medio de espera e de consulta, bem como o tempo total passado na clinica.


## Area de Apresentacao de Resultados

A area de leitura principal da interface e constituida por uma caixa de texto, utilizada para apresentar mensagens, resultados da simulacao e analises do sistema. Os resultados sao apresentados de forma sequencial e clara, permitindo acompanhar simulacao e interpretar os dados produzidos.


## Estrutura e Modo de Organizacao da Janela Principal

Interface principal dividida em duas colunas, do lado esquerdo com botoes e caixas de texto para inserir valores e do lado direito uma janela, em que apos ocorrer simulacao nos mostra os resultados carregados na interface e os dados dos pacientes, do ficheiro Json.


## Ecra de Login

A clinica e os seus respetivos dados, tem um acesso protegido por palavra-passe, que impede alteracoes ou simulacoes sem autorizacao.


## Parametros da Clinica

Comecamos por definir os dados com os valores que queremos, para os doentes por hora, numero de medicos, tempo da consulta e duracao da simulacao.


## Funcionalidades dos botoes

- **Configurar Simulacao**
  - Definir os parâmetros da simulação
  - Ajustar taxas de chegada
  - Selecionar o modelo de distribuição estatística

- **Executar Simulacao**
  - Iniciar o motor de simulação
  - Registar eventos em tempo real
  - Processamento dos atendimentos
  
- **Estatisticas**
  - Evolucao da fila ao longo do tempo
  - Ocupação dos médicos durante a simulacao
  - Taxa media da fila vs Taxa de Chegada
  - Tempo de cada paciente na clinica


## Explicacao

**Configurar Simulacao:** Esta opcao permite ao utilizador definir os parametros principais da simulacao antes da sua execucao. Atraves de uma janela, e possivel configurar o numero de medicos disponiveis, o tempo total de simulacao, a taxa de chegada de doentes e a distribuicao do tempo de consulta. Estas configuracoes influenciam diretamente o comportamento e os resultados do sistema.

**Distribuicao:** Estes botoes permitem escolher o tipo de grafico e modelo de Distribuicao Estatistica que queremos observar: Exponencial, Normal e Uniforme.

**Executar Simulacao:** Inicia o processo de simulacao com base nos parametros previamente definidos. Apos a execucao, os principais resultados sao apresentados na area de output, o que permite ao utilizador analisar detalhadamente e registar eventos em tempo real o comportamento da fila de espera durante a simulacao incluindo informacoes como o tamanho medio da fila e dados gerais da simulacao.

**Carregar pessoas do Json:** Carrega lista de pacientes, aparecendo no output os 2000 doentes que se encontram disponiveis no dataset e sao estas que vao constituir os graficos e a sua evolucao.


## Analise de Resultados
A simulacao gera indicadores cruciais para a gestao hospitalar. Os graficos apresentados representam:

**Evolucao do tamanho da fila ao longo do tempo:** Este grafico evidencia um crescimento inicial do tamanho da fila, resultado da adaptacao do sistema a taxa de chegada de doentes. Apos esse periodo, observa-se uma estabilizacao da fila, indicando que a capacidade de atendimento da clinica e suficiente para absorver a procura na maioria do tempo. No entanto, pequenos picos revelam momentos pontuais de congestionamento;

**Ocupacao dos medicos:** Apresenta a ocupacao de cada medico ao longo de toda a simulacao. Valores muito altos representam o limite dos consultorios a serem ocupados por consultas enquanto valores muito baixos, poderao mostrar excesso de medicos para determinada especialidade;

**Tamanho Medio da Fila vs Taxa de Chegada de pacientes:** O tamanho medio da fila foi calculado como uma media ponderada pelo tempo, refletindo o numero medio de doentes em espera ao longo da simulacao. A medida que a taxa de chegada aumenta o tamanho da fila aumenta de modo proporcional, devido a maior afluencia para um mesmo numero de medicos, levando ao congestionamento da fila.  

**Tempo medio na clinica por paciente:** Este grafico representa o tempo medio que cada paciente permanece na clinica, desde a sua chegada ate ao final da consulta. Este valor inclui tanto o tempo de espera na fila como o tempo efetivo de atendimento medico. Observa-se que, a medida que a taxa de chegada de doentes aumenta ou o numero de medicos se mantem limitado, o tempo medio na clinica tende a aumentar, refletindo o crescimento das filas e dos tempos de espera. Este comportamento evidencia o impacto direto da carga do sistema na experiencia do paciente e no desempenho global da clinica.


## Conclusao

No ambito deste projeto foi implementada uma simulacao do funcionamento de uma clinica medica, permitindo gerir a chegada dos doentes, o atendimento realizado pelos medicos e a recolha de indicadores de desempenho do sistema. A simulacao revelou-se eficaz na representacao de cenarios realistas, evidenciando situacoes de congestionamento, variacoes na carga de trabalho e os efeitos resultantes da alteracao dos parametros de configuracao.  
A analise dos resultados obtidos permitiu verificar que a taxa de chegada dos doentes e o numero de medicos disponiveis influenciam diretamente o tamanho das filas de espera e os tempos medios de atendimento. Verificou-se ainda que, para valores elevados da taxa de chegada, o sistema tende a atingir rapidamente um estado de saturacao, comprometendo o seu desempenho.  
Em sintese, este trabalho possibilitou a aplicacao pratica de conceitos fundamentais abordados na unidade curricular de Algoritmos e Tecnicas de Programacao, essenciais para o desenvolvimento de sistemas de engenharia eficientes, como a utilizacao de filas de prioridade, simulacao de eventos discretos e uma estrutura modular do codigo. Apesar das simplificacoes adotadas, o modelo desenvolvido constitui uma base solida para futuras extensoes, tais como a inclusao de pausas dos medicos, diferentes horarios de funcionamento ou a realizacao de multiplas simulacoes para uma analise estatistica mais aprofundada.













