import threading
import backend
import frontend
import classes
import time

def loop_de_coleta(sistema: backend.Sistema):
    while True:
        #Auxiliar usada pra atualizar os dados.
        #OBS: não dá pra usar pegaSistema() diretamente no sistema original por causa da thread, já que ela recebe como parâmetro uma referência do sistema original
        auxSistema = classes.Processo()
        auxSistema = backend.pegaSistema()

        #Atualiza os dados com base no sistema auxiliar criado acima. 
        sistema.atualizaDados(auxSistema)

        backend.calculaPercentualMemoria(sistema)

        # Aguarda 1 segundo antes de atualizar novamente
        time.sleep(1)

#Coleta inicial do sistema para que seja possível usá-lo nas diferentes threads
sistema = backend.pegaSistema()
# Thread de coleta de dados
thread = threading.Thread(target=loop_de_coleta, args=(sistema,), daemon=True)
thread.start()

# Thread de interface
if __name__ == "__main__":
    app = frontend.Dashboard(sistema)
    app.mainloop()