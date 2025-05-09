'''https://stackoverflow.com/questions/39066998/what-are-the-meaning-of-values-at-proc-pid-stat'''

import os
import classes

def pegaProcessos(self) -> list[classes.Processo]:
    processos = []
    valores_necessarios = [0,1,2,3,10,15,22,51] #define quais dados dos processos queremos acessar -> total: 52
    dados_processos = []
    
    dados_threads = []
    threads = []

    for pid in os.scandir("/proc/"):
        #Processos
        if pid.name.isdigit(): #Verifica se os nomes dos processos são números
            pasta = open(f"/proc/{pid.name}/stat")
            processos = pasta.read().split(" ") #separa os dados da string do processo para uma lista
            dados_processos = [processos[i] for i in valores_necessarios] #Pega os dados do processo de posições especificamente selecionadas
            
            usuario = os.stat(f"/proc/{pid.name}").st_uid #Coleta o ID do usuário referente ao processo

            #Threads

            for thread in os.scandir(f"/proc/{pid.name}/task"):  #entra na pasta de threads do processo atual
                if thread.name.isdigit(): #nome da thread é número?
                    tid = thread.name  # pega os nomes das threads e salva
                    threads.append(tid)
                    with open(f"/proc/{pid.name}/task/{tid}/comm") as tf: #abre a theread como um objeto
                        nome_thread = tf.read().strip() # lê e tira os espaço que podem ter na palavra
                        dados_threads.append((tid, nome_thread)) #faz a lista de dados da thread -> Aqui que tá dando o "problema" de printar a lista toda

            # Exibe dados coletados
            print(f"Usuário UID: {usuario}")
            print(f"Processo: {dados_processos}")
            print(f"Threads (TIDs): {threads}")
            print(f"Infos das Threads: {dados_threads}\n")



pegaProcessos(None)