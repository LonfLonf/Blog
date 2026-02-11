# Arquitetura e organização de computadores - Introdução

A Linguagem de um sistema computacional é totalmente diferente da linguagem humana, ou seja, para existir uma comunicação entre essas duas diferentes linguagens vamos precisar de um intermediário podendo ser um Tradutor ou Interpretador.

### Tradutores
Tradutores são responsaveis por traduzir todo um programa em uma linguagem de montagem. O fluxo geralmente é este: ```C -> Assembly -> Machine Code```

Existem alguns níveis de tradução e estarei explicando abaixo. Entre os niveis temos: Compilador(Compiler), Montador(Assembler), Ligador(Linker) e Carregador(Loader).

Só dizer os niveis e não explicar com algo visual e prático fica complicada a compreensão do assunto, por isso fiz um hello world em C, e partirei desse pequeno programa até torná-lo um executável usando GCC.

![Código em C](https://i.imgur.com/8sUebhZ.png)

Criei o arquivo C com o nome de ```hello.c```, e após isso a primeira coisa que fiz foi pre-processar o arquivo, ou seja, expandi o arquivo, então todas as referências são coladas dentro de um novo arquivo chamado ```hello.i```.

![Arquivo Criado](https://i.imgur.com/z9SWEHN.png)

Se utilizar o comando ```vim hello.i``` podemos ver como é a estrutura e como o nosso arquivo muda depois de ter utilizado do comando ```gcc -E hello.c > hello.i```

![Dentro do Hello.i](https://i.imgur.com/Qre0Pa1.png)

Agora vamos utilizar o parâmetro -S que serve para a geração do arquivo em Assembly, então vamos traduzir todo o programa em uma linguagem chamada Assembly(Linguagem de Montagem), o comando que vamos utilizar será este: ```gcc -S hello.i```, o resultado deste comando será ```hello.s```

![Arquivo Hello Compilado](https://i.imgur.com/Lacj5cx.png)

Vamos olhar novamente como o nosso arquivo fica, agora em linguagem Assembly.

![Linguagem Assembly](https://i.imgur.com/gcNC6Vw.png)

Após ter o nosso ```hello.s``` precisamos usar um Montador, ou seja, vamos pegar aquele output do compilador e transformar em linguagem de máquina, sendo esta a função do Montador. Vou utilizar o seguinte comando para realizar essa "transformação": ```gcc -c hello.s```. Depois da utilização desse comando, vamos ter o ```hello.o```

![Montador](https://i.imgur.com/anJ9xI4.png)

Analisando o ```hello.o```:

![Arquivo hello.o](https://i.imgur.com/OHk2oio.png)

Podemos ver algumas coisas interessantes aqui dentro do arquivo hello.o como o ELF, O arquivo hello.o é um arquivo objeto no formato ELF relocável, ainda não executável.

Chegando na reta final para ter um executavel precisamos usar o Linker, que tem a função de ligar os modulos e referencias, e após isso teremos nosso executavel. Vamos usar o comando ```gcc hello -o hello```

![Arquivo Executavel](https://i.imgur.com/Cjoyoib.png)

Podemos ver que o nosso hello ficou verde, significando que aquele pode ser executavel, e vamos para o ultimo passo da nossa jornada, executar nosso arquivo.

![Executando o Arquivo](https://i.imgur.com/PQxG9yw.png)

**Sumário de comandos**
```gcc -E hello.c > hello.i``` - Pre-Processamento
```gcc -S hello.i``` - Compilador 
```gcc -c hello.s``` - Montador 
```gcc hello.o -o hello``` - Linker

### Interpretadores

Meu foco aqui não é explicar muito os interpretadores mas um breve resumo: AAssim que interpreta uma linha, executa-a logo em seguida.

## Componentes de um computador
![Componentes de um computador](https://i.imgur.com/XPsGRqq.png)

Nós temos a ULA(ALU) que é responsável por fazer contas, os registradores são aqueles que possuem a capacidade de armazenar e são conhecidos por ter "memória rápida", e os dispositivos são discos, teclados, monitores, mouses e etc...
CPU busca, decodifica, executa e controla

![Barramentos](https://i.imgur.com/wtdgpBq.png)

### Barramentos
De forma resumida e para não complicar podemos entender como: Conjuntos de fios elétricos que interligam CPU, memória e outros E/S.
Temos 3 Tipos: barramento de endereços, Barramento de dados e barramento de Controle.

#### Barramento de Endereço
- Indica onde acessar endereços
- Maior quantidade de Fios -> + Quantidade de endereços (64 bits -> 2⁶⁴)Obs :x86-64 usa ~48 bits de endereço virtual
- CPU
#### Barramento de dados
- Transporta o conteudo
- 8 bits -> 1 Byte e 64 bits -> 8 bytes
- CPU <-> RAM <-> E/S
#### Barramento de Controle
- Diz o que pode fazer: ler, escrever, reset

Um pequeno exemplo é o seguinte código em assembly
```mov rax, [x]```

1. CPU coloca o endereço de x nos fios de endereço
2. CPU ativa o sinal READ no barramento de controle
3. Memória coloca o valor de x nos fios de dados
4. CPU lê os dados e guarda em rax

