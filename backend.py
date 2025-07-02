import time
from classes import Processo, Sistema, Threads, NoArquivo, Particao
import ctypes
import ctypes.util
import os

# Uma interface pra permitir usar as funções da biblioteca c (o CDLL, junto do ctypes.util.find_library("c") pega a biblioteca de c para isso)
libc = ctypes.CDLL(ctypes.util.find_library("c"))

#Variáveis usadas para verificar a permissão do usuário que está rodando o programa em entrar nos diretórios 
uid = libc.getuid()  
gid = libc.getgid()

#Classe usada pra guardar informações sobre arquivos  (usamos diretamente apenas o d_name, mas se tirar o resto para de funcionarkkkk)
class Dirent(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("d_ino", ctypes.c_ulonglong),
        ("d_off", ctypes.c_longlong),
        ("d_reclen", ctypes.c_ushort),
        ("d_type", ctypes.c_ubyte), 
        ("d_name", ctypes.c_char * 256)
    ]

#Classe usada para guardar algumas informações a mais sobre o arquivo, principalmente usuário, permissões e tamanho
class Stat(ctypes.Structure): # https://man7.org/linux/man-pages/man3/stat.3type.html mais informações
    _fields_ = [
        ("st_dev", ctypes.c_ulong),
        ("st_ino", ctypes.c_ulong),
        ("st_nlink", ctypes.c_ulong),
        ("st_mode", ctypes.c_uint), # permissões
        ("st_uid", ctypes.c_uint),
        ("st_gid", ctypes.c_uint),
        ("st_rdev", ctypes.c_ulong),
        ("st_size", ctypes.c_long),  # tamanho do arquivo
        ("__pad0", ctypes.c_byte * 256),  # para evitar ler além dos limites, se tirar dá segmentation fault   
    ]

class StatVFS(ctypes.Structure):
    _fields_ = [
        ("f_bsize", ctypes.c_ulong),
        ("f_frsize", ctypes.c_ulong),
        ("f_blocks", ctypes.c_ulong),
        ("f_bfree", ctypes.c_ulong),
        ("f_bavail", ctypes.c_ulong),
        ("f_files", ctypes.c_ulong),
        ("f_ffree", ctypes.c_ulong),
        ("f_favail", ctypes.c_ulong),
        ("f_fsid", ctypes.c_ulong),
        ("f_flag", ctypes.c_ulong),
        ("f_namemax", ctypes.c_ulong),
    ]

# Os tipos de arquivo definidos por d_type na classe Dirent, é mais prático definir na mão do que extrair do dirent.h do linux
# Mas caso precise extrair o caminho está em /usr/include/dirent.h
TIPOS = {
    0: "Desconhecido",
    1: "Pipe nomeado",
    2: "Arquivo de caractére",
    4: "Diretório",
    6: "Arquivo de bloco",
    8: "Arquivo regular",
    10: "Link simbólico",
    12: "Socket",
    14: "Entrada whiteout"
}

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

libc.statvfs.argtypes = [ctypes.c_char_p, ctypes.POINTER(StatVFS)]
libc.statvfs.restype = ctypes.c_int

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

# Função para aplicar statvfs usando ctypes
def uso_particao(caminho):
    stat = StatVFS()

    if(libc.statvfs(ctypes.c_char_p(caminho.encode('utf-8')), ctypes.byref(stat)) == 0): 
        
        total = stat.f_frsize * stat.f_blocks
        livre = stat.f_frsize * stat.f_bfree
        usado = total - livre
        return total, usado, livre
    
    return None

# Lê /proc/partitions -> lista de partições disponíveis
def ler_particoes():
    # Dicionário que associa guarda o nome da partição e seu tamanho
    particoes = {}
    with open("/proc/partitions") as f:
        next(f)  # pula cabeçalho
        next(f)
        for linha in f:
            campos = linha.strip().split()
            if len(campos) == 4:
                blocos, nome = int(campos[2]), campos[3]
                particoes[nome] = blocos * 1024  
    return particoes

