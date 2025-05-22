import threading
import backend
import frontend
import time
from queue import Queue

#Cria um canal (uma fila) bloqueante entre as threads para evitar problemas gerados por um eventual conflito (race condition) entre elas
#Se comunicam no sentido coleta > tratamento > interface

#Fila coleta-tratamento
filaCT = Queue()
#Fila tratamento-interface
filaTI = Queue()

def loop_de_coleta():
    while True:

        auxSistema = backend.pega_sistema()
        filaCT.put(auxSistema)
        
        time.sleep(1)

def loop_de_tratamento():
    while True:
        
        auxSistema = filaCT.get()
        backend.calcula_uso_memoria(auxSistema)
        backend.calcula_uso_processador(auxSistema)
        filaTI.put(auxSistema)

        time.sleep(1)

#=========================#
#PARTE PRINCIPAL DO CÓDIGO#
#=========================#
threadColeta = threading.Thread(target=loop_de_coleta, daemon=True)
threadTratamento = threading.Thread(target=loop_de_tratamento, daemon=True)

threadColeta.start()
threadTratamento.start()

app = frontend.Dashboard(filaTI)
app.mainloop()