import threading
import backend
import frontend
import time
from queue import Queue

#Cria um canal (uma fila) bloqueante entre as threads para evitar problemas gerados por um eventual conflito (race condition) entre elas
#Se comunicam no sentido coleta > tratamento > interface

#Fila coleta-tratamento
fila_ct = Queue()
#Fila tratamento-interface
fila_ti = Queue()

def loop_de_coleta():
    while True:
        
        auxSistema = backend.pegaSistema()
        fila_ct.put(auxSistema)
        
        time.sleep(1)

def loop_de_tratamento():
    while True:
        
        auxSistema = fila_ct.get()
        backend.calculaPercentualMemoria(auxSistema)
        backend.calcular_uso_processador(auxSistema)
        fila_ti.put(auxSistema)

        time.sleep(1)

if __name__ == "__main__":
    sistema = backend.pegaSistema()

    threadColeta = threading.Thread(target=loop_de_coleta, daemon=True)
    threadTratamento = threading.Thread(target=loop_de_tratamento, daemon=True)

    threadColeta.start()
    threadTratamento.start()

    app = frontend.Dashboard(fila_ti)
    app.mainloop()