# Lê /proc/mounts e pega os pontos de montagem de cada partição, retornando-os
def ler_montagens():
    #Dicionário que associa um nome da partição a um ponto de montagem
    montagens = {}

    with open("/proc/mounts") as f:

        for linha in f:

            campos = linha.split()
            dispositivo, ponto = campos[0], campos[1]

            if dispositivo.startswith("/dev/"):

                nomeParticao = dispositivo.split("/")[-1]
                montagens[nomeParticao] = ponto
                
    return montagens

# Junta tudo
def pega_particoes():
    particoes = ler_particoes()
    montagens = ler_montagens()

    listaParticoes = []

    #tamanho não é usado mas precisa ser chamado porque temos dois tens dentro do dicionario de partições
    for nome, tamanho in particoes.items():

        if nome in montagens:

            ponto = montagens[nome]
            
            resultado = uso_particao(ponto)
            
            if resultado:
                total, usado, livre = resultado
                percentual = (usado / total) * 100 if total else 0
                particao = Particao(nome, ponto, total, usado, livre, percentual)
                listaParticoes.append(particao)

    return listaParticoes
                
# Formata de bloco para bytes e então para algo legível
def format_bytes(qtd):
    #Converte de blocos para bytes
    qtd /= 4

    for unidade in ['B','KB','MB','GB','TB']:

        #Se a quantidade não puder mais ser dividida
        if qtd < 1024:

            return f"{qtd:.1f}{unidade}"
        
        #Divide para a próxima unidade
        qtd /= 1024

    return f"{qtd:.1f}PB"


# Pega os dados globais do sistema
def pega_sistema() -> Sistema:

    sistemaRetorno = Sistema()

    dadosProcessador = coleta_dados_processador()
    sistemaRetorno.adiciona_dados_processador(dadosProcessador)

    dadosMem = coleta_dados_memoria_sistema()
    sistemaRetorno.adiciona_dados_memoria(dadosMem[1], dadosMem[4], dadosMem[103]) #Memória física total, Memória física livre e total de memória usada para endereçamento virtual

    processos = pega_processos(sistemaRetorno)
    sistemaRetorno.adiciona_processos(processos)

    return sistemaRetorno

# A seção abaixo coleta todos os processos do sistema e suas informações

# Coleta alguns dados variados do sistema, no momento usado principalmente para pegar o nome do processo (o indice [1])
# Pegamos algumas outras informações para, se necessário
def coleta_infos_processo(pid) -> list:
    valores_necessarios = [0,1,2,3,17] #define quais dados dos processos queremos acessar -> total: 52
    dadosProcessos = []

    with open(f"/proc/{pid}/stat") as pasta:
        processos = pasta.read().split(" ") #separa os dados da string do processo para uma lista
        dadosProcessos = [processos[i] for i in valores_necessarios] #Pega os dados do processo de posições especificamente selecionadas
        #coleta_dados_sockets(pid)
    return dadosProcessos

# Pega o id do usuário que chamou o processo
def coleta_usuario_processo(pid: int) -> int:
    caminho = f"/proc/{pid}".encode('utf-8')
    stat = Stat()

    if libc.stat(caminho, ctypes.byref(stat)) == 0:
        return stat.st_uid
    else:
        print("Erro ao coletar o usuário do processo")

# Coleta dos dos dados de entrada e saída dos arquivos e processos
def coleta_dados_IO(pid: int):
    dadosIO = []
    try:
        with open(f"/proc/{pid}/io") as t:
            linhas = t.readlines()
            for linha in linhas:
                if linha.startswith("rchar:"):
                    dadosIO.append(linha.split()[1])
                elif linha.startswith("wchar:"):
                    dadosIO.append(linha.split()[1])
                elif linha.startswith("syscr:"):
                    dadosIO.append(linha.split()[1])
                elif linha.startswith("syscw:"):
                    dadosIO.append(linha.split()[1])
    except PermissionError:
        pass

