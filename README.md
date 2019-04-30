[![Maintainability](https://api.codeclimate.com/v1/badges/4c615c9093a4c6c95d4a/maintainability)](https://codeclimate.com/github/prefeiturasp/SME-fila-da-creche-API/maintainability)

# Pátio Digital

_“Recurso público retorna ao público”._

Nós somos o **pátio digital**, uma iniciativa da Secretaria Municipal de Educação de São Paulo que, por meio do fortalecimento da transparência, da participação social e do desenvolvimento de novas tecnologias, aproxima diferentes grupos da sociedade civil por um objetivo maior: a melhoria da educação na cidade de São Paulo. 

<a href="url"><img src="http://patiodigital.prefeitura.sp.gov.br/wp-content/uploads/sites/4/2018/04/logo_fila.jpg" align="left" height="100" width="200" ></a> 

# Fila da Creche
</br>

## Conteúdo

1. [Sobre o Fila da creche](#sobre-o-fila-da-creche)
2. [Comunicação](#comunicação)
3. [Como contribuir](#como-contribuir)
4. [Requesitos](#requesitos)
5. [Organização do projeto](#organização-do-projeto)
6. [Instalação](#instalação)
7. [Endpoints de acesso](#endpoints-de-acesso)
8. [Repositórios relacionados](#repositórios-relacionados)


## Sobre o Fila da Creche 

Para que os pais e famílias possam se programar e acompanhar a geração de vagas na educação infantil, a Secretaria Municipal de Educação de São Paulo, por meio da iniciativa de governo aberto [Pátio Digital](http://patiodigital.prefeitura.sp.gov.br/), lançou uma ferramenta online inédita que permite saber como está a espera de acordo com o endereço fornecido e a faixa etária informada. 
http://filadacreche.sme.prefeitura.sp.gov.br



## Comunicação

| Canal de comunicação | Objetivos |
|----------------------|-----------|
| [Issues do Github](https://github.com/prefeiturasp/SME-fila-da-creche-API/issues) | - Sugestão de novas funcionalidades<br> - Reportar bugs<br> - Discussões técnicas |
| [Telegram](https://t.me/patiodigital ) | - Comunicar novidades sobre os projetos<br> - Movimentar a comunidade<br>  - Falar tópicos que **não** demandem discussões profundas |

Qualquer outro grupo de discussão não é reconhecido oficialmente.


## Como contribuir

Contribuições são **super bem vindas**! Se você tem vontade de construir o
Fila da creche conosco, veja o nosso [guia de contribuição](./CONTRIBUTING.md)
onde explicamos detalhadamente como trabalhamos e de que formas você pode nos
ajudar a alcançar nossos objetivos. Lembrando que todos devem seguir 
nosso [código de conduta](./CODEOFCONDUCT.md).


### Passos iniciais para contribuir

- Melhorar a qualidade de código
- Iniciar a escrita de testes unitários
- Iniciar escrita de testes funcionais
- Melhorar documentação de maneira enxuta


## Organização do projeto

* Dependências estão citadas em requirements.txt
* Arquivo .env_file gerência as variáveis de ambiente


## Requesitos

1. Docker https://docs.docker.com/install/
2. Docker Compose https://docs.docker.com/compose/install/
  

## Instalação

1. Crie um arquivo `env_file` seguindo o `env_file.sample` como referência.
2. Crie as redes externas que não conflitem com sua rede.

2.1. `docker network create fila-da-creche-api-db --subnet xxx.xxx.xxx.xxx/xx`

2.2. `docker network create fila-da-creche-api-web --subnet xxx.xxx.xxx.xxx/xx`

3. `docker-compose up`para executar o projeto.

4. Servido em `localhost:8080`.


## Endpoints de acesso

 Para acessar os dados da Api faça um request nos seguintes endpoints:
 
 https://github.com/prefeiturasp/SME-fila-da-creche-API/blob/master/app.py#L63
 https://github.com/prefeiturasp/SME-fila-da-creche-API/blob/master/app.py#L83
 https://github.com/prefeiturasp/SME-fila-da-creche-API/blob/master/app.py#L103

## Repositórios relacionados

[SME Fila da creche Front-end](https://github.com/prefeiturasp/SME-FilaDaCreche)

---

Baseado no Readme do [i-educar](https://github.com/portabilis/i-educar)
