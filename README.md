# trabalho-SO
Repositório para realização do trabalho "dashboard" da matéria Sistemas Operacionais da UTFPR

O trabalho consiste em coletar informações relevantes da pasta /proc/ dentro de sistemas Linux e mostrá-las na forma de um Dashboard, com as restrições de que: 
  - Não podem ser usadas bibliotecas como OS ou Pathlib, mas sim outras que implementam chamadas de mais baixo nível. Aqui usamos Ctype, que implementa bibliotecas de C para uso em Python.
  - O projeto deve ser multithreads. Aqui são implementadas três: uma para coletar os dados, outra para processá-los quando necessário e outra para a interface. Para resolver as condições de disputas entre as threads, foi usada a biblioteca Queue, que implementa algo semelhante à um semáforo/mutex.

A interface consiste em uma área para as informações do sistema como um todo, mostrando informações da CPU a da memória RAM, além de outras que podem ser relevantes como número de processos e threads atualmente no sistema. Existem dois gráficos, um que mostra o uso de CPU ao longo do tempo e outro o uso de memória RAM. Por fim há uma tabela com todos os processos em execução no sistema, que mostra informações simples sobre cada processo, como id e nome. Ao clicar sobre um processo são mostradas informações mais detalhadas, como uso de memória em diferentes campos, a prioridade do processo, informações sobre as threads do processo, etc.

Comandos relevantes:

- make install - instala todas as dependências do programa
- make run - roda o programa

Importante: o programa roda APENAS em sistemas Linux (bem como em máquinas virtuais/WSL)
