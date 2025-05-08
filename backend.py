'''https://stackoverflow.com/questions/39066998/what-are-the-meaning-of-values-at-proc-pid-stat'''

import os
import classes 

def pegaProcessos(self) -> list[classes.Processo]:
    processos = []
    valores_necessarios = [0,1,2,3,10,15,22,51] #define quais dados dos processos queremos acessar -> total: 52
    dados = []
    for pid in os.scandir("/proc/"):
        if pid.name.isdigit(): #Verifica se os nomes dos processos são números
            pasta = open(f"/proc/{pid.name}/stat")
            processos = pasta.read().split(" ")
            dados = [processos[i] for i in valores_necessarios]
            print(dados)

pegaProcessos(None)