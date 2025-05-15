import classes
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class Dashboard(tk.Tk):
    def __init__(self, sistema: classes.Sistema):
        super().__init__()
        self.title("Gerenciador de Tarefas 0.5v")
        self.geometry("900x500")

        # FRAME: Lista de processos
        frame_processos = ttk.Frame(self)
        frame_processos.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(frame_processos, text="Processos em Execução", font=("Helvetica", 12)).pack(pady=5)
        self.lista_processos = tk.Listbox(frame_processos, width=40)
        self.lista_processos.pack(fill=tk.BOTH, expand=True)
        self.processos = []
        self.atualizar_processos(sistema)

        # FRAME: Gráfico
        frame_grafico = ttk.Frame(self)
        frame_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dados_memoria = []
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_title("Uso de Memória (%)")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 30)
        self.ax.set_ylabel("Memória usada (%)")
        self.linha, = self.ax.plot([], [], 'b-')

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.atualizar_grafico(sistema)

    def atualizar_processos(self, sistema: classes.Sistema):
        self.lista_processos.delete(0, tk.END)
        self.processos = sistema.retornaProcessos()
        self.after(5000, lambda: self.atualizar_processos(sistema))  # Atualiza lista a cada 5 segundos

    def atualizar_grafico(self, sistema: classes.Sistema):

        if len(self.dados_memoria) >= 30:
            self.dados_memoria.pop(0)
        self.dados_memoria.append(sistema.percentualMemLivre)

        self.linha.set_data(range(len(self.dados_memoria)), self.dados_memoria)
        self.ax.set_xlim(0, max(30, len(self.dados_memoria)))
        self.canvas.draw()
        self.after(5000, lambda: self.atualizar_grafico(sistema))  # Atualiza o gráfico a cada 1 segundo


