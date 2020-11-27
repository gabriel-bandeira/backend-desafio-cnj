<div align="center"><img img src='/static/logo.png' width="200"></div> 

# [Panorama](http://panorama-fase2.herokuapp.com/)

Este projeto é o backend da solução [Panorama](http://panorama-fase2.herokuapp.com/) e funciona em conjunto com o front-end, versionado no github [fase2_desafio_cnj](https://github.com/lfvvercosa/fase2_desafio_cnj)

Cada repositório (este e o do front-end) implementa um app no [Heroku](heroku.com). Além desses dois apps, contamos com um database, também no Heroku, onde armazenamos os dados necessários para execução da solução [Panorama](http://panorama-fase2.herokuapp.com/).

A solução [Panorama](http://panorama-fase2.herokuapp.com/) pode ser acessada por [este link](http://panorama-fase2.herokuapp.com/)

Para mais detalhes, visite o [repositório do front-end](https://github.com/lfvvercosa/fase2_desafio_cnj):

https://github.com/lfvvercosa/fase2_desafio_cnj

# Rodando a aplicação localmente

A aplicação pode rodar dentro de uma imagem docker, para isso é só rodar o comando do docker compose que já serão iniciados dois containers, um com a aplicação e outro com o banco de dados.

Durante o docker compose o banco de dados criado também é preenchido com os dados para utilizar na aplicação.

Para iniciar o backend e o banco de dados, execute:

> $ docker-compose up
