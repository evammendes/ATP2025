
import random
import numpy as np
import matplotlib.pyplot as plt
import json


#  IMPORTAÇÃO DO SIMPLEGUI 

try:
    import simplegui
except ImportError:
    try:
        import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
    except ImportError:
        simplegui = None



# PARÂMETROS - λ=10..30

TAXA_CHEGADA = 10
NUM_MEDICOS = 3
SERVICE_DISTRIBUTION = "exponential"
MEAN_SERVICE_TIME = 15
SIMULATION_TIME = 480

CHEGADA = "CHEGADA"
SAIDA = "SAIDA"



# FUNÇÕES DE FILA DE EVENTOS


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



# MODELO DO MÉDICO


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



# DISTRIBUIÇÃO DE CHEGADAS — NORMAL 


def gera_intervalo_tempo_chegada(lambda_rate):
    if lambda_rate <= 0:
        return 1.0

    media = 60.0 / lambda_rate
    std = media * 0.2
    intervalo = np.random.normal(media, std)
    return max(0.1, intervalo)



# DISTRIBUIÇÃO DO TEMPO DE CONSULTA


def gera_tempo_consulta(dist, mean):
    if dist == "exponential":
        return np.random.exponential(mean)
    elif dist == "normal":
        return max(0.1, np.random.normal(mean, mean/3))
    elif dist == "uniform":
        return np.random.uniform(mean/2, mean*1.5)
    return mean


# SIMULAÇÃO PRINCIPAL

def simula(lambda_rate=TAXA_CHEGADA,
           num_doctors=NUM_MEDICOS,
           service_distribution=SERVICE_DISTRIBUTION,
           mean_service_time=MEAN_SERVICE_TIME,
           simulation_time=SIMULATION_TIME,
           debug=False):
    
   

    # Capacidade máxima teórica por médico
    capacidade_por_medico = simulation_time / mean_service_time

    # Total de pacientes que podem ser atendidos
    capacidade_total = capacidade_por_medico * num_doctors

    # Ajusta a taxa de chegada para não saturar
    lambda_rate = min(lambda_rate, capacidade_total / (simulation_time / 60))


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
                    inicio = m_inicio_ultima_consulta(m)
                    fim = min(tempo_atual, simulation_time)

                    if inicio < simulation_time:
                        ocupado = max(0.0, fim - inicio)
                        m = mTempoOcupado(m, m_total_tempo_ocupado(m) + ocupado)

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
        "ocupacao_media_medicos": 100 * sum([m_total_tempo_ocupado(m) for m in medicos]) / (simulation_time * num_doctors),
        "doentes_atendidos": doentes_atendidos
    }

    series = {
        "time": time_points,
        "queue": queue_sizes,
        "occ": doctor_occ
    }

    return stats, series



#GRÁFICO COM 4 SUBPLOTS

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
        tempos_totais.append(stats["tempo_medio_clinica"]) 

    plt.figure(figsize=(15, 10))  

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



# GUI - VERSÃO COM 2 COLUNAS (Controles | Resultados + Pacientes)

import tkinter as tk
from tkinter import ttk

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
input_password = None


control_frame = None
right_frame = None
root = None


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
        f"Doentes atendidos: {last_stats['doentes_atendidos']}\n"
        f"Tempo espera: {last_stats['tempo_medio_espera']:.1f} min\n"
        f"Tempo consulta: {last_stats['tempo_medio_consulta']:.1f} min\n"
        f"Tempo total: {last_stats['tempo_medio_clinica']:.1f} min\n"
        f"Fila média: {last_stats['tamanho_medio_fila']:.1f}\n"
        f"Fila máxima: {last_stats['tamanho_maximo_fila']}\n"
        f"Ocupação médicos: {last_stats['ocupacao_media_medicos']:.1f}%"
    )
    
    print(texto)
    if results_label:
        results_label.config(text=texto)


def show_graphs():
    if last_series:
        plot_all_graphs(last_series)
    else:
        print("Corre uma simulação primeiro.")


def inp_lambda(t):
    global gui_lambda
    try:
        gui_lambda = float(t)
    except:
        pass


def inp_docs(t):
    global gui_doctors
    try:
        gui_doctors = int(t)
    except:
        pass


def inp_mean(t):
    global gui_mean
    try:
        gui_mean = float(t)
    except:
        pass


def inp_time(t):
    global gui_time
    try:
        gui_time = float(t)
    except:
        pass


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



# CARREGAR PESSOAS DO JSON

dados_pessoas = []


def carregar_pessoas():
    global dados_pessoas, pessoas_label
    try:
        with open("pessoas.json", "r", encoding="utf-8") as f:
            dados_pessoas = json.load(f)
            atualiza_lista_pacientes()
    except Exception as e:
        print("Erro ao carregar:", e)


