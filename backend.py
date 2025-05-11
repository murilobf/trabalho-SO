'''https://stackoverflow.com/questions/39066998/what-are-the-meaning-of-values-at-proc-pid-stat'''

import os
from classes import Processo, Sistema

#variavel usada pra transformar dados de memória de número de páginas para quantidade em KB
tamPaginaKb = 4

#========================#
#SEÇÃO DE COLEÇÃO DE DADOS
#========================#

def pegaProcessos() -> list[Processo]:
    processosRetorno = []
    processos = []
    valores_necessarios = [0,1,2,3,10,15,22,51] #define quais dados dos processos queremos acessar -> total: 52
    dados_processos = []
    
    dados_threads = []
    threads = []

    for pid in os.scandir("/proc/"):
        dados_threads = []
        dadosMem = []
        threads = [] 

        #Processos
        if pid.name.isdigit(): #Verifica se os nomes dos processos são números
            #Processo inicialmente vazio, será preenchido ao final da condicional
            processo = Processo()

            with open(f"/proc/{pid.name}/stat") as pasta:
                processos = pasta.read().split(" ") #separa os dados da string do processo para uma lista
                dados_processos = [processos[i] for i in valores_necessarios] #Pega os dados do processo de posições especificamente selecionadas
                
                usuario = os.stat(f"/proc/{pid.name}").st_uid #Coleta o ID do usuário referente ao processo
                #https://stackoverflow.com/questions/5327707/how-could-i-get-the-user-name-from-a-process-id-in-python-on-linux diz como pegar nome do usuario pelo uid

            processo.adicionaDadosBasicos(pid.name, dados_processos[1],usuario) #Adiciona id, nome do processo e o id do usuário

            #Threads
            for thread in os.scandir(f"/proc/{pid.name}/task"):  #entra na pasta de threads do processo atual
                if thread.name.isdigit(): #nome da thread é número?
                    tid = thread.name  # pega os nomes das threads e salva
                    threads.append(tid)
                    with open(f"/proc/{pid.name}/task/{tid}/comm") as tf: #abre a theread como um objeto
                        nome_thread = tf.read().strip() # lê e tira os espaço que podem ter na palavra
                        dados_threads.append((tid, nome_thread)) #faz a lista de dados da thread -> Aqui que tá dando o "problema" de printar a lista toda

            # Memoria. Nota: os dados vem todos numa única linha, é preciso separar. Nota 2: o tamanho é em páginas
            with open(f"/proc/{pid.name}/statm") as pastaMem: #Isso abre (e o with faz com que feche sozinha também) o arquivo 
                dadosMem = pastaMem.read().strip().split() #Lê, remove o \n no final da string e separa cada número em um elemento diferente 

            auxMemTotalKb = (int(dadosMem[0]))*tamPaginaKb # Multiplicação para tornar o dado de quantidade de páginas usadas no total para tamanho em KB
            processo.adicionaDadosMemoria(auxMemTotalKb,dadosMem[0],dadosMem[3],dadosMem[5]) #memTotal em kb, memTotal em páginas, memtotal em pg usadas pelo código (text) e memtotal em pg usadas por outras coisas

            # Exibe dados coletados
            '''print(f"Usuário UID: {usuario}")
            print(f"Processo: {dados_processos}")
            print(f"Threads (TIDs): {threads}")
            print(f"Infos das Threads: {dados_threads}")
            print(f"Dados memória: {dadosMem}\n")'''

            #processo.printDados()
            # Adiciona o processo na lista de processos
            processosRetorno.append(processo)

    return processosRetorno

# Pega os dados globais do sistema
def pegaGlobal() -> Sistema:

    sistemaRetorno = Sistema()
    dadosMem = []

    dadosSistema = Sistema( )
    with open("/proc/meminfo") as pastaMem:
        dadosMem = pastaMem.read().strip().split() #Não é o melhor método já que isso gera um vetor de >100 posições mas funciona

    sistemaRetorno.adicionaDadosMemoria(dadosMem[1], dadosMem[4], dadosMem[97]) #Memória física total, Memória física livre e total de memória virtual

    return sistemaRetorno

#============================#
#SEÇÃO DE TRATAMENTO DOS DADOS
#============================#

#Ca
def calculaPercentualMemoria(sistema: Sistema):
    memTotal = float(sistema.memFisica)
    memLivre = float(sistema.memLivre)

    percentualMemLivre = round(100*memLivre/memTotal, 2)
    percentualMemOcupada = round(100*(memTotal-memLivre)/memTotal, 2)

    sistema.adicionaPorcentagensMemoria(percentualMemLivre, percentualMemOcupada)
    
           

# Cria a lista de processos
processos = pegaProcessos()

sistema = pegaGlobal()

calculaPercentualMemoria(sistema)

print(sistema.percentualMemLivre)
print(sistema.percentualMemOcupada)
