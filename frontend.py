import classes
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
from queue import Queue

lock = threading.Lock()

class Dashboard(tk.Tk):
    def __init__(self, fila_ti: Queue):
        super().__init__()
        self.title("Gerenciador de Tarefas 0.5v")
        self.geometry("900x500")
        #self.barreira = barreira

        # FRAME: Dados globais do sistema
        frame_sistema = ttk.Frame(self)
        frame_sistema.pack(side=tk.TOP, fill=tk.X, expand=False, padx=5, pady=10)
        '''FALTA TERMINAR'''
        ttk.Label(frame_sistema, text="Dados do Sistema", font=("Helvetica, 12")).pack(pady=5)
        self.dados_sistema = tk.Label(frame_sistema, height=10)
        self.dados_sistema.pack(fill=tk.BOTH, expand=True)

        # FRAME: Lista de processos
        frame_processos = ttk.Frame(self)
        frame_processos.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(frame_processos, text="Processos em Execução", font=("Helvetica", 12)).pack(pady=5)
        self.lista_processos = tk.Listbox(frame_processos, width=60)
        self.lista_processos.pack(fill=tk.BOTH, expand=True)

        # FRAME: Gráficos
        frame_grafico_memoria = ttk.Frame(self)
        frame_grafico_memoria.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        frame_grafico_cpu = ttk.Frame(self)
        frame_grafico_cpu.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dados_memoria = []
        self.dados_cpu = []

        # Gráfico de uso de memória
        self.fig_mem, self.ax_mem = plt.subplots(figsize=(5, 3))
        self.ax_mem.set_title("Uso de Memória (%)")
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_xlim(0, 30)
        self.ax_mem.set_ylabel("Memória usada (%)")
        self.linha_mem, = self.ax_mem.plot([], [], 'b-')
        self.canvas_mem = FigureCanvasTkAgg(self.fig_mem, master=frame_grafico_memoria)
        self.canvas_mem.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Gráfico de uso de CPU
        self.fig_cpu, self.ax_cpu = plt.subplots(figsize=(5, 3))
        self.ax_cpu.set_title("Uso de CPU (%)")
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_xlim(0, 30)
        self.ax_cpu.set_ylabel("CPU usada (%)")
        self.linha_cpu, = self.ax_cpu.plot([], [], 'r-')
        self.canvas_cpu = FigureCanvasTkAgg(self.fig_cpu, master=frame_grafico_cpu)
        self.canvas_cpu.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.atualiza_interface(fila_ti)

    def atualiza_interface(self, fila_ti: Queue):
        
        auxSistema = fila_ti.get()
        self.atualizar_processos(auxSistema)
        self.atualizar_grafico(auxSistema)

        # Após atualização, libera a barreira
        '''try:
            self.barreira.wait()
        except threading.BrokenBarrierError:
            pass'''
        self.after(1000, self.atualiza_interface, fila_ti)

    def atualizar_sistemas(self):
        self.info_sistema.delete(0, tk.END)

    def atualizar_processos(self, sistema: classes.Sistema):
        self.lista_processos.delete(0, tk.END)
        for processo in sistema.retornaProcessos():
            self.lista_processos.insert(tk.END, processo.retornaStringDados())

    def atualizar_grafico(self, sistema: classes.Sistema):
        if len(self.dados_memoria) >= 30:
            self.dados_memoria.pop(0)
        if len(self.dados_cpu) >= 30:
            self.dados_cpu.pop(0)

        self.dados_memoria.append(sistema.percentualMemOcupada)
        self.dados_cpu.append(sistema.percentualProcessadorOcupado)

        self.linha_mem.set_data(range(len(self.dados_memoria)), self.dados_memoria)
        self.ax_mem.set_xlim(0, max(30, len(self.dados_memoria)))
        self.canvas_mem.draw()

        self.linha_cpu.set_data(range(len(self.dados_cpu)), self.dados_cpu)
        self.ax_cpu.set_xlim(0, max(30, len(self.dados_cpu)))
        self.canvas_cpu.draw()
