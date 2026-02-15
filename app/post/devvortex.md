# Write Up Devvortex
Neste write-up vou demonstrar o processo completo de enumeração e exploração da máquina Devvortex. A abordagem começa com enumeração de portas e serviços, passando pela identificação de um subdomínio rodando Joomla, exploração da aplicação web para obter acesso inicial, movimentação lateral através do banco de dados MySQL, e finalizando com a escalada de privilégios até obter acesso root na máquina.
## Enumeração

De começo sempre costumo rodar o nmap duas vezes, a primeira rodo por todas as portas para ver apenas as abertas, a segunda geralmente especifico para rodar com scripts, assim sei alguns possíveis caminhos da machine

`nmap —min-rate 1000 -T4 -p- 10.129.229.146`

![image.png](https://i.imgur.com/7GpJkes.png) 

`nmap -sC -A -p 80,22 10.129.229.146 -oN nmap.txt`

![image.png](https://i.imgur.com/VvDjTs1.png)

Visitando o site vemos a seguinte página:

![image.png](https://i.imgur.com/Lz5EPHZ.png)

Tem alguns detalhes que cheguei a observar como um email válido com o domínio `devvortex.htb`, ao lado dessas informações tinha um input para Newsletter que não funcionava.

![image.png](https://i.imgur.com/x02knKS.png)

![image.png](https://i.imgur.com/N0YOUoe.png)

Aproveitei para adicionar o domínio dentro da `/etc/hosts`

![image.png](https://i.imgur.com/zNHhfjB.png)

Voltando novamente ao site temos o conhecimento de quadro abas: Home, about, What we do, Portfolio e Contact Us.

Segue as imagens das páginas que citei acima?

`About:about.html`

![image.png](https://i.imgur.com/25fMGCx.png)

`What we do:do.html`

![image.png](https://i.imgur.com/xkWcw6A.png)

`Portfolio:portfolio.html`

![image.png](https://i.imgur.com/PmAyMsf.png)

`Contact Us:contact.html`

Tentei colocar algumas coisas nesses inputs e enviar depois mas sem progresso, fui analisar depois e o form estava sem action, logo não teria nenhum processamento com essas informações

![image.png](https://i.imgur.com/YaExj8w.png)

![image.png](https://i.imgur.com/AlUK8fS.png)

Nada em nenhuma pagina, então podemos a começar coisas como robots.txt e sitemap.xml, depois vamos para o nikto e gobuster, mas antes tenho que ver do que se trata as tech dessa maquina

![image.png](https://i.imgur.com/wYuURz1.png)

Nginx e Cloudflare, não sei porque mas veio Request Smuggling na cabeça agora, mas vamos rodas as ferramentas que citei e analisar robots.txt e sitemap.xml

robots.txt

![image.png](https://i.imgur.com/CONsJHu.png)

sitemap.xml

![image.png](https://i.imgur.com/CONsJHu.png)

Enquanto as duas ferramentas que citei rodam, vou tentar ver essa versão do nginx se tem alguma vulnerabilidade, e acabei achando isso daqui:

![image.png](https://i.imgur.com/C3joBoR.png)

Foi algo que me chamou atenção pois tinha pensando nessa possibilidade, já que vendo o Wappalyzer tinha visto reverse proxy, mas após algumas tentativas e juntando o output do gobuster não tinha muita coisa a se explorar, e aproveitando para falar o output do nikto também e não deu algo proveitoso

`nikto -url http://devvortex.htb`

`gobuster dir -u [http://devvortex.htb](http://devvortex.htb) -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -t 30 -x .js,.conf,.txt`

![image.png](https://i.imgur.com/sml9GuF.png)

![image.png](https://i.imgur.com/LrZOZ9q.png)

Pesquisando mais sobre nginx acabei achando essa vulnerabilidade que não me levou em lugar nenhum.

![image.png](https://i.imgur.com/pX6g2fM.png)

### Subdomain Enumeration

Como a resposta de todas as questões é a enumeração, pensei em enumerar os subdomínios e achamos o subdomínio `dev`

`gobuster vhost -u [http://devvortex.htb](http://devvortex.htb) -w ../../SecLists/Discovery/DNS/subdomains-top1million-110000.txt —no-error -t 40 —ad`

![image.png](https://i.imgur.com/L1H1nBG.png)

Agora deixar no nosso `/etc/hosts` e ver o que tem dentro desse subdomínio

![image.png](https://i.imgur.com/PrZhfTW.png)

As opções de about, services, portfólio e contact são apenas tabs

### Joomla

Uma coisa que me chamou a atenção ao analisar o *view-source* da página foi a presença de algo chamado **cassiopeia** dentro da pasta *templates*. Isso levantou a suspeita de que poderia se tratar de um CMS. Pesquisando melhor, confirmei que **Cassiopeia** é o template padrão do **Joomla 4**.

Ainda pretendo executar algumas ações nesse subdomínio, como rodar **Nikto** e **Gobuster**. Enquanto preparo as ferramentas, vou pesquisando possíveis vetores e vulnerabilidades relacionadas ao Joomla 4. Durante essa pesquisa, lembrei da existência de uma ferramenta específica chamada **JoomlaScan**, então pretendo utilizá-la em seguida

`joomscan -u [http://dev.devvortex.htb](http://dev.devvortex.htb) -ec`

![image.png](https://i.imgur.com/DNoUmqb.png)

De curioso foi ver o robots.txt e ja tinha os path da aplicação, o mais interessante para agora será o administrador page.

![image.png](https://i.imgur.com/RQrYB2M.png)

Outra coisa que posso fazer é pesquisar sobre a versão do joomla para ver se existe algum tipo de exploit

![image.png](https://i.imgur.com/Yw5t47u.png)

E acabei achando uma CVE que é para o **Joomla 4.2.8**. Mesmo sendo indicada para essa versão, sabemos que provavelmente se estende também para a **4.2.6**.

Com essa informação em mãos, podemos usar isso mais pra frente, caso não encontremos nenhum tipo de **credential** para logar no sistema, já que a vulnerabilidade é **unauthenticated**.

![image.png](https://i.imgur.com/DyccO0c.png)

Visitando o administrador page

![image.png](https://i.imgur.com/nJsXVSB.png)

Pesquisando por default credentials, foi confirmado que o Joomla não possui senha padrão. Dessa forma, o foco voltou para a CVE identificada, que aponta para um exploit no GitHub. Uma análise rápida mostrou que ele faz uso da API do Joomla para coletar informações.

![image.png](https://i.imgur.com/SqrNk6b.png)

Vamos clonar e testar esse exploit, depois de ter seguido o guide de instalação, podemos executar o exploit

![image.png](https://i.imgur.com/d53OgO8.png)


Primeira reação que tive foi de ir direto para o SSH, vai que utilizam a mesma credencial né, mas sem sucesso nas duas contas, então vamos voltar ao Joomla e ver o que eles nos entrega

![image.png](https://i.imgur.com/TDO5DYj.png)

Após me perder um pouco na quantidade de informação, comecei a pesquisar sobre Joomla Penetration Test então achei algumas coisas legais. Então descobri que podemos acessar a parte de templates do Joomla e modificar os arquivos PHP, e assim coloquei dentro do error.php o payload do PentestMonkey Reverse Shell PHP

![image.png](https://i.imgur.com/HGtOWkY.png)

![image.png](https://i.imgur.com/iCgzuXY.png)

Após colocar o payload e salvar o payload e vamos deixar o listener, e assim conseguimos o nosso querido 

![image.png](https://i.imgur.com/wKYKaen.png)

![image.png](https://i.imgur.com/KLXheI5.png)

Descobrimos que o **único usuário existente é o logan**. Como se trata de uma máquina Linux, isso indica que provavelmente será necessário realizar algum tipo de **lateral movement** até chegar nesse usuário.

## Movimentração Lateral

Após a enumeração, a porta **3306** foi identificada, indicando um serviço **MySQL** ativo. Em seguida, foi feito o login para analisar os dados disponíveis.

Abaixo estão as imagens do processo.

![image.png](https://i.imgur.com/QfLrl1m.png)

![image.png](https://i.imgur.com/qUYu3v9.png)

![image.png](https://i.imgur.com/NCeftRT.png)

![image.png](https://i.imgur.com/ekAWPwU.png)

Após consultar a consulta de users achamos a seguinte hash, que é bcrypt, no inicio achei que não iria me levar em nenhum lugar mas deixei o john fazer o serviço e assim ele encontrou a senha *tequieromucho*

![image.png](https://i.imgur.com/b6NJ1cQ.png)

![image.png](https://i.imgur.com/VjumOh3.png)

Achando as credenciais para o usuario logan vamos testar se conseguimos acessar a porta 22(SSH). Temos sucesso na nossa

![image.png](https://i.imgur.com/usNVBgg.png)

![image.png](https://i.imgur.com/hQS0A4P.png)

## Privesc

Em alguns cenários, o **apport-cli**, quando executado com sudo, pode permitir a interação com arquivos ou até a execução indireta de comandos, o que o torna um possível vetor para **privesc**.

Após uma breve enumeração encontramos o `apport-cli` com sudo. Pesquisando, descobri que o **apport-cli** é uma ferramenta usada no Ubuntu para **gerenciar e reportar crashes de aplicações**, permitindo analisar relatórios de falhas e gerar informações de debug sobre programas que falharam. Minha primeira reação foi criar um .crash e testar mas não tive exito, mas pesquisando mais um pouco descobri que é possivel executar o appor-cli com less, após executando e lendo o arquivo conseguimos dentro do less executar o !/bin/bash como root.

Abaixo segue as imagens de todo o processo até chegar em root.

![image.png](https://i.imgur.com/38tWxDZ.png)

![image.png](https://i.imgur.com/ufjI4xN.png)

![image.png](https://i.imgur.com/LKuhs6s.png)

![image.png](https://i.imgur.com/jZHuO7Y.png)

![image.png](https://i.imgur.com/UoTyumc.png)