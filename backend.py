'''https://stackoverflow.com/questions/39066998/what-are-the-meaning-of-values-at-proc-pid-stat'''

import os
import time
from classes import Processo, Sistema, Threads

#========================#
#SEÇÃO DE COLEÇÃO DE DADOS
#========================#

# TODO: da forma como isso está estruturado um novo objeto é criado sempre que a função é chamada, o que não permite a atualização correta dos dados nas
# threads da main. Precisamos mudar isso
# Pega os dados globais do sistema
def pega_sistema() -> Sistema:

    sistemaRetorno = Sistema()

    dadosProcessador = coleta_dados_processador()
    sistemaRetorno.adiciona_dados_processador(dadosProcessador)

    dadosMem = coleta_dados_memoria_sistema()
    sistemaRetorno.adiciona_dados_memoria(dadosMem[1], dadosMem[4], dadosMem[97]) #Memória física total, Memória física livre e total de memória virtual

    processos = pega_processos()
    sistemaRetorno.adiciona_processos(processos)

    return sistemaRetorno

#Lê meminfo para pegar todos os dados sobre memória do sistema, quais dados são lidos fica a cargo das funções que a chama
def coleta_dados_memoria_sistema():
    with open("/proc/meminfo") as pastaMem:
        dadosMem = pastaMem.read().strip().split() 
        #OBS: Não é o melhor método já que isso gera um vetor de >100 posições mas funciona e permite que outros dados sejam extraidos mais facilmente

    return dadosMem

#Pega os processos do sistema e seus dados  
def coleta_dados_processador():
    with open("/proc/stat") as pastaProc:
        dadosProcessador = pastaProc.read().strip().split()
    return dadosProcessador

def coleta_infos_processo(pid) -> list:
    valores_necessarios = [0,1,2,3,10,13,14,15,22,51] #define quais dados dos processos queremos acessar -> total: 52
    dadosProcessos = []

    with open(f"/proc/{pid}/stat") as pasta:
        processos = pasta.read().split(" ") #separa os dados da string do processo para uma lista
        dadosProcessos = [processos[i] for i in valores_necessarios] #Pega os dados do processo de posições especificamente selecionadas
        
    return dadosProcessos

#Pega os processos do sistema e seus dados
def pega_processos() -> list[Processo]:
    processosRetorno = []

    for pid in os.scandir("/proc/"):
        
        #Processos
        if pid.name.isdigit(): #Verifica se os nomes dos processos são números
            #Processo inicialmente vazio, será preenchido ao final da condicional
            processo = Processo()

            #Try catch pra alguns casos de processos que nascem e morrem muito rapidamente e geram erros ao tentar acessá-los
            try:
                #Coleta todos os dados do processo
                dadosProcesso = coleta_infos_processo(pid.name)
                
                #https://stackoverflow.com/questions/5327707/how-could-i-get-the-user-name-from-a-process-id-in-python-on-linux diz como pegar nome do usuario pelo uid
                usuario = os.stat(f"/proc/{pid.name}").st_uid #Coleta o ID do usuário referente ao processo

                processo.adiciona_dados_basicos(pid.name, dadosProcesso[1], usuario) #Adiciona id, nome do processo e o id do usuário
                
                #Threads
                threads = (coleta_dados_threads(pid.name))
                processo.adiciona_threads(threads)

                # Coleta e guarda a memória do processo
                dadosMem = coleta_dados_memoria(pid.name)
                processo.adiciona_dados_memoria(dadosMem[0],dadosMem[3],dadosMem[5]) #memTotal em kb, memTotal em páginas, memtotal em pg usadas pelo código (text) e memtotal em pg usadas por outras coisas

                # Adiciona o processo na lista de processos
                processosRetorno.append(processo)


            except FileNotFoundError:
                continue

    return processosRetorno

# 0.3 Calcular % do uso do processador #

#===> def coletar_dadosProcessos(self) ->list(classes.Processos):

def coleta_dados_memoria(pid: int):
    # Memoria. Nota: os dados vem todos numa única linha, é preciso separar. Nota 2: o tamanho é em páginas
    with open(f"/proc/{pid}/statm") as pastaMem: #Isso abre (e o with faz com que feche sozinha também) o arquivo 
        dadosMem = pastaMem.read().strip().split() #Lê, remove o \n no final da string e separa cada número em um elemento diferente 
    
    return dadosMem

def coleta_dados_threads(pid: int) -> list[Threads]: #vai receber o processo específico e retorna uma lista com os dados das threads dele
    dadosThreads = []
    caminho = f"/proc/{pid}/task"
    qntThreads = 0

    for thread in os.scandir(caminho):  #entra na pasta de threads do processo atual
        if thread.name.isdigit(): #nome da thread é número?
            tid = int(thread.name)  # pega os nomes das threads e salva
            with open(f"{caminho}/{tid}/comm") as t: #abre a theread como um objeto
                nomeThread = t.read().strip() # lê e tira os espaço que podem ter na palavra
                qntThreads += 1
            dadosThreads.append(Threads(pid, tid, qntThreads, nomeThread)) #faz a lista de dados da thread -> Aqui que tá dando o "problema" de printar a lista toda

    return dadosThreads

#============================#
#SEÇÃO DE TRATAMENTO DOS DADOS
#============================#

# Calcula o porcentual de memória usado pelo sistema no momento
def calcula_uso_memoria(sistema: Sistema):
    memTotal = float(sistema.memFisica)
    memLivre = float(sistema.memLivre)

    percentualMemLivre = round(100*memLivre/memTotal, 2)
    percentualMemOcupada = 100 - percentualMemLivre

    sistema.adiciona_porcentagens_memoria(percentualMemLivre, percentualMemOcupada)

# Calcula uso da cpu por um processo em um intervalo de tempo
def calcula_uso_processador(sistema: Sistema):
    somaPrimeiraAmostragem = float(sistema.dadosProcessador[1]) + float(sistema.dadosProcessador[2]) + float(sistema.dadosProcessador[3])
    totalPrimeiraAmostragem = somaPrimeiraAmostragem + float(sistema.dadosProcessador[4])

    time.sleep(0.5)  # Espera curta para medir diferença

    auxDadosProcessador = coleta_dados_processador()
    somaSegundaAmostragem = float(auxDadosProcessador[1]) + float(auxDadosProcessador[2]) + float(auxDadosProcessador[3])
    totalSegundaAmostragem = somaSegundaAmostragem + float(auxDadosProcessador[4])
    
    diferencaSoma = somaSegundaAmostragem - somaPrimeiraAmostragem
    diferencaTotal = totalSegundaAmostragem - totalPrimeiraAmostragem
        

    percentualProcessadorOcupado = round(100 * (diferencaSoma / diferencaTotal), 2)
    percentualProcessadorLivre = 100 - percentualProcessadorOcupado

    sistema.adiciona_porcentagens_processador(percentualProcessadorLivre, percentualProcessadorOcupado) 