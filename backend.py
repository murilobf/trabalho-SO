import time
from classes import Processo, Sistema, Threads
import ctypes
import ctypes.util

# Uma interface pra permitir usar as funções da biblioteca c (o CDLL, junto do ctypes.util.find_library("c") pega a biblioteca de c para isso)
libc = ctypes.CDLL(ctypes.util.find_library("c"))

#Classe usada pra guardar informações sobre arquivos  (usamos diretamente apenas o d_name, mas se tirar o resto para de funcionarkkkk)
class Dirent(ctypes.Structure):
    _fields_ = [
        ("d_ino", ctypes.c_ulong),
        ("d_off", ctypes.c_long),
        ("d_reclen", ctypes.c_ushort),
        ("d_type", ctypes.c_ubyte), 
        ("d_name", ctypes.c_char * 256)
    ]

#Classe usada para guardar
class Stat(ctypes.Structure):
    _fields_ = [
        ("st_dev", ctypes.c_ulong),
        ("st_ino", ctypes.c_ulong),
        ("st_nlink", ctypes.c_ulong),
        ("st_mode", ctypes.c_uint),
        ("st_uid", ctypes.c_uint),
        ("st_gid", ctypes.c_uint),
        ("__pad", ctypes.c_byte * 256)  # para evitar ler além dos limites, se tirar dá segmentation fault
    ]

#========================#
#SEÇÃO DE COLETA DE DADOS#
#========================#

# Define os tipos de entrada e saída esperados pelas funções que usamos do ctype

# Pega uma string (ponteiro de char) e retorna o objeto de tipo DIR (definido no ctype) presente dela (por isso é um ponteiro pra void)
libc.opendir.argtypes = [ctypes.c_char_p]
libc.opendir.restype = ctypes.c_void_p

# Pega um ponteiro pra void (o DIR) e retorna um ponteiro pra estrutura Dirent (definida acima)
libc.readdir.argtypes = [ctypes.c_void_p]
libc.readdir.restype = ctypes.POINTER(Dirent)

# Pega um ponteiro pra void (o DIR) e retorna um inteiro
libc.closedir.argtypes = [ctypes.c_void_p]
libc.closedir.restype = ctypes.c_int

# Pega uma string e retorna um ponteiro pro
libc.stat.argtypes = [ctypes.c_char_p, ctypes.POINTER(Stat)]
libc.stat.restype = ctypes.c_int

#Função usada para pegar os nomes (ids) de pastas dentro
def pega_ids(caminho: str):

    #O opendir não aceita uma variável do tipo str, tem que converter usando a função abaixo para que seja um char*
    caminhoBytes = caminho.encode('utf-8')
    # Ponteiro pro diretório específicado (no nosso caso, /proc ou /proc/pid/task, dependendo da função que a chame)
    pdir = libc.opendir(caminhoBytes)

    # Lista de retorno
    ids = []

    try:
        # Acessa os diretórios enquanto existir um próximo
        while True:
            # Pega um ponteiro para o próximo diretório
            diretorio = libc.readdir(pdir)
            
            # Se o atual não for um diretório ele não existe. Quebra o loop
            if not diretorio:
                break

            # Pega o nome da pasta, usaremos isso para verificar se o arquivo é ou nãp um processo
            nome = diretorio.contents.d_name.decode("utf-8")

            # O arquivo é um processo quando seu nome possui um dígito
            if nome.isdigit():
                ids.append(nome)

    #Apenas para fim de debug/evitar do código quebrar mesmo quando se encontra algum problema
    except Exception as e:
        print(f"Erro ao abrir o proc: {e}")
    # Ao final, fecha o diretório
    finally:
        libc.closedir(pdir)

    return ids

