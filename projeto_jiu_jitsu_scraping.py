import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px
import re

# 1ª ETAPA - OBTENÇÃO DOS DADOS

url = "https://www.bjjheroes.com/a-z-bjj-fighters-list" 
response = requests.get(url)

# Cria o objeto BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser") 

# Encontramos a tabela através do nome da sua classe
tabela_lutadores = soup.find("tbody", {"class":"row-hover"})

data_list = []

for row in tabela_lutadores.find_all("tr"):
    tds = row.find_all("td") # Lista com todos os elementos td da linha da tabela que estamos iterando
    data = [td.get_text(strip=True) for td in tds] # Lista com o texto em cada elemento td da linha
    data_str = '|'.join(data) # Junta cada texto em uma única string separada por um |
    
    anchor = row.find("a") # Encontra a primeira tag de link (Anchor Tag: <a>) na linha.
    
    href = anchor["href"] # Pega o parâmetro href
    href_response = requests.get("https://www.bjjheroes.com"+href)
    href_soup = BeautifulSoup(href_response.text, "html.parser")
        
    href_table = href_soup.find("tbody") # Pega a tabela com o histórico de lutas
        
    if href_table:
        for href_row in href_table.find_all("tr"):
            href_tds = href_row.find_all("td")
            href_data = [td.get_text(strip=True) for td in href_tds]
            href_data_str = '|'.join(href_data)
            data_list.append([href, data_str, href_data_str])
    else:
        data_list.append([href, data_str, None])

df_heroes_list = pd.DataFrame(data_list, columns=["link", "dados_lutador", "historico_lutas"])

# 2ª ETAPA - TRATAMENTO DE DADOS

# Retirar valores vazios da coluna 'historico_lutas'
df_heroes_list.dropna(subset=['historico_lutas'], inplace=True)

# Separar os dados referente a coluna 'dados_lutador' em outras colunas
df_heroes_list[['First Name','Last Name','Nickname','Team']] = df_heroes_list['dados_lutador'].str.split("|", expand=True)

# Mesmo procedimento acima para a coluna 'historico_lutas'
df_heroes_list[['Id', 'Opponent', 'W/L', 'Method', 'Competition', 'Weight', 'Stage', 'Year']] = df_heroes_list['historico_lutas'].str.split("|", expand=True)

df_heroes_list.drop(columns=['dados_lutador', 'historico_lutas'], inplace=True)

# A coluna "Opponent" tem os nomes repetidos em várias linhas. Isso acontece quando oponente tem o link direcionando para sua página

