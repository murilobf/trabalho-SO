#variavel usada pra transformar dados de memória de número de páginas para quantidade em KB
tamPaginakB = 4

class Sistema:
    def __init__(self):
        #Dados do processador
        self.dadosProcessador = []
        self.percentualProcessadorLivre = 0
        self.percentualProcessadorOcupado = 0
        self.percentualProcessadorOcioso = 0
        #Dados de memória
        self.memLivreKB = 0
        self.memLivreGB = 0
        self.memFisicaKB = 0
        self.memFisicaGB = 0
        self.memVirtualKB = 0
        self.memVirtualGB = 0
        self.percentualMemLivre = 0
        self.percentualMemOcupada = 0
        #Vetor que guarda todos os processos atualmente no sistema
        self.processos = []
        self.quantidadeProcessos = 0
        #Quantidade de Threads no processador
        self.quantidadeThreads = 0

    def adiciona_dados_processador(self, dadosProcessador: list):
        self.dadosProcessador = dadosProcessador

    def adiciona_dados_memoria(self, memFisicaKB: int, memLivreKB: int, memVirtualKB: int):
        self.memFisicaKB = memFisicaKB
        self.memLivreKB = memLivreKB
        self.memVirtualKB = memVirtualKB
        #Converte a quantidade de KB para GB ao dividí-la por 1048576 (1024*1024)
        self.memLivreGB = round((int(memLivreKB)/1048576),2)
        self.memFisicaGB = round((int(memFisicaKB)/1048576),2)
        self.memVirtualGB = round((int(memVirtualKB)/1048576),2)
        
    def adiciona_porcentagens_memoria(self, percentualMemLivre: float, percentualMemOcupada: float):
        self.percentualMemLivre = percentualMemLivre
        self.percentualMemOcupada = percentualMemOcupada

    def adiciona_porcentagens_processador(self, percentualProcessadorLivre: float, percentualProcessadorOcupado: float):
        self.percentualProcessadorLivre = percentualProcessadorLivre
        self.percentualProcessadorOcupado = percentualProcessadorOcupado

    def adiciona_porcentagem_ocioso(self, percentualOcioso: float):
        self.percentualProcessadorOcioso = percentualOcioso
        
    def adiciona_processos(self, processos):
        self.processos = processos

    def retorna_processos(self):
        return self.processos
    
    def getMemOcupada(self):
        return self.percentualMemOcupada

    def adiciona_quantidade_threads(self, qtdeThreads: int): 
        self.quantidadeThreads += qtdeThreads

    def adiciona_quantidade_processos(self, qntdeProcessos):
        self.quantidadeProcessos = qntdeProcessos

#Classe que armazena os dados de um processo
class Processo:
    
    #Função inicializadora do processo
    def __init__(self):
        
        #Dados identificadores do processo (id, nome, usuário)
        self.pid = 0
        self.nome = ""
        self.ppid = ""
        self.usuario = ""
        self.estado = ""
        self.prioridade = ""
        #Dados relativos ao requisito 2 do trabalho (memória)
        self.memTotal = 0
        self.memResidente = 0
        self.qtdePaginasTotal = 0
        self.qtdePaginasResidente = 0
        self.qtdePaginasCodigo = 0
        self.qtdePaginasOutros = 0
        #Dados sobre as threads do processo
        self.threads = []
        self.qtdeThreads = 0

    def calcula_pagina_kb(self, dadoPag):
        auxMemTotalKb = (int(dadoPag)*tamPaginakB) # Multiplicação para tornar o dado de quantidade de páginas usadas no total para tamanho em KB
        return auxMemTotalKb

    def adiciona_dados_basicos(self, pid: int, nome: str, usuario: str, estado: str, prioridade:str):
        self.pid = pid
        self.nome = nome
        self.usuario = usuario
        self.estado = estado
        self.prioridade = prioridade
    
    def adiciona_threads(self, threads: list):
        self.threads = threads
    
    def adiciona_quantidade_threads(self, qntThreadsProcesso:int):
        self.qtdeThreads = qntThreadsProcesso

    def adiciona_dados_memoria(self, qtdePaginasTotal: int, qtdePaginasResidente: int, qtdePaginasCodigo: int, qtdePaginasOutros: int):
        self.memTotal = self.calcula_pagina_kb(qtdePaginasTotal)
        self.memResidente = self.calcula_pagina_kb(qtdePaginasResidente)
        self.qtdePaginasTotal = qtdePaginasTotal
        self.qtdePaginasResidente = qtdePaginasResidente
        self.qtdePaginasCodigo = qtdePaginasCodigo
        self.qtdePaginasOutros = qtdePaginasOutros # Soma da quantidade de páginas usadas por data e por stack

    def retorna_string_dados(self):
        return f"ID: {self.pid} | Processo: {self.nome} | Usuário: {self.usuario} | Estado: {self.estado}"

class Threads:
    def __init__(self, pid: int, tid: int, nomeThread: str, estado:str):
        self.pid = pid
        self.tid = tid
        self.nomeThread = nomeThread
        self.estadoThread = estado

class NoArquivo:
    def __init__(self):
        self.nome = ""
        self.tipoNum = 0
        self.tipoNome = ""
        self.tamanho = ""
        self.permissoes = ""
        self.filhos = []

    def adicionaInformacoes(self, nome, tipoNum, tipoNome, tamanho, permissoes, filhos):
        self.nome = nome
        self.tipoNum = tipoNum
        self.tipoNome = tipoNome
        self.tamanho = tamanho
        self.permissoes = permissoes
        self.filhos = filhos