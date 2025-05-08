'''https://stackoverflow.com/questions/39066998/what-are-the-meaning-of-values-at-proc-pid-stat'''

import os
import classes 

def pegaProcessos(self) -> list[classes.Processo]:
    processos = []
    threads = []
    valores_necessarios = [0,1,2,3,10,15,22,51] #define quais dados dos processos queremos acessar -> total: 52
    dados = []
    for pid in os.scandir("/proc/"):
        if pid.name.isdigit(): #Verifica se os nomes dos processos são números
            pasta = open(f"/proc/{pid.name}/stat")
            processos = pasta.read().split(" ") #separa os dados da string do processo para uma lista
            dados = [processos[i] for i in valores_necessarios] #Pega os dados do processo de posições especificamente selecionadas
            
            usuario = os.stat(f"/proc/{pid.name}").st_uid #Coleta o ID do usuário referente ao processo
            
            pasta_threads = os.scandir(f"/proc/{pid.name}/task") #Coleta informações das threads do processo

            threads = [thread.name for thread in pasta_threads if thread.name.isdigit()]

            print(f"Usuario {usuario}")
            print(f"Processos: {dados}")
            print(f"Threads: {threads}\n")
            print(f"Infos Threads: {threads}\n") #Área para coletar as infos de cada thread


pegaProcessos(None)