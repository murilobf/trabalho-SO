import threading
import backend
import frontend
import time
from queue import Queue

#Cria um canal (uma fila) bloqueante entre as threads para evitar problemas gerados por um eventual conflito (race condition) entre elas. 
#Se comunicam no sentido coleta > tratamento > interface
    
#Fila coleta-tratamento
filaCT = Queue(1)
#Fila tratamento-interface
filaTI = Queue(1)
#Fila arvore-interface
filaAI = Queue(1)

#Funções que serão chamadas nas threads

#Responsável pela coleta de dados
def loop_de_coleta():
    while True:

        auxSistema = backend.pega_sistema()
        filaCT.put(auxSistema)
        
        time.sleep(1)

def loop_arvore_diretorio():
    while True:

        auxArvore = backend.pega_arvore_diretorios()
        filaAI.put(auxArvore)


#Responsável pelo "tratamento" dos dados (cálculos e quaisquer outras possíveis necessidades futuras)
def loop_de_tratamento():   
    while True:
        
        auxSistema = filaCT.get()
        backend.calcula_uso_memoria(auxSistema)
        backend.calcula_uso_processador(auxSistema)
        backend.calcula_processador_ocioso(auxSistema)
        filaTI.put(auxSistema)

#=========================#
#PARTE PRINCIPAL DO CÓDIGO#
#=========================#
threadColeta = threading.Thread(target=loop_de_coleta, daemon=True)
threadTratamento = threading.Thread(target=loop_de_tratamento, daemon=True)

threadColeta.start()
threadTratamento.start()

#Interface
app = frontend.Dashboard(filaTI)
app.mainloop()