#Coleta os sockets do sistema
def coleta_dados_sockets (pid: int):
    dadosSockets = []

    diretorios = pega_ids(f"/proc/{pid}/fdinfo")
    for fd in diretorios:
        try:
            caminho = f"/proc/{pid}/fd/{fd}"
            destino = os.readlink(caminho)
            if destino.startswith("socket:["):
                dadosSockets.append(destino)
        except PermissionError:
            continue
        except FileNotFoundError:
            continue

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
        with open(f"/proc/{pid}/task/{tid}/status") as t: #abre a theread como um objeto
            nomeThread = ""
            estado = ""
            linhas = t.readlines()
            for linha in linhas:
                if linha.startswith("Name:"):
                    nomeThread = linha.split()[1]
                elif linha.startswith("State:"):
                    estado = linha.split()[1]
                #nomeThread = t.read().strip() # lê e tira os espaço que podem ter na palavra. Pega o nome da thread
        dadosThreads.append(Threads(pid, tid, nomeThread, estado)) #faz a lista de dados da thread 

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

            processo.adiciona_dados_basicos(pid, dadosProcesso[1], usuario, dadosProcesso[2], dadosProcesso[4]) #Adiciona id, nome do processo, id do usuário e prioridade
            
            #Threads
            threads = (coleta_dados_threads(pid))
            #Adiciona quantidade de threads total no prcessador
            sistema.adiciona_quantidade_threads(len(threads))
            processo.adiciona_quantidade_threads(len(threads))
            processo.adiciona_threads(threads)

            # Coleta e guarda a memória do processo
            dadosMem = coleta_dados_memoria(pid)
            processo.adiciona_dados_memoria(dadosMem[0],dadosMem[1],dadosMem[3],dadosMem[5]) #memTotal em páginas, memTotal residente em páginas, memtotal em pg usadas pelo código (text) e memtotal em pg usadas por outras coisas

            # Adiciona o processo na lista de processos
            processosRetorno.append(processo)

        except FileNotFoundError:
            continue
    
    #Adiciona quantidade de processos total no sistema
    sistema.adiciona_quantidade_processos(len(processosRetorno))

    return processosRetorno

# Função para verificar se o usuário que rodou o programa tem permissão para entrar nos diretórios
def tem_permissao(uidArquivo, gidArquivo, permissoes) -> bool:
    #Se o usuário atual é o dono do arquivo e ele pode ler ele tem permissão
    if(uid == uidArquivo and int(permissoes[0]) >= 4):
        return True
    #Idem mas para os grupos
    if(gid == gidArquivo and int(permissoes[1]) >= 4):
        return True
    #Idem mas para "outros"
    if(int(permissoes[2]) >= 4):
        return True
    #Idem mas para o root
    if(uid == 0):
        return True
    return False

# Função para transformar as permissões que temos no formato de número (ex 705) para um formato legível pelo usuário (ex rwx---r-x)
# 4 = leitura(r); 2 = escrita(w); 1 = execução(x). Os outros números são somas desses 3.
def permissoes_para_string(permissoes: int):
    permissoesString = ""
    digitos = []

    # Separa cada caractere de permissoes já que cada um representa níveis diferentes de permissão (na ordem root-grupo-usuário)
    
    while permissoes > 0:
        digitos.append(permissoes % 10)
        permissoes = permissoes // 10

    # Como append coloca no fim da lista e começamos pegando do elemento pelo número mais baixo, temos que inverter a lista
    digitos.reverse()

    for digito in digitos:
        if((digito - 4) >= 0):
            permissoesString += 'r'
            digito -= 4
        else:
            permissoesString += '-'

        if((digito - 2) >= 0):
            permissoesString += 'w'
            digito -= 2
        else:
            permissoesString += '-'

        if((digito - 1) >= 0):
            permissoesString += 'x'
            digito -= 1
        else:
            permissoesString += '-'

    return permissoesString
            

