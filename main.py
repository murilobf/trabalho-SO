import threading
import backend
import frontend
import time

def loop_de_coleta(sistema: backend.Sistema):
    while True:
        sistema = backend.pegaGlobal()
        backend.calculaPercentualMemoria(sistema)

        # Aguarda 5 segundos antes de atualizar novamente
        time.sleep(5)

#Coleta inicial do sistema para que seja possível usá-lo nas diferentes threads
sistema = backend.pegaGlobal()
# Thread de coleta de dados
thread = threading.Thread(target=loop_de_coleta, args=(sistema,), daemon=True)
thread.start()

# Thread de interface
if __name__ == "__main__":
    app = frontend.Dashboard(sistema)
    app.mainloop()