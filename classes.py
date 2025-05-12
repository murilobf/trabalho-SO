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

#Classe que armaeznea os dados de um processo
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

    def adicionaDadosBasicos(self, pid: int, nome: str, usuario: str):
        self.pid = pid
        self.nome = nome
        self.usuario = usuario

    def adicionaDadosMemoria(self, mem_alocada: int, qtde_paginas_total: int, qtde_paginas_codigo: int, qtde_paginas_outros: int):
        self.mem_alocada = mem_alocada
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

class Threads:
    def __init__(self, pid: int,tid: int, qnt_threads: int, nome_threads: str):
        self.pid = pid
        self.tid = tid
        self.qnt_threads = qnt_threads
        self.nome_threads = nome_threads

    


'''PARTE DO MURILO:
Monitorar e apresentar as informações do uso de memória dos processos; 
Este objetivo consiste em fornecer as informações de uso de memória global do 
sistema e de cada processo individualmente. Os requisitos abaixo devem ser obrigatoriamente 
seguidos: 
1. Mostrar dados globais do uso de memória do sistema, p.ex. percentual de uso da memória, 
percentual de memória livre, quantidade de memória física (RAM) e virtual, etc. 
2. Mostrar informações detalhadas sobre o uso de memória para cada processo, p.ex. quantidade 
total de memória alocada, quantidade de páginas de memória (total, de código, heap, stack), 
etc. 
3. Ao mostrar informações detalhadas de cada processo, as informações podem ser apresentadas 
em uma nova tela (ou aba) que, ao ser fechada, retorna a tela principal.

PARTE DO HENRIQUE:
Monitorar e apresentar as características e propriedades de todos os processes existentes 
em execução no sistema operacional; 
Este objetivo consiste em implementar o primeiro conjunto de funcionalidades do 
Dashboard visando apresentar as informações sobre os processos que existem e estão executando 
no sistema operacional. Os requisitos abaixo devem ser seguidos: 
1. Mostrar dados globais do uso do processador, p.ex. percentual de uso do processador, 
percentual de tempo ocioso, quantidade total de processos e threads, etc. 
2. Mostrar a lista de processos existentes juntamente com os respectivos usuários; 
3. Mostrar informações sobre os threads de cada processo; 
4. Mostrar informações detalhadas de cada processo. Nesse caso, as informações podem ser 
apresentadas em uma nova tela (ou aba) que, ao ser fechada, retorna a tela principal.''' 



    

   