def  remove_repeated_substrings(string): 
    first_half = string[: len (string)// 2 ] 
    second_half = string[ len (string)// 2 :]
     
    return first_half if first_half == second_half else string 

df_heroes_list['Opponent'] = df_heroes_list['Opponent'].apply(remove_repeated_substrings)

# A coluna W/L deve ter apenas 3 valores possíveis, essa linha garante que isso seja respeitado
df_heroes_list = df_heroes_list[df_heroes_list['W/L'].isin(['W', 'L', 'D'])] 

df_heroes_list = df_heroes_list.dropna(subset=['Weight', 'Stage', 'Year'])


df_heroes_list['Method'] = df_heroes_list['Method'].str.title()

values_to_remove = ['---', 'N/A', 'Pts: Xyes', 'Exhaustion']
mask = ~df_heroes_list['Method'].isin(values_to_remove)
df_heroes_list = df_heroes_list[mask]
df_heroes_list.reset_index(drop=True, inplace=True)


# Função que remove todos os valores que estão com uma das pontuações faltando. Ex: 'Pts: X2', 'Pts: X3' 
def remove_incorrect_pts(value):
    # Match values that start with "Pts:"
    if value.startswith("Pts:"):
        # Check for valid cases with "Adv" or "Pen" at the end
        if value.endswith("Adv") or value.endswith("Pen"):
            return True
        # Check for the correct "Pts:" format using a regex
        # This regex matches "Pts:" followed by a required number, an "x", and another required number
        if re.match(r'^Pts:\s*\d+X\d+$', value):
            return True
        # If it doesn't match the correct format, remove it
        return False
    return True

df_heroes_list = df_heroes_list[df_heroes_list['Method'].apply(remove_incorrect_pts)]

df_heroes_list['Full Name'] = df_heroes_list['First Name'] + ' ' + df_heroes_list['Last Name']

corrections = {
    'Trangle': 'Triangle',
    'Triange': 'Triangle',
    'Trianglle': 'Triangle',
    'Triangulo': 'Triangle',
    'Triangle W/ Arm': 'Triangle',
    'Arnbar': 'Armbar',
    'Armlock': 'Armbar',
    'Straight Armlock': 'Armbar',
    'Triangle-Armbar': 'Triangle Armbar',
    'Triangle/Armbar': 'Triangle Armbar',
    'Triange Armbar': 'Triangle Armbar',
    'Rnc': 'Rear Naked Choke',
    'Possible Rnc': 'Rear Naked Choke',
    'Choke From The Back': 'Choke From Back', 
    'Mata Leao': 'Rear Naked Choke',
    'Inj (Knee)': 'Injury',
    'Dq': 'Disqualification',
    'Adv': 'Advantages',
    'Advantage': 'Advantages',
    'Botinha': 'Footlock',
    'Foot Lock': 'Footlock',
    'Pressure/Injury': 'Injury', 
    'Anaconda Choke': 'Anaconda', 
    'No-Gi Ezekiel': 'Ezekiel',
    "Policeman'S Lock": 'Policeman Lock',
    'Basebal Choke': 'Baseball Bat Choke',
    'Baseball Choke': 'Baseball Bat Choke',
    'Bread Cutter': 'Bread Cutter Choke',
    'Breat Cutter': 'Bread Cutter Choke',
    'Brad Cutter Choke': 'Bread Cutter Choke',
    'Choke F. Omoplata': 'Choke From Omoplata',
    'Choke F/ Omoplata': 'Choke From Omoplata',
    'Omoplata Choke': 'Choke From Omoplata',
    'Omoplata/Choke': 'Choke From Omoplata',
    'Crucifix Armbar': 'Crucifix Armlock',
    'Ezekiel Choke': 'Ezekiel',
    'Ezequiel': 'Ezekiel',
    'Guillotina': 'Guillotine',
    'Guilotine': 'Guillotine',
    'Inside Heel Hool': 'Inside Heel Hook',
    '7-Yo-Choke': '7 Year Old Choke' ,
    '7Yo Choke': '7 Year Old Choke',
    'Armlock F/ Crucifix': 'Armlock From Crucifix',
    'Bread Slicer': 'Bread Cutter Choke', 
    'Paper Cutter Choke': 'Bread Cutter Choke',
    'Darce': 'Darce Choke', 
    'Katagame': 'Kata Gatame',
    'Katagatame': 'Kata Gatame',
    'Kimura F/ Triangle': 'Kimura From Triangle',
    'Leg Lock': 'Leglock', 
    'Ng Baseball Choke': 'Baseball Bat Choke',
    'North South Choke': 'North-South Choke',
    'Scissor Choke': 'Scissors Choke',
    'Smother': 'Smother Choke',
    'Straigh Ankle Lock': 'Straight Ankle Lock', 
    'Straight Anke Lock': 'Straight Ankle Lock',  
    'Straignt Ankle Lock': 'Straight Ankle Lock',
    'Wrislock': 'Wristlock',
    'Kimura/Triangle': 'Kimura From Triangle', 
    'Kimura-Triangle': 'Kimura From Triangle',
    'Omoplata Armbar': 'Armbar From Omoplata',
    'Omoplata Armlock': 'Armlock From Omoplata',
    'Omoplata/Armlock': 'Armlock From Omoplata',
    'Omoplata/Rnc': 'Rear Naked Choke From Omoplata',
    'Amassa Pao': 'Amassa Pao Choke',
    'Rev. Omoplata': 'Reverse Omoplata',
    'Smother Choke': 'Smother Tap',
    'Teepe Choke': 'Teepee Choke',
    'Verbal': 'Verbal Tap',
    'Arm In Rnc': 'Arm In Rear Naked Choke',
    'Body Choke': 'Body Triangle',
    'Mounted X Choke': 'Mouted Cross Choke',
    'Standing Brabo Ck': 'Standing Brabo Choke',
    'Standing X Choke': 'Standing Cross Choke',
    'Terra Lock': 'Terra Footlock',
    'Triangle Shld Lock': 'Triangle Shoulder Lock',
    'Triangle Shldr Lock': 'Triangle Shoulder Lock',
    'Triangle/Kimura': 'Triangle Kimura', 
    'Violin Armbar': 'Violin Armlock',
    'X Choke': 'Cross Choke',
    'Mir Armlock': 'Mir Lock',
    'Muffler Tap':'Muffler'
}

df_heroes_list['Method'] = df_heroes_list['Method'].replace(corrections)

def categorize_method(method):
    if method.startswith("Pts:"):
        if method.endswith("Adv"):
            return 'Advantages'
        elif method.endswith("Pen"):
            return 'Penalties'
        else:
            return 'Points'
    else:
        if method == 'Advantages':
            return 'Advantages'
        elif method == 'Pen':
            return 'Penalties'
        elif method == 'Disqualification':
            return 'Disqualification'
        elif method == 'Ebi/Ot':
            return 'Ebi/Ot'
        elif method == 'Points':
            return 'Points'
        elif method == 'Referee Decision':
            return 'Referee Decision'
        else:
            return 'Submission'

df_heroes_list['Method_Category'] = df_heroes_list['Method'].apply(categorize_method)

# Agora vamos criar a coluna que identifica qual parte do corpo a técnica está atacando
technique_to_body_part = {
    '10 Finger Guillotine': 'Neck',
    '50/50 Armbar': 'Arm',
    '7 Year Old Choke': 'Neck',
    'Amassa Pao Choke': 'Neck',
    'Americana': 'Arm',
    'Anaconda': 'Neck',
    'Ankle Lock': 'Foot',
    'Aoki Lock': 'Foot',
    'Arm In Ezekiel': 'Neck',
    'Arm In Guillotine': 'Neck',
    'Arm In Rear Naked Choke': 'Neck',
    'Arm Triangle': 'Neck',
    'Armbar': 'Arm',
    'Armlock From Crucifix': 'Arm',
    'Armlock From Omoplata': 'Arm',
    'Back Triangle': 'Neck',
    'Banana Split': 'Leg',
    'Baratoplata': 'Arm',
    'Baseball Bat Choke': 'Neck',
    'Berimbau Choke': 'Neck',
    'Bicep Slicer': 'Arm',
    'Body Lock': 'Torso',
    'Body Triangle': 'Torso',
    'Boston Crab': 'Leg',
    'Bow And Arrow': 'Neck',
    'Brabo Choke': 'Neck',
    'Bread Cutter Choke': 'Neck',
    'Buggy Choke': 'Neck',
    'Bulldog Choke': 'Neck',
    'Cachecol Choke': 'Neck',
    'Calf Crusher': 'Foot',
    'Calf Slicer': 'Leg',
    'Canto Choke': 'Neck',
    'Carney Lock': 'Arm',
    'Choke': 'Neck',
    'Choke From Back': 'Neck',
    'Choke From Mount': 'Neck',
    'Choke From Omoplata': 'Neck',
    'Clock Choke': 'Neck',
    'Collar Choke': 'Neck',
    'Copacabana Choke': 'Neck',
    'Cross Ankle Lock': 'Foot',
    'Cross Choke': 'Neck',
    'Cross Face': 'Neck',
    'Crucifix Armlock': 'Arm',
    'Crucifix Choke': 'Neck',
    'Cryangle': 'Neck',
    'Darce Choke': 'Neck',
    'Dead Orchard': 'Arm',
    'Dogbar': 'Leg',
    'Dogbar/Kneebar': 'Leg',
    'Espalha Frango': 'Torso',
    'Estima Lock': 'Foot',
    'Ezekiel': 'Neck',
    'Face Mask Choke': 'Neck',
    'Flying Armbar': 'Arm',
    'Flying Guillotine': 'Neck',
    'Flying Triangle': 'Neck',
    'Footlock': 'Foot',
    'Gogoplata': 'Neck',
    'Guillotine': 'Neck',
    'Hashimoto Choke': 'Neck',
    'Headlock': 'Neck',
    'Heel Hook': 'Foot',
    'Inside Heel Hook': 'Foot',
    'Inverted Armbar': 'Arm',
    'Inverted Katagatame': 'Neck',
    'Inverted Omoplata': 'Arm',
    'Inverted Triangle': 'Neck',
    'Japanese Necktie': 'Neck',
    'Junny Lock': 'Leg',
    'Kata Gatame': 'Neck',
    'Kimura': 'Arm',
    'Kimura From Triangle': 'Arm',
    'Kimura/Armbar': 'Arm',
    'Kimura/Choke': 'Arm',
    'Knee Choke': 'Neck',
    'Knee On Belly': 'Torso',
    'Knee On Belly/Choke': 'Neck',
    'Knee Ride': 'Torso',
    'Kneebar': 'Leg',
    'Kneebar/Dogbar': 'Leg',
    'Lapel Choke': 'Neck',
    'Lateral Kneebar': 'Leg',
    'Leaf Clover': 'Leg',
    'Leglock': 'Leg',
    'Loop Choke': 'Neck',
    'Manoplata': 'Arm',
    'Marceloplata': 'Arm',
    'Marcelotine': 'Neck',
    'Mikey Lock': 'Foot',
    'Mir Armlock': 'Arm',
    'Mir Lock': 'Arm',
    'Monoplata': 'Arm',
    'Monted Triangle': 'Neck',
    'Mount Pressure': 'Torso',
    'Mounted Choke': 'Neck',
    'Mounted Guillotine': 'Neck',
    'Mounted Triangle': 'Neck',
    'Mouted Cross Choke': 'Neck',
    'Muffler': 'Face & Arm',
    'Neck Crank': 'Neck',
    'Necktie': 'Neck',
    'No Arm Triangle': 'Neck',
    'North-South Choke': 'Neck',
    'Omoplata': 'Arm',
    'Omoplata-Wristlock': 'Wrist',
    'One Arm Guillotine': 'Neck',
    'Outside Heel Hook': 'Foot',
    'Pena Choke': 'Neck',
    'Peruvian Necktie': 'Neck',
    'Policeman Lock': 'Arm',
    'Power Guillotine': 'Neck',
    'Pressure': 'Torso',
    'Rear Naked Choke': 'Neck',
    'Rear Naked Choke From Omoplata': 'Neck',
    'Reverse Omoplata': 'Arm',
    'Reverse Triangle': 'Neck',
    'Russian Armbar': 'Arm',
    'Scissors Choke': 'Neck',
    'Shin Lock': 'Leg',
    'Short Choke': 'Neck',
    'Shoulder Lock': 'Arm',
    'Shoulder Pressure': 'Arm',
    'Sidecontrol Choke': 'Neck',
    'Smother Tap': 'Neck',
    'Standing Brabo Choke': 'Neck',
    'Standing Cross Choke': 'Neck',
    'Straight Ankle Lock': 'Foot',
    'Suloev Stretch': 'Leg',
    'Tarikoplata': 'Arm',
    'Teepee Choke': 'Neck',
    'Terra Footlock': 'Foot',
    'Toe Hold': 'Foot',
    'Toe Hook': 'Foot',
    'Triangle': 'Neck',
    'Triangle Armbar': 'Arm',
    'Triangle Armlock': 'Arm',
    'Triangle From Back': 'Neck',
    'Triangle Kimura': 'Arm',
    'Triangle Shoulder Lock': 'Arm',
    'Triangle Wristlock': 'Wrist',
    'Twister': 'Neck',
    'Violin Armlock': 'Arm',
    'Von Fluke Choke': 'Neck',
    'Wormbar': 'Arm',
    'Wormhat Choke': 'Neck',
    'Wristlock': 'Wrist',
    'Wristlock/Omoplata': 'Wrist',
    'Yoko Sankaku': 'Neck',
    'Z Lock': 'Leg'
}

df_heroes_list['Body_Part_Targeted'] = df_heroes_list['Method'].apply(
    lambda x: technique_to_body_part.get(x, 'Unknown')  # 'Unknown' for techniques not in the dictionary
)

# 3ª ETAPA - ARMAZENAMENTO DOS DADOS

user = 'postgres'
password = '1234'
host = 'localhost'
port = '5432'
database = 'Projeto_JiuJitsu'

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')

table_name = 'heroes_list'
df_heroes_list.to_sql(table_name, engine, if_exists='replace', index=False)