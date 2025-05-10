'''https://stackoverflow.com/questions/39066998/what-are-the-meaning-of-values-at-proc-pid-stat'''

import os
from classes import Processo, Sistema

#variavel usada pra transformar dados de memória de número de páginas para quantidade em KB
tamPaginaKb = 4

#Coleção dos dados
def pegaProcessos() -> list[Processo]:
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

            pasta = open(f"/proc/{pid.name}/stat")
            processos = pasta.read().split(" ") #separa os dados da string do processo para uma lista
            dados_processos = [processos[i] for i in valores_necessarios] #Pega os dados do processo de posições especificamente selecionadas
            
            usuario = os.stat(f"/proc/{pid.name}").st_uid #Coleta o ID do usuário referente ao processo

            processo.adicionaDadosBasicos(pid.name, dados_processos[1],usuario)

            #Threads
            for thread in os.scandir(f"/proc/{pid.name}/task"):  #entra na pasta de threads do processo atual
                if thread.name.isdigit(): #nome da thread é número?
                    tid = thread.name  # pega os nomes das threads e salva
                    threads.append(tid)
                    with open(f"/proc/{pid.name}/task/{tid}/comm") as tf: #abre a theread como um objeto
                        nome_thread = tf.read().strip() # lê e tira os espaço que podem ter na palavra
                        dados_threads.append((tid, nome_thread)) #faz a lista de dados da thread -> Aqui que tá dando o "problema" de printar a lista toda

            # Memoria. Nota: os dados vem todos numa única linha, é preciso separar. Nota 2: o tamanho é em páginas
            # Os dados vem na ordem: tamanho total - 
            with open(f"/proc/{pid.name}/statm") as pastaMem: #Isso abre (e o with faz com que feche sozinha também) o arquivo 
                dadosMem = pastaMem.read().strip().split() #Lê, remove o \n no final da string e separa cada número em um elemento diferente 

            # Exibe dados coletados
            '''print(f"Usuário UID: {usuario}")
            print(f"Processo: {dados_processos}")
            print(f"Threads (TIDs): {threads}")
            print(f"Infos das Threads: {dados_threads}")
            print(f"Dados memória: {dadosMem}\n")'''

            processo.printDadosBasicos()
            # Adiciona o processo na lista de processos
            processos.append(processo)

    # Memória global
    '''with open("/proc/meminfo") as dadosMem:
        for linhaDadosMem in dadosMem:
            print(linhaDadosMem)'''

    return processos


# Cria a lista de processos
processos = pegaProcessos()
