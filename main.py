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
particoes = backend.pega_particoes()
#Funções que serão chamadas nas threads

#Responsável pela coleta de dados
def loop_de_coleta():
    while True:

        auxSistema = backend.pega_sistema()
        auxSistema.particoes = particoes
        filaCT.put(auxSistema)
        
        time.sleep(1)

def loop_arvore_diretorio():
    while True:
        #Aqui será feita uma abordagem diferente dos outros loops, como demora muito pra coletar a árvore, vamos pegar o tempo que falta pra coleta dar 1 ciclo (60s no nosso caso).
        t1 = time.time()
        auxRaiz = backend.pega_arvore_diretorios("/")
        filaAI.put(auxRaiz)
        t2 = time.time()
        tempoFaltante = 60 - (t2 - t1)

        #Se esse tempo for maior que 0, espera o tempo necessário para dar 60s, caso contrário, estamos atrasados, chama a função de novo imediatamente
        if(tempoFaltante > 0):
            time.sleep(tempoFaltante)


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
threadArvore = threading.Thread(target=loop_arvore_diretorio, daemon=True)

threadColeta.start()
threadTratamento.start()
threadArvore.start()

#Interface
app = frontend.Dashboard(filaTI, filaAI)
app.mainloop()