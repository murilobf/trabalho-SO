'''https://stackoverflow.com/questions/39066998/what-are-the-meaning-of-values-at-proc-pid-stat'''

import os
import classes 

def pegaProcessos(self) -> list[classes.Processo]:
    
    for pid in os.scandir("/proc/"):
        if(pid.name.isdigit()): #Coleta ids que números
            pasta = open("/proc/{pid}/stat") #Abre o diretório stat de cada processo
            #pid = pasta.name
            #print(type(pasta.read()))
            print(type(pasta))
pegaProcessos(None)