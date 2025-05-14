#variavel usada pra transformar dados de memória de número de páginas para quantidade em KB
tamPaginakB = 4

class Sistema:
    def __init__(self):
        #Dados de memória
        self.memLivre = 0
        self.memFisica = 0
        self.memVirtual = 0
        self.percentualMemLivre = 0
        self.percentualMemOcupada = 0
        #Vetor que guarda todos os processos atualmente no sistema
        self.processos = []

    def adicionaDadosMemoria(self, memFisica: int, memLivre: int, memVirtual: int):
        self.memFisica = memFisica
        self.memLivre = memLivre
        self.memVirtual = memVirtual

    def adicionaPorcentagensMemoria(self, percentualMemLivre: float, percentualMemOcupada: float):
        self.percentualMemLivre = percentualMemLivre
        self.percentualMemOcupada = percentualMemOcupada

    def adicionaProcessos(self, processos):
        self.processos = processos

    def retornaProcessos(self):
        return self.processos


#Classe que armazena os dados de um processo
class Processo:
    
    #Função inicializadora do processo
    def __init__(self):
        
        #Dados identificadores do processo (id, nome, usuário)
        self.pid = 0
        self.nome = ""
        self.usuario = ""
        #Dados relativos ao requisito 2 do trabalho (memória)
        self.mem_alocada = 0
        self.qtde_paginas_total = 0
        self.qtde_paginas_codigo = 0
        self.qtde_paginas_outros = 0
        self.threads = []

    def calculaPaginaPkB(self, dadoPag):
        auxMemTotalKb = (int(dadoPag)*tamPaginakB) # Multiplicação para tornar o dado de quantidade de páginas usadas no total para tamanho em KB

        return auxMemTotalKb

    def adicionaDadosBasicos(self, pid: int, nome: str, usuario: str):
        self.pid = pid
        self.nome = nome
        self.usuario = usuario
    
    def adicionaThreads(self, threads: list):
        self.threads = threads

    def adicionaDadosMemoria(self, qtde_paginas_total: int, qtde_paginas_codigo: int, qtde_paginas_outros: int):
        self.mem_alocada = self.calculaPaginaPkB(qtde_paginas_total)
        self.qtde_paginas_total = qtde_paginas_total
        self.qtde_paginas_codigo = qtde_paginas_codigo
        self.qtde_paginas_outros = qtde_paginas_outros # Soma da quantidade de páginas usadas por data e por stack
    
    def printDados(self):
        print("\nDADOS BÁSICOS:")
        print(f"Id: {self.pid}")
        print(f"Nome: {self.nome}")
        print(f"Usuario: {self.usuario}")
        print("DADOS DE MEMÓRIA:")
        print(f"Memória alocada: {self.mem_alocada}kB")
        print(f"Quantidade total de páginas usadas: {self.qtde_paginas_total}")
        print(f"Quantidade de páginas de código: {self.qtde_paginas_codigo}")
        print(f"Quantidade de páginas usadas por data, heap e stack: {self.qtde_paginas_outros}")

    def retornaStringDados(self):
        return "{self.pid} - {self.nome} - {self.usuario} - {self.mem_alocada}"

class Threads:
    def __init__(self, pid: int, tid: int, qnt_thread: int, nome_thread: str):
        self.pid = pid
        self.tid = tid
        self.qnt_thread = qnt_thread
        self.nome_thread = nome_thread

class BufferSistema:
    def __init__(self, sistema: Sistema):
        self.sistema = sistema