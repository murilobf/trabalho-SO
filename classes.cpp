//Arquivo que armazena as classes a serem utilizadas no dashboard

#include <iostream>
#include <string>

using namespace std;
//Classe que armazena os dados de um processo
class Processo{
    public:
    //Dados identificadores do processo (id, nome, usuário)
    int pid;
    string nome;
    string usuario;

    //Dados relativos a memoria do processo
    int memAlocada;
    int qtdePaginasTotal;
    int qtdePaginasCodigo;
    int qtdePaginasHeap;
    int qtdePaginasStack;

    //Dados relativos 
};

//Classe que armazena os dados do sistema
class Sistema{

    int memTotal;
    int memLivre;
    int memFisica;
    int memVirtual;
};

/*PARTE DO MURILO:
Monitorar e apresentar as informações do uso de memória dos processos; 
Este objetivo consiste em fornecer as informações de uso de memória global do 
sistema e de cada processo individualmente. Os requisitos abaixo devem ser obrigatoriamente 
seguidos: 
1. Mostrar dados globais do uso de memória do sistema, p.ex. percentual de uso da memória, 
percentual de memória livre, quantidade de memória física (RAM) e virtual, etc. 
2. Mostrar informações detalhadas sobre o uso de memória para cada processo, p.ex. quantidade 
total de memória alocada, quantidade de páginas de memória (total, de código, heap, stack), 
etc. 
3. Ao mostrar informações detalhadas de cada processo, as informações podem ser apresentadas 
em uma nova tela (ou aba) que, ao ser fechada, retorna a tela principal.
*/

/*PARTE DO HENRIQUE:
Monitorar e apresentar as características e propriedades de todos os processes existentes 
em execução no sistema operacional; 
Este objetivo consiste em implementar o primeiro conjunto de funcionalidades do 
Dashboard visando apresentar as informações sobre os processos que existem e estão executando 
no sistema operacional. Os requisitos abaixo devem ser seguidos: 
1. Mostrar dados globais do uso do processador, p.ex. percentual de uso do processador, 
percentual de tempo ocioso, quantidade total de processos e threads, etc. 
2. Mostrar a lista de processos existentes juntamente com os respectivos usuários; 
3. Mostrar informações sobre os threads de cada processo; 
4. Mostrar informações detalhadas de cada processo. Nesse caso, as informações podem ser 
apresentadas em uma nova tela (ou aba) que, ao ser fechada, retorna a tela principal.*/