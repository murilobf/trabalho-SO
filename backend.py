import os
import classes 

def pegaProcessos(self) -> list[classes.Processo]:
    
    for pasta in os.scandir("/proc"):
        pid = pasta.name
        print(pid)
    
pegaProcessos(None)