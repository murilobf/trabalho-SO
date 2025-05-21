import classes
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from queue import Queue

class Dashboard(tk.Tk):
    def __init__(self, filaTI: Queue):
        super().__init__()
        self.title("Gerenciador de Tarefas 0.5v")
        self.geometry("900x500")
        #self.barreira = barreira

        # FRAME: Dados globais do sistema
        # Seria a "div" externa, tem o título 
        frameSistema = ttk.Frame(self)
        frameSistema.pack(side=tk.TOP, fill=tk.X, expand=False, padx=5, pady=5)
        '''FALTA TERMINAR'''
        ttk.Label(frameSistema, text="Dados do Sistema", font=("Helvetica, 12")).pack(pady=5)

        # Guarda os frames de dados
        frameDadosSistema = ttk.Frame(frameSistema)
        frameDadosSistema.pack(fill=tk.X)

        # Os frames abaixos são os dados propriamente ditos
        self.dadoSistemaCpuUsado = tk.Label(frameDadosSistema, text="")
        self.dadoSistemaCpuUsado.pack(side=tk.LEFT,padx=10)
        self.dadoSistemaCpuLivre = tk.Label(frameDadosSistema, text="")
        self.dadoSistemaCpuLivre.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemUsada = tk.Label(frameDadosSistema, text="")
        self.dadoSistemaMemUsada.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemLivre = tk.Label(frameDadosSistema, text="")
        self.dadoSistemaMemLivre.pack(side=tk.LEFT, padx=10)

        # FRAME: Lista de processos
        frameProcessos = ttk.Frame(self)
        frameProcessos.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(frameProcessos, text="Processos em Execução", font=("Helvetica", 12)).pack(pady=5)
        self.listaProcessos = tk.Listbox(frameProcessos, width=60)
        self.listaProcessos.pack(fill=tk.BOTH, expand=True)

        # FRAME: Gráficos
        frameGraficoMemoria = ttk.Frame(self)
        frameGraficoMemoria.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        frameGraficoCpu = ttk.Frame(self)
        frameGraficoCpu.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dadosMemoria = []
        self.dadosCpu = []

        # Gráfico de uso de memória
        self.figMem, self.axMem = plt.subplots(figsize=(5, 3))
        self.axMem.set_title("Uso de Memória (%)")
        self.axMem.set_ylim(0, 100)
        self.axMem.set_xlim(0, 30)
        self.axMem.set_ylabel("Memória usada (%)")
        self.linhaMem, = self.axMem.plot([], [], 'b-')
        self.canvasMem = FigureCanvasTkAgg(self.figMem, master=frameGraficoMemoria)
        self.canvasMem.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Gráfico de uso de CPU
        self.figCpu, self.axCpu = plt.subplots(figsize=(5, 3))
        self.axCpu.set_title("Uso de CPU (%)")
        self.axCpu.set_ylim(0, 100)
        self.axCpu.set_xlim(0, 30)
        self.axCpu.set_ylabel("CPU usada (%)")
        self.linhaCpu, = self.axCpu.plot([], [], 'r-')
        self.canvasCpu = FigureCanvasTkAgg(self.figCpu, master=frameGraficoCpu)
        self.canvasCpu.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.atualiza_interface(filaTI)

    def atualiza_interface(self, filaTI: Queue):
        
        auxSistema = filaTI.get()
        self.atualiza_processos(auxSistema)
        self.atualiza_grafico(auxSistema)
        self.atualiza_sistema(auxSistema)

        self.after(1000, self.atualiza_interface, filaTI)

    def atualiza_sistema(self, sistema: classes.Sistema):
        
        self.dadoSistemaCpuUsado.config(text=f"CPU usado: {sistema.percentualProcessadorOcupado:.2f}%")
        self.dadoSistemaCpuLivre.config(text=f"CPU livre: {sistema.percentualProcessadorLivre:.2f}%")
        self.dadoSistemaMemUsada.config(text=f"RAM usada: {sistema.percentualMemOcupada:.2f}%")
        self.dadoSistemaMemLivre.config(text=f"RAM livre: {sistema.percentualMemLivre:.2f}%")

    def atualiza_processos(self, sistema: classes.Sistema):
        self.listaProcessos.delete(0, tk.END)
        for processo in sistema.retorna_processos():
            self.listaProcessos.insert(tk.END, processo.retorna_string_dados())

    def atualiza_grafico(self, sistema: classes.Sistema):
        if len(self.dadosMemoria) >= 30:
            self.dadosMemoria.pop(0)
        if len(self.dadosCpu) >= 30:
            self.dadosCpu.pop(0)

        self.dadosMemoria.append(sistema.percentualMemOcupada)
        self.dadosCpu.append(sistema.percentualProcessadorOcupado)

        self.linhaMem.set_data(range(len(self.dadosMemoria)), self.dadosMemoria)
        self.axMem.set_xlim(0, max(30, len(self.dadosMemoria)))
        self.canvasMem.draw()

        self.linhaCpu.set_data(range(len(self.dadosCpu)), self.dadosCpu)
        self.axCpu.set_xlim(0, max(30, len(self.dadosCpu)))
        self.canvasCpu.draw()
