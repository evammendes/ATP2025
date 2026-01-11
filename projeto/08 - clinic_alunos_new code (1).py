
import random
import numpy as np
import matplotlib.pyplot as plt
import json


# ============================================================
#  IMPORTAÇÃO DO SIMPLEGUI (CodeSkulptor OU SimpleGUICS2Pygame)
# ============================================================

try:
    import simplegui
except ImportError:
    try:
        import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
    except ImportError:
        simplegui = None


# ============================================================
# PARÂMETROS DEFAULT (ajustados para estudo λ=10..30)
# ============================================================

TAXA_CHEGADA = 10
NUM_MEDICOS = 3
SERVICE_DISTRIBUTION = "exponential"
MEAN_SERVICE_TIME = 15
SIMULATION_TIME = 480

CHEGADA = "CHEGADA"
SAIDA = "SAIDA"


# ============================================================
# FUNÇÕES DE FILA DE EVENTOS
# ============================================================

def enqueue(event_list, event):
    event_list.append(event)
    event_list.sort(key=lambda e: e[0])
    return event_list

def dequeue(event_list):
    ev = event_list[0]
    rest = event_list[1:]
    return ev, rest

def e_tempo(ev): return ev[0]
def e_tipo(ev): return ev[1]
def e_doente(ev): return ev[2]


# ============================================================
# MODELO DO MÉDICO
# ============================================================

def mOcupa(m): m[1] = not m[1]; return m
def mInicioConsulta(m, t): m[3] = t; return m
def mDoenteCorrente(m, d): m[2] = d; return m
def mTempoOcupado(m, v): m[4] = v; return m

def m_ocupado(m): return m[1]
def m_doente_corrente(m): return m[2]
def m_inicio_ultima_consulta(m): return m[3]
def m_total_tempo_ocupado(m): return m[4]

def procuraMedico(medicos):
    for m in medicos:
        if not m_ocupado(m):
            return m
    return None


# ============================================================
# DISTRIBUIÇÃO DE CHEGADAS — NORMAL (pedido do utilizador)
# ============================================================

def gera_intervalo_tempo_chegada(lambda_rate):
    if lambda_rate <= 0:
        return 1.0

    media = 60.0 / lambda_rate
    std = media * 0.2
    intervalo = np.random.normal(media, std)
    return max(0.1, intervalo)


# ============================================================
# DISTRIBUIÇÃO DO TEMPO DE CONSULTA
# ============================================================

def gera_tempo_consulta(dist, mean):
    if dist == "exponential":
        return np.random.exponential(mean)
    elif dist == "normal":
        return max(0.1, np.random.normal(mean, mean/3))
    elif dist == "uniform":
        return np.random.uniform(mean/2, mean*1.5)
    return mean


# ============================================================
# SIMULAÇÃO PRINCIPAL
# ============================================================

def simula(lambda_rate=TAXA_CHEGADA,
           num_doctors=NUM_MEDICOS,
           service_distribution=SERVICE_DISTRIBUTION,
           mean_service_time=MEAN_SERVICE_TIME,
           simulation_time=SIMULATION_TIME,
           debug=False):

    tempo_atual = 0.0
    contador = 1
    queueEventos = []
    queue = []

    medicos = [[f"m{i}", False, None, 0.0, 0.0] for i in range(num_doctors)]

    chegadas = {}
    tempo_atual += gera_intervalo_tempo_chegada(lambda_rate)

    while tempo_atual < simulation_time:
        did = f"d{contador}"
        contador += 1
        chegadas[did] = tempo_atual
        queueEventos = enqueue(queueEventos, (tempo_atual, CHEGADA, did))
        tempo_atual += gera_intervalo_tempo_chegada(lambda_rate)

    # estatísticas
    tempos_espera = []
    tempos_consulta = []
    tempos_total = []
    time_points = []
    queue_sizes = []
    doctor_occ = []

    tempo_atual = 0.0
    doentes_atendidos = 0

    while queueEventos:
        evento, queueEventos = dequeue(queueEventos)
        tempo_atual = e_tempo(evento)

        time_points.append(tempo_atual)
        queue_sizes.append(len(queue))
        doctor_occ.append(sum(1 for m in medicos if m_ocupado(m)) / num_doctors)

        if e_tipo(evento) == CHEGADA:
            m = procuraMedico(medicos)
            if m:
                m = mOcupa(m)
                m = mInicioConsulta(m, tempo_atual)
                dur = gera_tempo_consulta(service_distribution, mean_service_time)
                tempos_consulta.append(dur)
                m = mDoenteCorrente(m, e_doente(evento))
                tempos_espera.append(0.0)
                queueEventos = enqueue(queueEventos, (tempo_atual + dur, SAIDA, e_doente(evento)))
            else:
                queue.append((e_doente(evento), tempo_atual))

        else:  # SAIDA
            doentes_atendidos += 1

            encontrado = False
            for m in medicos:
                if not encontrado and m_doente_corrente(m) == e_doente(evento):
                    m = mTempoOcupado(m, m_total_tempo_ocupado(m) + tempo_atual - m_inicio_ultima_consulta(m))
                    m = mOcupa(m)
                    m = mDoenteCorrente(m, None)
                    encontrado = True


            tempos_total.append(tempo_atual - chegadas[e_doente(evento)])

            if queue:
                prox, tch = queue.pop(0)
                m = procuraMedico(medicos)
                m = mOcupa(m)
                m = mInicioConsulta(m, tempo_atual)
                m = mDoenteCorrente(m, prox)
                tempos_espera.append(tempo_atual - tch)
                dur = gera_tempo_consulta(service_distribution, mean_service_time)
                tempos_consulta.append(dur)
                queueEventos = enqueue(queueEventos, (tempo_atual + dur, SAIDA, prox))

    stats = {
        "tempo_medio_espera": np.mean(tempos_espera) if tempos_espera else 0,
        "tempo_medio_consulta": np.mean(tempos_consulta) if tempos_consulta else 0,
        "tempo_medio_clinica": np.mean(tempos_total) if tempos_total else 0,
        "tamanho_medio_fila": np.mean(queue_sizes),
        "tamanho_maximo_fila": max(queue_sizes),
        "ocupacao_media_medicos": np.mean([m_total_tempo_ocupado(m)/simulation_time for m in medicos]),
        "doentes_atendidos": doentes_atendidos
    }

    series = {
        "time": time_points,
        "queue": queue_sizes,
        "occ": doctor_occ
    }

    return stats, series