# Função para montar a árvore de diretórios do sistema, baseada na função pega_ids
def pega_arvore_diretorios(caminho: str) -> NoArquivo:
    caminhoBytes = caminho.encode('utf-8')
    pdir = libc.opendir(caminhoBytes)

    no = NoArquivo()
    stat_dir = Stat()

    #Pega informações sobre o diretório atual
    if libc.stat(caminhoBytes, ctypes.byref(stat_dir)) == 0:
        tamanho = stat_dir.st_size
        permissoesDir = int(oct(stat_dir.st_mode & 0o777)[2:])
        stringPermissoes = permissoes_para_string(permissoesDir)
        tipoNum = 4  # diretório
        tipoNome = TIPOS.get(tipoNum, "desconhecido")
        nomeDir = caminho.split('/')[-1] if caminho != '/' else '/'
        no.adicionaInformacoes(nomeDir, tipoNum, tipoNome, tamanho, stringPermissoes, [])
    else:
        print(f"Erro ao coletar dados do diretório {caminho}")
        return no  # retorna o nó vazio mesmo se não conseguir o stat

    #Pega informações sobre todos os filhos do diretório
    try:
        while True:
            stat = Stat()
            tamanho = 0
            permissoes = ""
            permitido = False

            diretorio = libc.readdir(pdir)
            if not diretorio:
                break

            try:
                nome = diretorio.contents.d_name.decode("utf-8").strip('\x00')
            except Exception as e:
                print(f"Erro ao decodificar nome em {caminho}: {e}")
                continue
            
            tipoNum = diretorio.contents.d_type
            tipoNome = TIPOS.get(tipoNum)
            caminhoArquivoAtual = caminho + '/' + nome if caminho != '/' else '/' + nome

            #Ignora as pastas do próprio arquivo (.) e do do arquivo anterior (..)
            if nome in ['.', '..']:
                continue

            #A condição é pra verificar se podemos acessar o arquivo, retorna 0 se sim. Importante para ver se temos permissão ou se o arquivo ainda existe
            if libc.stat(caminhoArquivoAtual.encode('utf-8'), ctypes.byref(stat)) == 0:
                tamanho = stat.st_size
                permissoes = int(oct(stat.st_mode & 0o777)[2:]) #Esse bando de coisa basicamente pega apenas os elementos úteis de st_mode e os torna um int
                stringPermissoes = permissoes_para_string(permissoes)
                uidArquivo = stat.st_uid
                gidArquivo = stat.st_gid
                permitido = True

            # O tipo de arquivo ser 4 indica um diretório. Navega ele se possível.
            # Não coletamos informações aqui pois, ao chamar recursivamente a função para o diretório, teremos as informações no começo ao começo
            if tipoNum == 4 and permitido:
                try:
                    # O sistema diz que temos permissão para ler fdinfo mas ao tentar acessar vemos que não temos de verdade, temos mas não temos, por isso evitamos.
                    # c é a pasta que o ponto de acesso do wsl para o diretório do windows, ignoramos pois não queremos a pasta do windows, apenas do linux.
                    if(tem_permissao(uidArquivo,gidArquivo,str(permissoes)) and nome not in ['c']):
                        filho = pega_arvore_diretorios(caminhoArquivoAtual)
                        no.filhos.append(filho)
                        no.tamanho += filho.tamanho #obs: isso aqui tem em em
                except Exception as e:
                    print(f"Erro ao abrir o diretório {caminhoArquivoAtual}: {e}")
                    continue
            # Se não for diretório só pega informações sobre ele
            else:
                filho = NoArquivo()
                filho.adicionaInformacoes(nome, tipoNum, tipoNome, tamanho, stringPermissoes, [])
                no.filhos.append(filho)
                no.tamanho += filho.tamanho

    except Exception as e:
        print(f"Erro ao abrir o diretório: {e}")
    finally:
        libc.closedir(pdir)

    return no

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