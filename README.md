# Jiu-Jitsu Analytics

## 🥋 Visão Geral

Este projeto é uma visualização interativa de dados de Jiu-Jitsu desenvolvida com Streamlit. O principal objetivo do projeto é identificar as partes do corpo onde o atleta selecionado é mais eficiente atacando (nas vitórias) e onde ele tende a se expor (nas derrotas). Outras análises estão disponíveis, como a evolução do número de lutas competitivas de Jiu Jitsu ao longo dos anos. Em breve novas análises serão implementadas! 

Segue o link para acessar o Dashboard: https://app-jiu-jitsu-szkogmnlelxfot2qehc8eh.streamlit.app/

## 📌 O Projeto

O desenvolvimento do projeto seguiu as seguintes etapas:

1️⃣ **Coleta de Dados:** Realizei Web Scraping com a biblioteca Beautiful Soup para obter a base de dados;  
2️⃣ **Armazenamento:** A base foi inicialmente armazenada em um banco PostgreSQL local, utilizando SQLAlchemy. Posteriorment, fiz a migração para o Tembo, um serviço de cloud com um free tier excelente;  
3️⃣ **Dashboard:** Usei o Streamlit para criar uma visualização interativa dos dados;  
4️⃣ **Deployment:** Utilizei a própria plataforma do Streamlit (Streamlit Community Cloud) para realizar o deploy do projeto. 

A principal funcionalidade se encontra na página "Fighter Analysis". Nessa página você encontra o mapa de calor do corpo humano, destacando as áreas em que o atleta selecionado é mais eficiente atacando (nas vitórias) e onde ele tende a se expor (nas derrotas). 

Vamos usar como exemplo o Micael Galvão (do qual sou muito fã): 

A imagem a seguir mostra as áreas que históricamente o Mica é mais eficiente nos ataques. É perigoso deixar os braços, e principalmente, o pescoço desprotegido em uma luta contra o Micael. 

<p align="center">
  <img src="mica-01.png" alt="Mapa de Calor de Vitórias" width="300">
</p>

Nas poucas derrotas por finalização que o Micael Galvão sofreu, o seu pé/tornozelo foi atacado, o que indica que esse pode ser um caminho a ser explorado pelos adversários. 

<p align="center">
  <img src="mica-02.png" alt="Mapa de Calor de Derrotas" width="300">
</p>

Além disso, na página "General Analysis" você pode visualizar algumas análises gerais sobre o esporte:  
- Evolução do número de lutas competitivas de Jiu-Jitsu ao longo dos anos;
- Número de lutas que cada equipe teve. Identificamos que a equipe com o maior número de lutas é a Alliance.

Você pode usar uma série de filtros para visualizar os dados da forma que preferir. 

Em breve novas analises serão implementadas!

## 🛠️ Tecnologias Utilizadas

**Linguagens:**   
- Python

**Bibliotecas e Módulos:**  
- Pandas
- Beautiful Soup
- Streamlit
- Plotly
- Regex
- SQLAlchemy
- psycopg2-binary
- Python-dotenv
- Pillow
- Requests

**Banco de Dados:**   
- PostgreSQL

**Plataforma Clound:**  
- Tembo.io  
- Streamlit Community Cloud

## 📋 Pré-Requisitos  
1. Instalar Python  
2. Instalar dependências do projeto:  

```bash
    pip install -r requirements.txt
```

## 🚀 Como Rodar o Projeto
Para iniciar o aplicativo em um ambiente local, siga estas etapas:

```bash  
## Clone o repositório  
git clone https://github.com/Vinicius-FBr/streamlit-jiu-jitsu.git
```

É necessário atualizar as informações de conexão de banco de dados, presentes no arquivo projeto_jiu_jitsu_scraping.py com os seus dados. O mesmo deve ser feito no arquivo projeto_jiu_jitsu_dash.py. 

Caso esteja rodando o projeto em um banco de dados local, é ok deixar as informações de conexão no próprio código, como fiz no projeto_jiu_jitsu_scraping.py

Agora, caso pretenda disponibilizar o código para outros usuários, não é recomendado deixar as informações do código, isso acarreta problemas de segurança. Uma possibilidade seria utilizar um arquivo .env (conforme utilizei no projeto_jiu_jitsu_dash.py). Coloque as credenciais no arquivo e deixe-o salvo no mesmo diretório do script para gerar o dashboard. 

Após seguir as recomendações acima:

```bash
## Execute o script de Web Scrapping - isso demora em torno de 20 minutos  
python projeto_jiu_jitsu_scraping.py

# Execute o arquivo para visualizar o Dashboard
streamlit run projeto_jiu_jitsu_dash.py
```

## 🤝 Contribuições
Contribuições são bem-vindas! Para contribuir, faça um fork do projeto e envie um pull request.

## ⚠️ Observação Importante  
As análises contidas nesse projeto foram realizadas com base nos dados obtidos no site BJJ Heroes (https://www.bjjheroes.com/a-z-bjj-fighters-list). Não existe garantia de que todo o histórico de lutas do atleta esteja contido na base de dados, assim, as análises apresentadas podem não refletir a realidade devido a possibilidade da fonte de dados não estar completa. 

