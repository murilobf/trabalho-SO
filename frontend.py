import classes
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from queue import Queue
import time
from backend import format_bytes

class Dashboard(tk.Tk):
    def __init__(self, filaTI: Queue, filaAI: Queue):
        super().__init__()
        self.title("Gerenciador de Tarefas 0.5v")
        self.geometry("900x500")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Aba principal
        self.aba_principal = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_principal, text="Dashboard")

        # Aba da árvore de diretórios
        self.aba_diretorios = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_diretorios, text="Sistema de Arquivos")

        # FRAME: Dados globais do sistema
        frameSistema = ttk.Frame(self.aba_principal)
        frameSistema.pack(side=tk.TOP, fill=tk.X, expand=False, padx=5, pady=5)
        ttk.Label(frameSistema, text="Dados do Sistema", font=("Helvetica, 12")).pack(pady=5)

        frameDadosCpuSistema = ttk.Frame(frameSistema)
        frameDadosCpuSistema.pack(fill=tk.X, pady=5)
        frameDadosMemSistema = ttk.Frame(frameSistema)
        frameDadosMemSistema.pack(fill=tk.X, pady=5)
        frameDadosOutrosSistema = ttk.Frame(frameSistema)
        frameDadosOutrosSistema.pack(fill=tk.X, pady=5)
        self.frameParticoesSistema = ttk.Frame(frameSistema)
        self.frameParticoesSistema.pack(fill=tk.X, pady=5)

        self.dadoSistemaCpuUsado = tk.Label(frameDadosCpuSistema, text="")
        self.dadoSistemaCpuUsado.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaCpuLivre = tk.Label(frameDadosCpuSistema, text="")
        self.dadoSistemaCpuLivre.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaCpuOcioso = tk.Label(frameDadosCpuSistema, text="")
        self.dadoSistemaCpuOcioso.pack(side=tk.LEFT, padx=10)

        self.dadoSistemaMemLivre = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemLivre.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemTotal = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemTotal.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemUsadaPer = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemUsadaPer.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaMemLivrePer = tk.Label(frameDadosMemSistema, text="")
        self.dadoSistemaMemLivrePer.pack(side=tk.LEFT, padx=10)

        self.dadoSistemaMemVirtual = tk.Label(frameDadosOutrosSistema, text="")
        self.dadoSistemaMemVirtual.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaQtdProcessos = tk.Label(frameDadosOutrosSistema, text="")
        self.dadoSistemaQtdProcessos.pack(side=tk.LEFT, padx=10)
        self.dadoSistemaQtdThreads = tk.Label(frameDadosOutrosSistema, text="")
        self.dadoSistemaQtdThreads.pack(side=tk.LEFT, padx=10)

        frameProcessos = ttk.Frame(self.aba_principal)
        frameProcessos.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        ttk.Label(frameProcessos, text="Processos em Execução", font=("Helvetica", 12)).pack(pady=5)
        self.listaProcessos = tk.Listbox(frameProcessos, width=60)
        self.listaProcessos.pack(fill=tk.BOTH, expand=True)
        self.listaProcessos.bind("<<ListboxSelect>>", self.mostra_detalhes_processo)

        frameGraficoMemoria = ttk.Frame(self.aba_principal)
        frameGraficoMemoria.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        frameGraficoCpu = ttk.Frame(self.aba_principal)
        frameGraficoCpu.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dadosMemoria = []
        self.dadosCpu = []
        self.listaObjetosProcessos = []
        self.labelsParticoes = []

        self.figMem, self.axMem = plt.subplots(figsize=(5, 3))
        self.axMem.set_title("Uso de Memória (%)")
        self.axMem.set_ylim(0, 100)
        self.axMem.set_xlim(0, 30)
        self.axMem.set_ylabel("Memória usada (%)")
        self.linhaMem, = self.axMem.plot([], [], 'b-')
        self.canvasMem = FigureCanvasTkAgg(self.figMem, master=frameGraficoMemoria)
        self.canvasMem.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figCpu, self.axCpu = plt.subplots(figsize=(5, 3))
        self.axCpu.set_title("Uso de CPU (%)")
        self.axCpu.set_ylim(0, 100)
        self.axCpu.set_xlim(0, 30)
        self.axCpu.set_ylabel("CPU usada (%)")
        self.linhaCpu, = self.axCpu.plot([], [], 'r-')
        self.canvasCpu = FigureCanvasTkAgg(self.figCpu, master=frameGraficoCpu)
        self.canvasCpu.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        #Frame pra árvore de diretórios
        self.frameArvore = ttk.Frame(self.aba_diretorios)
        self.frameArvore.pack(fill=tk.BOTH, expand=True)
        
        #A árvore em si
        self.arvoreDiretorios = ttk.Treeview(self.frameArvore, columns=("tipo", "tamanho", "permissoes"), show="tree headings")
        self.arvoreDiretorios.heading("#0", text="Nome")
        self.arvoreDiretorios.heading("tipo", text="Tipo")
        self.arvoreDiretorios.heading("tamanho", text="Tamanho")
        self.arvoreDiretorios.heading("permissoes", text="Permissões")

        self.arvoreDiretorios.pack(fill=tk.BOTH, expand=True)

        #A função da árvore está separada devido ao tempo que leva pra
        self.atualiza_arvore(filaAI)
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

        #As label para as partições
        for label in self.labelsParticoes:
            label.destroy()
        self.labelsParticoes.clear()

        # Adiciona uma nova linha para cada partição
        for particao in sistema.particoes:  
            texto = (f"{particao.nome} montado em {particao.montagem} | "
                    f"Tamanho: {particao.tamanho} | Usado: {particao.usado} | "
                    f"Livre: {particao.livre} | Uso: {particao.percentual}%")
            label = tk.Label(self.frameParticoesSistema, text=texto, anchor="w")
            label.pack(fill=tk.X, padx=20)
            self.labelsParticoes.append(label)

    #Atualia a lista de processos
    def atualiza_processos(self, sistema: classes.Sistema):
        #Salva a posição y que o usuário está na rolagem. 
        #Precisamos fazer isso pois deletamos toda a lista para reconstruir. Nisso, o usuário é enviado para o topo da lista mesmo que estivesse abaixo.
        scroll_pos = self.listaProcessos.yview()
        #Pega todos os elementos atualmente na lista de processos do objeto sistema
        self.listaObjetosProcessos = sistema.retorna_processos()

        #Deleta a lista anterior (apenas na interface)
        self.listaProcessos.delete(0,tk.END)
        #Imprime os elementos dessa lista
        for processo in self.listaObjetosProcessos:
            self.listaProcessos.insert(tk.END, processo.retorna_string_dados())

        #Move o usuário para a posição que estava anteriormente
        self.listaProcessos.yview_moveto(scroll_pos[0])

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
        tk.Label(janelaDetalhes, text=f"Prioridade: {processo.prioridade}").pack()        
        tk.Label(janelaDetalhes, text=f"Quantidade de memória total: {processo.memTotal}KB").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade de memória presente na RAM: {processo.memResidente}KB").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade total de páginas: {processo.qtdePaginasTotal}").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade de páginas presentes na RAM: {processo.qtdePaginasResidente}").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade de páginas de TEXT: {processo.qtdePaginasCodigo}").pack()
        tk.Label(janelaDetalhes, text=f"Quantidade de páginas de DATA+STACK: {processo.qtdePaginasOutros}").pack()

        # Separador da parte das Threads
        ttk.Separator(janelaDetalhes, orient='horizontal').pack(fill= 'x', pady=5)
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
            tk.Label(scrollable_frame, text=f"TID: {thread.tid} | Nome: {thread.nomeThread} | Estado: {thread.estadoThread} |").pack(anchor='w', padx=10)

    # Função para guardar os nós abertos da árvore para quando ela for refeita abrí-los de novo, de forma que o usuário não perceba que a árvore foi substituída
    def guarda_caminho_aberto(self):
        expandidos = []

        #Visita recursivamente todos os nós que estiverem abertos, guardando o id deles numa lista
        def visitar(item_id):
            if self.arvoreDiretorios.item(item_id, "open"):
                expandidos.append(self.arvoreDiretorios.item(item_id, "text"))
                for filho in self.arvoreDiretorios.get_children(item_id):
                    visitar(filho)

        #Visita o diretório ra raiz da arvore (no nosso caso ele visitaria o '/')
        for root_id in self.arvoreDiretorios.get_children():
            visitar(root_id)

        return expandidos
    
    #Pega todos os nós expandidos guardados na lista de expandidos e os reexpande
    def reexpande_caminho(self, expandidos):
        def visitar(item_id):
            nomeDiretorio = self.arvoreDiretorios.item(item_id, "text")
            if nomeDiretorio in expandidos:
                self.arvoreDiretorios.item(item_id, open=True)
                for filho in self.arvoreDiretorios.get_children(item_id):
                    visitar(filho)

        #Começa pelos nó raiz ('/' no nosso caso)
        for root_id in self.arvoreDiretorios.get_children():
            visitar(root_id)
    
    def preenche_arvore(self, pai, no: classes.NoArquivo):
        id_item = self.arvoreDiretorios.insert(
            pai,
            "end",
            text=no.nome,
            values=(no.tipoNome, (f'{format_bytes(no.tamanho*4)}'), no.permissoes) #o *4 do no.tamanho é porque o format_bytes foi feito pra coletar blocos originalmente
        )
        
        for filho in no.filhos:
            self.preenche_arvore(id_item, filho)

    def atualiza_arvore(self, filaAI: Queue):
        expandidos = self.guarda_caminho_aberto()
        raiz = filaAI.get()
        t1 = time.time()
        #Deleta a árvore anterior e a recria
        self.arvoreDiretorios.delete(*self.arvoreDiretorios.get_children())
        self.preenche_arvore("", raiz)
        t2 = time.time()

        #Reabre os nós expandidos anteriormente (se houver algum)
        self.reexpande_caminho(expandidos)
        #Quanto tempo falta para o ciclo de 60s
        tempoFaltante = int(60 - (t2 - t1))

        if(tempoFaltante > 0):
            #O tempo usado pelo after é em ms então fazemos a conversão
            tempoFaltante *= 1000
        
        #Chama a função imediatamente
        else:
            tempoFaltante = 0

        self.after(tempoFaltante, self.atualiza_arvore, filaAI)