# Pega os dados globais do sistema
def pega_sistema() -> Sistema:

    sistemaRetorno = Sistema()

    dadosProcessador = coleta_dados_processador()
    sistemaRetorno.adiciona_dados_processador(dadosProcessador)

    dadosMem = coleta_dados_memoria_sistema()
    sistemaRetorno.adiciona_dados_memoria(dadosMem[1], dadosMem[4], dadosMem[100]) #Memória física total, Memória física livre e total de memória usada para endereçamento virtual

    processos = pega_processos(sistemaRetorno)
    sistemaRetorno.adiciona_processos(processos)

    return sistemaRetorno

#Lê meminfo para pegar todos os dados sobre memória do sistema, quais dados são lidos fica a cargo das funções que a chama
def coleta_dados_memoria_sistema():
    with open("/proc/meminfo") as pastaMem:
        dadosMem = pastaMem.read().strip().split() 
        #OBS: Não é o melhor método já que isso gera um vetor de >100 posições mas funciona e permite que outros dados sejam extraidos mais facilmente se necessário

    return dadosMem

# Coleta dados do processador
def coleta_dados_processador():
    with open("/proc/stat") as pastaProc:
        dadosProcessador = pastaProc.read().strip().split()
    return dadosProcessador

# A seção abaixo coleta todos os processos do sistema e suas informações

# Coleta alguns dados variados do sistema, no momento usado principalmente para pegar o nome do processo (o indice [1])
# Pegamos algumas outras informações para, se necessário
def coleta_infos_processo(pid) -> list:
    valores_necessarios = [0,1,2,3,10,13,14,15,22,51] #define quais dados dos processos queremos acessar -> total: 52
    dadosProcessos = []

    with open(f"/proc/{pid}/stat") as pasta:
        processos = pasta.read().split(" ") #separa os dados da string do processo para uma lista
        dadosProcessos = [processos[i] for i in valores_necessarios] #Pega os dados do processo de posições especificamente selecionadas
        
    return dadosProcessos

# Pega o id do usuário que chamou o processo
def coleta_usuario_processo(pid: int) -> int:
    caminho = f"/proc/{pid}".encode('utf-8')
    stat = Stat()

    if libc.stat(caminho, ctypes.byref(stat)) == 0:
        return stat.st_uid
    else:
        print("Erro ao coletar o usuário do processo")

# Pega dados da memória
def coleta_dados_memoria(pid: int):
    # Memoria. Nota: os dados vem todos numa única linha, é preciso separar. Nota 2: o tamanho é em páginas
    with open(f"/proc/{pid}/statm") as pastaMem: #Isso abre (e o with faz com que feche sozinha também) o arquivo 
        dadosMem = pastaMem.read().strip().split() #Lê, remove o \n no final da string e separa cada número em um elemento diferente 
    
    return dadosMem

# Pega dados das threads de um processo
def coleta_dados_threads(pid: int) -> list[Threads]: #vai receber o processo específico e retorna uma lista com os dados das threads dele
    dadosThreads = []
    tids = pega_ids(f"/proc/{pid}/task")

    for tid in tids:  #itera sobre os ids das threads pego pela função pega_ids
        with open(f"/proc/{pid}/task/{tid}/comm") as t: #abre a theread como um objeto
            nomeThread = t.read().strip() # lê e tira os espaço que podem ter na palavra. Pega o nome da thread
        dadosThreads.append(Threads(pid, tid, nomeThread)) #faz a lista de dados da thread 

    return dadosThreads

