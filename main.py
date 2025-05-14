import threading
import backend
import frontend
import time

#Loop principal do código
thread = threading.Thread(target=loop_de_coleta, daemon=True)
thread.start()
sistema = backend.pegaGlobal()

def loop_de_coleta():
    while True:
        sistema = backend.pegaGlobal

        # Aguarda 5 segundos antes de atualizar novamente
        time.sleep(5)

if __name__ == "__main__":
    app = frontend.Dashboard(sistema)
    app.mainloop()