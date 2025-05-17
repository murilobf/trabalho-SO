import threading
import backend
import frontend
import time

lock = threading.Lock()
barreira = threading.Barrier(3)

def loop_de_coleta(sistema: backend.Sistema):
    while True:
        auxSistema = backend.pegaSistema()
        with lock:
            sistema.atualizaDados(auxSistema)
            sistema.cont += 1  # Para debug
        try:
            barreira.wait()
        except threading.BrokenBarrierError:
            pass

        backend.calcular_uso_processador(sistema)
        print(sistema.percentualProcessadorOcupado)
        time.sleep(1)

def loop_de_tratamento(sistema: backend.Sistema):
    while True:
        with lock:
            backend.calculaPercentualMemoria(sistema)
            backend.calcular_uso_processador(sistema)
        try:
            barreira.wait()
        except threading.BrokenBarrierError:
            pass

        time.sleep(1)

if __name__ == "__main__":
    sistema = backend.pegaSistema()

    threadColeta = threading.Thread(target=loop_de_coleta, args=(sistema,), daemon=True)
    threadTratamento = threading.Thread(target=loop_de_tratamento, args=(sistema,), daemon=True)

    threadColeta.start()
    threadTratamento.start()

    app = frontend.Dashboard(sistema, barreira)
    app.mainloop()