#Pega os processos do sistema e seus dados
def pega_processos(sistema:Sistema) -> list[Processo]:
    processosRetorno = []

    pids = pega_ids("/proc")

    for pid in pids:
        #Processos
        #Processo inicialmente vazio, será preenchido ao final da condicional
        processo = Processo()

        #Try catch pra alguns casos de processos que nascem e morrem muito rapidamente e geram erros ao tentar acessá-los
        try:
            #Coleta todos os dados do processo
            dadosProcesso = coleta_infos_processo(pid)
            
            #https://stackoverflow.com/questions/5327707/how-could-i-get-the-user-name-from-a-process-id-in-python-on-linux diz como pegar nome do usuario pelo uid
            usuario = coleta_usuario_processo(pid)

            processo.adiciona_dados_basicos(pid, dadosProcesso[1], usuario) #Adiciona id, nome do processo e o id do usuário
            
            #Threads
            threads = (coleta_dados_threads(pid))
            #Adiciona quantidade de threads total no prcessador
            sistema.adiciona_quantidade_threads(len(threads))
            processo.adiciona_threads(threads)

            # Coleta e guarda a memória do processo
            dadosMem = coleta_dados_memoria(pid)
            processo.adiciona_dados_memoria(dadosMem[0],dadosMem[3],dadosMem[5]) #memTotal em kb, memTotal em páginas, memtotal em pg usadas pelo código (text) e memtotal em pg usadas por outras coisas

            # Adiciona o processo na lista de processos
            processosRetorno.append(processo)
            #Adiciona quantidade de processos total no sistema
            sistema.adiciona_quantidade_processos(len(processosRetorno))


        except FileNotFoundError:
            continue

    return processosRetorno

#============================#
#SEÇÃO DE TRATAMENTO DOS DADOS
#============================#

# Calcula o porcentual de memória usado pelo sistema no momento
def calcula_uso_memoria(sistema: Sistema):
    memTotal = float(sistema.memFisicaKB)
    memLivre = float(sistema.memLivreKB)

    percentualMemLivre = round(100*memLivre/memTotal, 2)
    percentualMemOcupada = 100 - percentualMemLivre

    sistema.adiciona_porcentagens_memoria(percentualMemLivre, percentualMemOcupada)

# Calcula uso da cpu pelo sistema em um intervalo de tempo (em %)
def calcula_uso_processador(sistema: Sistema):

    # Soma todos os tempo em que o processador não está ocioso (em modo usuario, usuario de baixa prioridade e kernel)
    somaPrimeiraAmostragem = float(sistema.dadosProcessador[1]) + float(sistema.dadosProcessador[2]) + float(sistema.dadosProcessador[3])
    # Pega o tempo total de uso do processador (a soma anterior junto do tempo em que ele está em modo ocioso)
    totalPrimeiraAmostragem = somaPrimeiraAmostragem + float(sistema.dadosProcessador[4])

    time.sleep(0.5)  # Espera curta para medir diferença

    auxDadosProcessador = coleta_dados_processador()
    # Faz o mesmo só que com novos dados 
    somaSegundaAmostragem = float(auxDadosProcessador[1]) + float(auxDadosProcessador[2]) + float(auxDadosProcessador[3])
    totalSegundaAmostragem = somaSegundaAmostragem + float(auxDadosProcessador[4])
    
    # Pega a diferença entre as duas medições. Isso é necessário pois /proc/stat guarda os tempos desde a inicialização do sistema.
    diferencaSoma = somaSegundaAmostragem - somaPrimeiraAmostragem
    diferencaTotal = totalSegundaAmostragem - totalPrimeiraAmostragem

    # Transforma em porcentagens
    percentualProcessadorOcupado = round(100 * (diferencaSoma / diferencaTotal), 2)
    percentualProcessadorLivre = 100 - percentualProcessadorOcupado

    sistema.adiciona_porcentagens_processador(percentualProcessadorLivre, percentualProcessadorOcupado) 

# Calculo a porcentagem de tempo que o processdor ficou ocioso

def calcula_processador_ocioso(sistema: Sistema):

    # Pega o tempo total de uso do processador e o divide por todos os dados de uso do processador (em modo usuario, usuario de baixa prioridade, kernel e ocioso)
    somaTotal = (float(sistema.dadosProcessador[1]) + float(sistema.dadosProcessador[2]) + float(sistema.dadosProcessador[3])+ float(sistema.dadosProcessador[4]))
    percentualOcioso = round(100*float(sistema.dadosProcessador[4])/somaTotal,2)

    sistema.adiciona_porcentagem_ocioso(percentualOcioso)