#COPILOT JA NAO ANALISOU
# ============================================================
# GRÁFICO ÚNICO COM 3 SUBPLOTS
# ============================================================

def plot_all_graphs(series):
    t = series["time"]
    q = series["queue"]
    occ = [x * 100 for x in series["occ"]]

    lambdas = range(10, 31)
    medias = []
    tempos_totais = []

    for lam in lambdas:
        stats, _ = simula(lambda_rate=lam)
        medias.append(stats["tamanho_medio_fila"])
        tempos_totais.append(stats["tempo_medio_clinica"])  # ← agora sim!

    plt.figure(figsize=(15, 10))  # ← espaço para 2x2 subplots

    # Subplot 1
    plt.subplot(2, 2, 1)
    plt.plot(t, q)
    plt.title("Fila de espera")
    plt.xlabel("Tempo")
    plt.ylabel("Tamanho da fila")
    plt.grid(True)

    # Subplot 2
    plt.subplot(2, 2, 2)
    plt.plot(t, occ, color="orange")
    plt.title("Ocupação dos médicos (%)")
    plt.xlabel("Tempo")
    plt.ylabel("Ocupação (%)")
    plt.grid(True)

    # Subplot 3
    plt.subplot(2, 2, 3)
    plt.plot(lambdas, medias, marker="o", color="green")
    plt.title("Fila média vs λ (10 a 30)")
    plt.xlabel("λ (doentes/hora)")
    plt.ylabel("Fila média")
    plt.grid(True)

    # Subplot 4
    plt.subplot(2, 2, 4)
    plt.plot(lambdas, tempos_totais, marker="s", color="purple")
    plt.title("Tempo médio na clínica vs λ")
    plt.xlabel("λ (doentes/hora)")
    plt.ylabel("Tempo médio (min)")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


# ============================================================
# GUI
# ============================================================

gui_lambda = TAXA_CHEGADA
gui_doctors = NUM_MEDICOS
gui_dist = SERVICE_DISTRIBUTION
gui_mean = MEAN_SERVICE_TIME
gui_time = SIMULATION_TIME

last_stats = None
last_series = None
results_label = None
pessoas_label = None
frame = None
label_intro = None
input_password= None


def run_sim():
    global last_stats, last_series
    last_stats, last_series = simula(
        lambda_rate=gui_lambda,
        num_doctors=gui_doctors,
        service_distribution=gui_dist,
        mean_service_time=gui_mean,
        simulation_time=gui_time
    )

    texto = (
        "=== RESULTADOS ===\n"
        f"Doentes atendidos: {last_stats['doentes_atendidos']}\n"
        f"Tempo médio de espera: {last_stats['tempo_medio_espera']:.2f} min\n"
        f"Tempo médio de consulta: {last_stats['tempo_medio_consulta']:.2f} min\n"
        f"Tempo médio na clínica: {last_stats['tempo_medio_clinica']:.2f} min\n"
        f"Tamanho médio da fila: {last_stats['tamanho_medio_fila']:.2f}\n"
        f"Tamanho máximo da fila: {last_stats['tamanho_maximo_fila']}\n"
        f"Ocupação média dos médicos: {last_stats['ocupacao_media_medicos']*100:.2f}%\n"
    )

    print(texto)

    if results_label:
        results_label.set_text(texto)


def show_graphs():
    if last_series:
        plot_all_graphs(last_series)
    else:
        print("Corre uma simulação primeiro.")


def inp_lambda(t):
    global gui_lambda
    gui_lambda = float(t)

def inp_docs(t):
    global gui_doctors
    gui_doctors = int(t)

