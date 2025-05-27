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
        ttk.Label(frameSistema, text="Dados do Sistema", font=("Helvetica, 12")).pack(pady=5)

        # Guarda os frames de dados
        frameDadosCpuSistema = ttk.Frame(frameSistema)
        frameDadosCpuSistema.pack(fill=tk.X, pady=5)
        frameDadosMemSistema = ttk.Frame(frameSistema)
        frameDadosMemSistema.pack(fill=tk.X, pady=5)
        frameDadosOutrosSistema = ttk.Frame(frameSistema)
        frameDadosOutrosSistema.pack(fill=tk.X, pady=5)

        # Os frames abaixos são os dados propriamente ditos
        # Esses se referem aos dados de CPU
        self.dadoSistemaCpuUsado = tk.Label(frameDadosCpuSistema, text="")
        self.dadoSistemaCpuUsado.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaCpuLivre = tk.Label(frameDadosCpuSistema, text="")
        self.dadoSistemaCpuLivre.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaCpuOcioso = tk.Label(frameDadosCpuSistema, text="")
        self.dadoSistemaCpuOcioso.pack(side=tk.LEFT,padx=10)

        #Esses se referem aos dados de memória
        self.dadoSistemaMemLivre = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemLivre.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemTotal = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemTotal.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemUsadaPer = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemUsadaPer.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemLivrePer = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemLivrePer.pack(side=tk.LEFT, padx=10)

        #Esses se referem a outros dados que até se encaixam nos critérios acima, mas que por estética estão separados
        self.dadoSistemaMemVirtual = tk.Label(frameDadosOutrosSistema, text="")
        self.dadoSistemaMemVirtual.pack(side=tk.LEFT, padx=10)
        
        # Dados adicionais: quantidade de processos e threads
        self.dadoSistemaQtdProcessos = tk.Label(frameDadosOutrosSistema, text="")
        self.dadoSistemaQtdProcessos.pack(side=tk.LEFT, padx=10)

        self.dadoSistemaQtdThreads = tk.Label(frameDadosOutrosSistema, text="")
        self.dadoSistemaQtdThreads.pack(side=tk.LEFT, padx=10)

        # FRAME: Lista de processos
        frameProcessos = ttk.Frame(self)
        frameProcessos.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(frameProcessos, text="Processos em Execução", font=("Helvetica", 12)).pack(pady=5)
        self.listaProcessos = tk.Listbox(frameProcessos, width=60)
        self.listaProcessos.pack(fill=tk.BOTH, expand=True)
        # Binda um evento (no caso, chamar a função mostra_detalhes_processo) aos elementos da lista de processos
        self.listaProcessos.bind("<<ListboxSelect>>", self.mostra_detalhes_processo)

        # FRAME: Gráficos
        frameGraficoMemoria = ttk.Frame(self)
        frameGraficoMemoria.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        frameGraficoCpu = ttk.Frame(self)
        frameGraficoCpu.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dadosMemoria = []
        self.dadosCpu = []
        self.listaObjetosProcessos = []

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

    #Chama as funções que vão atualizar o dashboard
    def atualiza_interface(self, filaTI: Queue):
        
        auxSistema = filaTI.get()
        self.atualiza_processos(auxSistema)
        self.atualiza_grafico(auxSistema)
        self.atualiza_sistema(auxSistema)

        self.after(1000, self.atualiza_interface, filaTI)

    #Atualiza os dados mostrados na parte de sistema global (aba superior)
    def atualiza_sistema(self, sistema: classes.Sistema):
        
        #Dados principais de memória
        self.dadoSistemaMemTotal.config(text=f"Memória RAM total: {sistema.memFisicaKB}KB ou {sistema.memFisicaGB}GB")
        self.dadoSistemaMemLivre.config(text=f"RAM livre: {sistema.memLivreKB}KB ou {sistema.memLivreGB}GB")
        #Porcentagens
        self.dadoSistemaCpuUsado.config(text=f"Porcentagem da CPU usada: {sistema.percentualProcessadorOcupado:.2f}%")
        self.dadoSistemaCpuLivre.config(text=f"Porcentagem da CPU livre: {sistema.percentualProcessadorLivre:.2f}%")
        self.dadoSistemaCpuOcioso.config(text=f"Porcentagem de tempo em que a CPU estava ociosa: {sistema.percentualProcessadorOcioso:.2f}%")
        self.dadoSistemaMemUsadaPer.config(text=f"Porcentagem de RAM usada: {sistema.percentualMemOcupada:.2f}%")
        self.dadoSistemaMemLivrePer.config(text=f"Porcentagem de RAM livre: {sistema.percentualMemLivre:.2f}%")
        #Quantidade de processos e threads do sistema
        self.dadoSistemaQtdProcessos.config(text=f"Quantidade de processos: {sistema.quantidadeProcessos}")
        self.dadoSistemaQtdThreads.config(text=f"Quantidade de threads: {sistema.quantidadeThreads}")
        #Outros dados relevantes
        self.dadoSistemaMemVirtual.config(text=f"Memória usada para o endereçamento virtual: {sistema.memVirtualKB}KB ou {sistema.memVirtualGB}GB")

    #Atualia a lista de processos
    def atualiza_processos(self, sistema: classes.Sistema):
        #Pega todos os elementos atualmente na lista de processos do objeto sistema
        self.listaObjetosProcessos = sistema.retorna_processos()

        #Deleta a lista anterior (apenas na interface)
        self.listaProcessos.delete(0,tk.END)
        #Imprime os elementos dessa lista
        for processo in self.listaObjetosProcessos:
            self.listaProcessos.insert(tk.END, processo.retorna_string_dados())

    #Atualiza os gráficos de uso de memória e CPU
    def atualiza_grafico(self, sistema: classes.Sistema):

        #Apaga o ponto mais velho quando houver mais que 30 elementos na lista
        if len(self.dadosMemoria) >= 30:
            self.dadosMemoria.pop(0)
        if len(self.dadosCpu) >= 30:
            self.dadosCpu.pop(0)

        #Adiciona mais um ponto
        self.dadosMemoria.append(sistema.percentualMemOcupada)
        self.dadosCpu.append(sistema.percentualProcessadorOcupado)

        #Desenha o gráfico
        self.linhaMem.set_data(range(len(self.dadosMemoria)), self.dadosMemoria)
        self.axMem.set_xlim(0, max(30, len(self.dadosMemoria)))
        self.canvasMem.draw()

        self.linhaCpu.set_data(range(len(self.dadosCpu)), self.dadosCpu)
        self.axCpu.set_xlim(0, max(30, len(self.dadosCpu)))
        self.canvasCpu.draw()

    def mostra_detalhes_processo(self, event):
        selecao = self.listaProcessos.curselection()
        if not selecao:
            return

        #Pega o índice equivalente ao processo da lista de processos clicada pelo usuário
        indice = selecao[0]
        processo = self.listaObjetosProcessos[indice]  

        janelaDetalhes = tk.Toplevel(self)
        janelaDetalhes.title("Detalhes do Processo")
        janelaDetalhes.geometry("400x500")

        #Destrói a janela quando o usuário clica fora dela
        janelaDetalhes.bind("<FocusOut>",lambda e: janelaDetalhes.destroy())
        # Exiba informações extras do processo
        tk.Label(janelaDetalhes, text=f"PID: {processo.pid}").pack()
        tk.Label(janelaDetalhes, text=f"Nome: {processo.nome}").pack()
        tk.Label(janelaDetalhes, text=f"Usuário: {processo.usuario}").pack()        
        tk.Label(janelaDetalhes, text=f"Quantidade de Threads: {processo.qtdeThreads}").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade de memória alocada: {processo.memAlocada}KB").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade total de páginas na memória: {processo.qtdePaginasTotal}").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade de páginas de TEXT: {processo.qtdePaginasCodigo}").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade de páginas de DATA+STACK: {processo.qtdePaginasOutros}").pack()

        # Separador da parte das Threads
        ttk.Separator(janelaDetalhes, orient='horizontal').pack(fill='x', pady=5)
        tk.Label(janelaDetalhes, text="Threads do Processo:", font=('Helvetica', 10, 'bold')).pack()

        # Frame com scrollbar para listar threads
        frameThreads = tk.Frame(janelaDetalhes)
        frameThreads.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frameThreads)
        scrollbar = tk.Scrollbar(frameThreads, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Preenche com as threads
        for thread in processo.threads:
            tk.Label(scrollable_frame, text=f"TID: {thread.tid} | Nome: {thread.nomeThread} | Estado: {thread.estadoThread}").pack(anchor='w', padx=10)