def atualiza_lista_pacientes():
    """Atualiza a lista de pacientes no lado direito"""
    global pessoas_label
    
    if not pessoas_label:
        return
    

    for widget in pessoas_label.winfo_children():
        widget.destroy()
    
    # Mostra os pacientes
    n = len(dados_pessoas)
    titulo = tk.Label(pessoas_label, text=f"PACIENTES ({n})", font=("Arial", 10, "bold"), bg="#ecf0f1")
    titulo.pack(fill="x", padx=5, pady=5)
    
    
    canvas = tk.Canvas(pessoas_label, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(pessoas_label, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Adiciona pacientes à lista
    for i, p in enumerate(dados_pessoas):
        nome = p.get("nome", "N/A")
        prioridade = p.get("prioridade", "Normal")
        
        # Cor baseada na prioridade
        cor_fundo = "#ffe6e6" if prioridade == "Alta" else "#e6f2ff" if prioridade == "Média" else "#f0f0f0"
        
        item = tk.Frame(scrollable_frame, bg=cor_fundo, relief="flat", bd=1)
        item.pack(fill="x", padx=3, pady=2)
        
        label_info = tk.Label(
            item,
            text=f"{i+1}. {nome[:20]}\n   Prioridade: {prioridade}",
            font=("Arial", 9),
            bg=cor_fundo,
            justify="left"
        )
        label_info.pack(fill="x", padx=5, pady=3)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")



# PASSWORD

def verifica_password(p):
    global label_intro
    if p == "clinica123":
        label_intro.config(text="✓ Acesso autorizado")
        setup_sim_controls()
    else:
        label_intro.config(text="✗ Password incorreta")


def clicar_entrar(event=None):
    global input_password
    password = input_password.get()
    verifica_password(password)



# SETUP - CONTROLS (Coluna esquerda)


def setup_sim_controls():
    global control_frame, right_frame, results_label, pessoas_label
    
    # Esconde a tela de login
    for widget in control_frame.winfo_children():
        widget.destroy()
    
    # COLUNA ESQUERDA (CONTROLOS)
    left_panel = tk.Frame(control_frame, bg="#ecf0f1")
    left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    # Título
    title = tk.Label(left_panel, text="SIMULAÇÃO", font=("Arial", 12, "bold"), bg="#ecf0f1")
    title.pack(pady=5)
    
    # PARÂMETROS
    section_params = tk.Label(left_panel, text="PARÂMETROS", font=("Arial", 10, "bold"), bg="#ecf0f1")
    section_params.pack(pady=(10, 5))
    
    tk.Label(left_panel, text="λ (doentes/h):", bg="#ecf0f1").pack(anchor="w")
    entry_lambda = tk.Entry(left_panel, width=20)
    entry_lambda.insert(0, str(TAXA_CHEGADA))
    entry_lambda.pack(padx=5, pady=2)
    entry_lambda.bind("<KeyRelease>", lambda e: inp_lambda(entry_lambda.get()))
    
    tk.Label(left_panel, text="Nº médicos:", bg="#ecf0f1").pack(anchor="w", pady=(5, 0))
    entry_docs = tk.Entry(left_panel, width=20)
    entry_docs.insert(0, str(NUM_MEDICOS))
    entry_docs.pack(padx=5, pady=2)
    entry_docs.bind("<KeyRelease>", lambda e: inp_docs(entry_docs.get()))
    
    tk.Label(left_panel, text="Tempo consulta (min):", bg="#ecf0f1").pack(anchor="w", pady=(5, 0))
    entry_mean = tk.Entry(left_panel, width=20)
    entry_mean.insert(0, str(MEAN_SERVICE_TIME))
    entry_mean.pack(padx=5, pady=2)
    entry_mean.bind("<KeyRelease>", lambda e: inp_mean(entry_mean.get()))
    
    tk.Label(left_panel, text="Duração simulação (min):", bg="#ecf0f1").pack(anchor="w", pady=(5, 0))
    entry_time = tk.Entry(left_panel, width=20)
    entry_time.insert(0, str(SIMULATION_TIME))
    entry_time.pack(padx=5, pady=2)
    entry_time.bind("<KeyRelease>", lambda e: inp_time(entry_time.get()))
    
    # DISTRIBUIÇÃO
    section_dist = tk.Label(left_panel, text="DISTRIBUIÇÃO", font=("Arial", 10, "bold"), bg="#ecf0f1")
    section_dist.pack(pady=(10, 5))
    
    btn_frame_dist = tk.Frame(left_panel, bg="#ecf0f1")
    btn_frame_dist.pack(fill="x", padx=5, pady=3)
    tk.Button(btn_frame_dist, text="Exponencial", command=set_exp, bg="#3498db", fg="white", width=12).pack(side="left", padx=2)
    
    btn_frame_dist2 = tk.Frame(left_panel, bg="#ecf0f1")
    btn_frame_dist2.pack(fill="x", padx=5, pady=3)
    tk.Button(btn_frame_dist2, text="Normal", command=set_norm, bg="#3498db", fg="white", width=12).pack(side="left", padx=2)
    tk.Button(btn_frame_dist2, text="Uniforme", command=set_uni, bg="#3498db", fg="white", width=12).pack(side="left", padx=2)
    
    # EXECUÇÃO
    section_exec = tk.Label(left_panel, text="EXECUÇÃO", font=("Arial", 10, "bold"), bg="#ecf0f1")
    section_exec.pack(pady=(10, 5))
    
    btn_frame_exec = tk.Frame(left_panel, bg="#ecf0f1")
    btn_frame_exec.pack(fill="x", padx=5, pady=3)
    tk.Button(btn_frame_exec, text="▶ Simular", command=run_sim, bg="#27ae60", fg="white", width=12).pack(side="left", padx=2)
    tk.Button(btn_frame_exec, text=" Gráficos", command=show_graphs, bg="#3498db", fg="white", width=12).pack(side="left", padx=2)
    
    # JSON
    section_json = tk.Label(left_panel, text="DADOS", font=("Arial", 10, "bold"), bg="#ecf0f1")
    section_json.pack(pady=(10, 5))
    tk.Button(left_panel, text=" Carregar JSON", command=carregar_pessoas, bg="#9b59b6", fg="white", width=20).pack(padx=5, pady=3)
    
    # COLUNA DIREITA (RESULTADOS + PACIENTES)
    for widget in right_frame.winfo_children():
        widget.destroy()
    
    right_panel = tk.Frame(right_frame, bg="white", relief="sunken", bd=1)
    right_panel.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Resultados
    results_title = tk.Label(right_panel, text="RESULTADOS", font=("Arial", 10, "bold"), bg="white")
    results_title.pack(anchor="w", padx=5, pady=(5, 3))
    
    results_label = tk.Label(
        right_panel,
        text="Clica 'Simular' para ver resultados...",
        font=("Arial", 9),
        justify="left",
        bg="#f9f9f9",
        relief="flat",
        padx=8,
        pady=8,
        anchor="nw"
    )
    results_label.pack(fill="x", padx=5, pady=3)
    
    # Separador
    separator = tk.Frame(right_panel, height=2, bg="#ddd")
    separator.pack(fill="x", pady=5)
    
    # Pacientes
    pessoas_label = tk.Frame(right_panel, bg="white")
    pessoas_label.pack(fill="both", expand=True, padx=5, pady=5)
    
    atualiza_lista_pacientes()


#Criar frame principal

def create_gui():
    global root, control_frame, right_frame, label_intro, input_password
    
    root = tk.Tk()
    root.title(" Simulação Clínica")
    root.geometry("1000x700")
    root.config(bg="#ecf0f1")
    
    # Login 
    top_frame = tk.Frame(root, bg="#3498db", height=80)
    top_frame.pack(fill="x")
    
    title_label = tk.Label(top_frame, text="SIMULAÇÃO CLÍNICA", font=("Arial", 14, "bold"), bg="#3498db", fg="white")
    title_label.pack(pady=5)
    
    subtitle_label = tk.Label(top_frame, text="Modelação de fila de espera", font=("Arial", 10), bg="#3498db", fg="white")
    subtitle_label.pack()
    
    # Password
    login_frame = tk.Frame(top_frame, bg="#3498db")
    login_frame.pack(pady=5)
    
    tk.Label(login_frame, text="Password:", font=("Arial", 10), bg="#3498db", fg="white").pack(side="left", padx=5)
    input_password = tk.Entry(login_frame, width=20, font=("Arial", 10))
    input_password.pack(side="left", padx=5)
    input_password.bind("<Return>", lambda e: clicar_entrar())
    
    tk.Button(login_frame, text="Entrar", command=clicar_entrar, bg="white", fg="#3498db", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    
    label_intro = tk.Label(top_frame, text="", font=("Arial", 9), bg="#3498db", fg="white")
    label_intro.pack(pady=3)
    
    # 2 Colunas Principais
    main_frame = tk.Frame(root, bg="#ecf0f1")
    main_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    control_frame = tk.Frame(main_frame, bg="#ecf0f1")
    control_frame.pack(side="left", fill="both", expand=True)
    
    right_frame = tk.Frame(main_frame, bg="white", relief="sunken", bd=1)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
    
    
    placeholder = tk.Label(control_frame, text="Introduce a password para começar", font=("Arial", 11), bg="#ecf0f1", fg="#999")
    placeholder.pack(pady=20)
    
    root.mainloop()


# ARRANQUE
if __name__ == "_main_":
    create_gui()