def inp_mean(t):
    global gui_mean
    gui_mean = float(t)

def inp_time(t):
    global gui_time
    gui_time = float(t)

def set_exp():
    global gui_dist
    gui_dist = "exponential"
    print("Distribuição: exponential")

def set_norm():
    global gui_dist
    gui_dist = "normal"
    print("Distribuição: normal")

def set_uni():
    global gui_dist
    gui_dist = "uniform"
    print("Distribuição: uniform")


# ============================================================
# FUNÇÕES DE ESTILO (FUNDO AZUL + BOTÕES AMARELOS)
# ============================================================

def estiliza_botoes(canvas):
    try:
        for btn in frame._buttons:
            btn.set_bg_color("yellow")
            btn.set_text_color("black")
    except AttributeError:
        pass # ignora se _buttons não existir


# ---- 1) Depois da password, montamos os controlos da simulação no MESMO frame ----

def setup_sim_controls():
    global frame, results_label, pessoas_label

    frame.add_label("")
    frame.add_label(" === PARÂMETROS DA SIMULAÇÃO ===")

    frame.add_label("Taxa de chegada (λ por hora)")
    frame.add_input("Escreve um valor:", inp_lambda, 100)

    frame.add_label("Número de médicos")
    frame.add_input("Escolhe o nº:", inp_docs, 100)

    frame.add_label("Tempo médio de consulta (min)")
    frame.add_input("Define um tempo:", inp_mean, 100)

    frame.add_label("Tempo total de simulação (min)")
    frame.add_input("Quanto tempo:", inp_time, 100)

    frame.add_label("")
    frame.add_label(" ——— Distribuição do Tempo de Serviço ———")
    frame.add_button("Exponencial", set_exp)
    frame.add_button("Normal", set_norm)
    frame.add_button("Uniforme", set_uni)

    frame.add_label("")
    frame.add_label(" === EXECUÇÃO ===")
    frame.add_button("Correr simulação", run_sim)
    frame.add_button("Ver gráficos", show_graphs)

    frame.add_label("")
    results_label = frame.add_label(" Resultados aparecerão aqui...")

    frame.add_label("")
    frame.add_label("=== FICHEIRO JSON ===")
    frame.add_button("Carregar pessoas do JSON", carregar_pessoas)
    pessoas_label = frame.add_label("Dados das pessoas aparecerão aqui...")


# ---- 2) Verificação da password ----

def verifica_password(p):
    global label_intro
    if p == "clinica123":  # a tua palavra-passe
        label_intro.set_text("Acesso autorizado. Carrega nos botões para simular.")
        setup_sim_controls()
    else:
        label_intro.set_text("Palavra-passe incorreta. Tenta novamente.")


def clicar_entrar():
    global input_password
    password = input_password.get_text()
    verifica_password(password)


# ---- 3) Criação do único frame (com fundo azul) ----

def dummy_password_handler(text):
    pass


def create_gui():
    global frame, label_intro, input_password

    if simplegui is None:
        print("Instala SimpleGUICS2Pygame para usar o GUI:")
        print("pip install SimpleGUICS2Pygame")
        return

    # Primeiro criamos o frame
    frame = simplegui.create_frame("Simulação Clínica", 1000, 800)
    frame.set_canvas_background("lightblue")  # Fundo azul

    # Agora podemos adicionar os labels
    frame.add_label(" Simulação Clínica")
    frame.add_label("Modelação de fila de espera em consulta")
    frame.add_label(" ")

    frame.add_label("Acesso à simulação")
    frame.add_label("Insere a palavra-passe para continuar:")

    input_password = frame.add_input("Palavra-passe", dummy_password_handler, 200)
    frame.add_button("Entrar", clicar_entrar)

    label_intro = frame.add_label("")

    frame.set_draw_handler(estiliza_botoes)

    frame.start()


# ============================================================
# IMPORTAÇÃO E VISUALIZAÇÃO DO FICHEIRO JSON DE PESSOAS
# ============================================================

dados_pessoas = []  # Lista global para guardar os dados do JSON
pessoas_label = None  # Referência ao label da interface

def carregar_pessoas():
    global dados_pessoas, pessoas_label
    try:
        with open("pessoas.json", "r", encoding="utf-8") as f:
            dados_pessoas = json.load(f)
            texto = "=== Pessoas carregadas ===\n\n"
            for i, p in enumerate(dados_pessoas, start=1):
                nome = p.get("nome", "N/A")
                idade = p.get("idade", "N/A")
                prioridade = p.get("prioridade", "N/A")
                texto += f"{i}. Nome: {nome}\n   Idade: {idade}\n   Prioridade: {prioridade}\n\n"
            print(texto)
            if pessoas_label:
                pessoas_label.set_text(texto)
    except Exception as e:
        print("Erro ao carregar pessoas:", e)
        if pessoas_label:
            pessoas_label.set_text("Erro ao carregar ficheiro JSON.")


# ============================================================
# ARRANQUE DIRETO NO GUI
# ============================================================

if __name__ == "__main__":
    create_gui()

    