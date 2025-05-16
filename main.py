import threading
import backend
import frontend
import time

lock = threading.Lock()

def loop_de_coleta(sistema: backend.Sistema):
    while True:
        #Auxiliar usada pra atualizar os dados.
        #OBS: não dá pra usar pegaSistema() diretamente no sistema original por causa da thread, já que ela recebe como parâmetro uma referência do sistema original
        auxSistema = backend.pegaSistema()

        #Trava pra evitar race conditions
        with lock:
            #Atualiza os dados com base no sistema auxiliar criado acima. 
            sistema.atualizaDados(auxSistema)

        # Aguarda 1 segundo antes de atualizar novamente
        time.sleep(1)

def loop_de_tratamento(sistema: backend.Sistema):
    while True:

        #Trava para evitar race conditions
        with lock:
            backend.calculaPercentualMemoria(sistema)
            backend.calcular_uso_processador(sistema)
            
        print(sistema.percentualMemLivre)

        time.sleep(1)

#Coleta inicial do sistema para que seja possível usá-lo nas diferentes threads
sistema = backend.pegaSistema()
# Thread de coleta de dados
threadColeta = threading.Thread(target=loop_de_coleta, args=(sistema,), daemon=True)
threadColeta.start()

threadTratamento = threading.Thread(target=loop_de_tratamento, args=(sistema,), daemon=True)
threadTratamento.start()




# Thread de interface
if __name__ == "__main__":
    app = frontend.Dashboard(sistema)
    app.mainloop()