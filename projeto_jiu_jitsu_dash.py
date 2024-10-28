import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import os


load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')

def load_data_with_engine(query):
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df

query = "SELECT * FROM heroes_list"
base_heroes_list = load_data_with_engine(query)

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    /* Adjust the padding for the main content area */
    .main {
        padding-top: 0rem !important;
    }

    /* For some Streamlit versions, target this specific class */
    .block-container {
        padding-top: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Fighter Analysis", "General Analysis"])

if page == "Fighter Analysis":

    def calculate_statistics(fighter_name):
        fighter_data = base_heroes_list[base_heroes_list['Full Name'] == fighter_name]
        
        # Wins and losses
        wins = fighter_data[fighter_data['W/L'] == 'W']
        losses = fighter_data[fighter_data['W/L'] == 'L']
        
        # Stratification
        win_stats = wins['Method_Category'].value_counts().reindex(['Points', 'Advantages', 'Submission', 'Penalties', 'Referee Decision', 'Disqualification', 'Ebi/Ot'], fill_value=0)
        loss_stats = losses['Method_Category'].value_counts().reindex(['Points', 'Advantages', 'Submission', 'Penalties', 'Referee Decision', 'Disqualification', 'Ebi/Ot'], fill_value=0)
        
        return win_stats, loss_stats
    
    def display_statistics_wins(win_stats):
        # Wins
        total_wins = win_stats.sum()
        st.subheader("Wins")
        st.text(f"Total Wins: {total_wins}")
        st.text(f"By Points: {win_stats['Points']} ({win_stats['Points'] / total_wins * 100:.2f}%)")
        st.text(f"By Advantages: {win_stats['Advantages']} ({win_stats['Advantages'] / total_wins * 100:.2f}%)")
        st.text(f"By Submission: {win_stats['Submission']} ({win_stats['Submission'] / total_wins * 100:.2f}%)")
        st.text(f"By Penalties: {win_stats['Penalties']} ({win_stats['Penalties'] / total_wins * 100:.2f}%)")
        st.text(f"By Referee Decision: {win_stats['Referee Decision']} ({win_stats['Referee Decision'] / total_wins * 100:.2f}%)")
        
        if win_stats['Disqualification'] > 0:
            st.text(f"By Disqualification: {win_stats['Disqualification']} ({win_stats['Disqualification'] / total_wins * 100:.2f}%)")
        if win_stats['Ebi/Ot'] > 0:
            st.text(f"By Ebi/Ot: {win_stats['Ebi/Ot']} ({win_stats['Ebi/Ot'] / total_wins * 100:.2f}%)")

    def display_statistics_losses(loss_stats):    
        # Losses
        total_losses = loss_stats.sum()
        st.subheader("Losses")
        st.text(f"Total Losses: {total_losses}")
        st.text(f"By Points: {loss_stats['Points']} ({loss_stats['Points'] / total_losses * 100:.2f}%)")
        st.text(f"By Advantages: {loss_stats['Advantages']} ({loss_stats['Advantages'] / total_losses * 100:.2f}%)")
        st.text(f"By Submission: {loss_stats['Submission']} ({loss_stats['Submission'] / total_losses * 100:.2f}%)")
        st.text(f"By Penalties: {loss_stats['Penalties']} ({loss_stats['Penalties'] / total_losses * 100:.2f}%)")
        st.text(f"By Referee Decision: {loss_stats['Referee Decision']} ({loss_stats['Referee Decision'] / total_losses * 100:.2f}%)")

        if loss_stats['Disqualification'] > 0:
            st.text(f"By Disqualification: {loss_stats['Disqualification']} ({loss_stats['Disqualification'] / total_losses * 100:.2f}%)")
        if loss_stats['Ebi/Ot'] > 0:
            st.text(f"By Ebi/Ot: {loss_stats['Ebi/Ot']} ({loss_stats['Ebi/Ot'] / total_losses * 100:.2f}%)")

    def get_top_techniques(fighter_data, n=5):
        exclusion_conditions = (
        fighter_data['Method'].str.startswith("Pts:") |
        (fighter_data['Method'] == 'Advantages') |
        (fighter_data['Method'] == 'Pen') |
        (fighter_data['Method'] == 'Disqualification') |
        (fighter_data['Method'] == 'Ebi/Ot') |
        (fighter_data['Method'] == 'Points') |
        (fighter_data['Method'] == 'Referee Decision')
        )

        filtered_data = fighter_data[~exclusion_conditions]

        techniques = filtered_data['Method'].value_counts().head(n)
        total_fights = fighter_data.shape[0]
    
        # Handle cases where total might be zero
        if total_fights == 0:
            return techniques, pd.Series([0]*n, index=techniques.index)

        percentage = (techniques / total_fights * 100).round(2)
        return techniques, percentage

    def display_top_techniques(techniques, percentages):
        technique_df = pd.DataFrame({
        'Technique': techniques.index,
        'Times Used': techniques.values,
        'Percentage in Fights (%)': percentages.values})

        technique_df['Percentage in Fights (%)'] = technique_df['Percentage in Fights (%)'].apply(lambda x: f"{x:.2f}%")

        st.subheader("Top Techniques Used")
        st.dataframe(technique_df, use_container_width=True)

    # Função que cria as áreas vermelhas na imagem
    def create_body_heatmap(fighter_name, df, result_filter):
         # Filter data for the selected fighter
         fighter_data = df[(df['Full Name'] == fighter_name) & (df['W/L'] == result_filter)]
        
         # Count the frequency of attacks on each body part
         body_part_counts = fighter_data['Body_Part_Targeted'].value_counts()

         # Normalize frequencies (optional)
         max_count = body_part_counts.max()
         normalized_counts = body_part_counts / max_count

         # Load the base image of the human body
         body_image = Image.open("silhueta.png").convert("RGBA")

        # Create an overlay image to draw the heatmap
         overlay = Image.new("RGBA", body_image.size, (255, 0, 0, 0))
         draw = ImageDraw.Draw(overlay)
         
         body_parts = {
       'Arm': [[
           (95, 99), (83, 110), (80, 121), (79, 129), (79, 140), (71, 161), 
           (70, 168), (70, 177), (70, 188), (64, 207), (64, 225), (83, 229), 
           (88, 216), (90, 206), (90, 188), (95, 182), (98, 174), (102, 161)
       ], [
           (201, 97), (209, 104), (215, 116), (217, 126), (217, 140), (221, 149), 
           (225, 158), (227, 171), (227, 188), (231, 200), (232, 215), (232, 225), 
           (214, 229), (207, 209), (207, 188), (201, 182), (198, 171), (195, 161)
       ]],
       'Neck': [[
           (132, 73), (131, 83), (127, 86), (133, 90), (141, 92), 
           (149, 92), (160, 91), (170, 86), (165, 81), (164, 73)
       ]],
       'Wrist': [[
           (63, 237), (64, 254), (75, 254), (80, 237)
       ], [
           (216, 236), (221, 253), (232, 253), (232, 233)
       ]],
       'Leg': [[
           (96, 286), (96, 309), (98, 332), (97, 347), (97, 358), (92, 378), 
           (91, 398), (92, 426), (94, 442), (112, 442), (117, 413), (121, 404), 
           (126, 391), (125, 378), (124, 364), (127, 355), (129, 345), (134, 330), 
           (138, 318), (142, 305), (144, 295), (146, 288)
       ], [
           (151, 288), (155, 305), (159, 320), (166, 339), (168, 352), (173, 363), 
           (171, 383), (172, 396), (178, 410), (182, 426), (185, 442), (204, 443), 
           (206, 416), (206, 387), (203, 370), (200, 359), (199, 342), (198, 336), 
           (199, 322), (201, 308), (200, 293), (200, 285)
       ]],
       'Foot': [[
           (93, 457), (91, 463), (82, 472), (73, 482), (65, 486), 
           (66, 492), (72, 492), (77, 497), (83, 492), (90, 489), 
           (97, 482), (104, 478), (111, 473), (111, 465), (111, 457)
       ], [
           (186, 458), (186, 464), (186, 473), (192, 477), (198, 480), 
           (204, 487), (212, 492), (217, 496), (223, 496), (229, 492), 
           (233, 487), (227, 482), (221, 478), (215, 473), (209, 466), (203, 459)
       ]]
    #'Torso': [(225, 170, 287, 350)], 
            }

        # Apply the heatmap
         for body_part, coordinates in body_parts.items():
             if body_part in normalized_counts:
                 intensity = int(255 * normalized_counts[body_part])
                 for cood in coordinates:
                    draw.polygon(cood, fill=(255, 0, 0, intensity))
                     
         combined = Image.alpha_composite(body_image, overlay)
         combined = combined.convert("RGB")

         return combined

    st.title("Fighter Analysis")

    full_name = st.sidebar.selectbox('Full Name', list(base_heroes_list['Full Name'].unique()))
    
    col1, col2, col3 = st.columns([1, 1, 1])
    # Define a default filter
    result_filter = "W"

    # Center the buttons and place them close together
    with col1:
        with st.container():
            col1_1, col1_2, col1_3, col1_4, col1_5, col1_6 = st.columns([0.5, 0.5, 3, 3, 0.5, 0.5]) 
            
            with col1_3:
                if st.button('**Wins**'):
                    result_filter = "W"  

            with col1_4:
                if st.button('**Losses**'):
                    result_filter = "L"

    body_heatmap = create_body_heatmap(full_name, base_heroes_list, result_filter)
    
    with col1:
        st.image(body_heatmap)
    
    # Calculate and display statistics
    fighter_data = base_heroes_list[base_heroes_list['Full Name'] == full_name]

    win_stats, loss_stats = calculate_statistics(full_name)

    top_win_techniques, top_win_percentage = get_top_techniques(fighter_data[fighter_data['W/L'] == "W"])
    top_loss_techniques, top_loss_percentage = get_top_techniques(fighter_data[fighter_data['W/L'] == "L"])

    with col2:
        display_statistics_wins(win_stats)
        display_top_techniques(top_win_techniques, top_win_percentage)

    with col3:
        display_statistics_losses(loss_stats)
        display_top_techniques(top_loss_techniques, top_loss_percentage)

elif page == "General Analysis":
    st.title("General Analysis")

    year = st.sidebar.slider('Year', int(base_heroes_list['Year'].min()), int(base_heroes_list['Year'].max()))
    team = st.sidebar.selectbox('Team', options=['All'] + list(base_heroes_list['Team'].unique()))
    #stage = st.sidebar.selectbox('Stage', options=['All'] + list(base_heroes_list['Stage'].unique()))
    competition = st.sidebar.selectbox('Competition', options=['All'] + list(base_heroes_list['Competition'].unique()))
    weight = st.sidebar.selectbox('Weight', options=['All'] + list(base_heroes_list['Weight'].unique()))
    method = st.sidebar.selectbox('Method', options=['All'] + list(base_heroes_list['Method'].unique()))

    filtered_data = base_heroes_list.copy()
    if team != 'All':
        filtered_data = filtered_data[filtered_data['Team'] == team]
    #if stage != 'All':
        #filtered_data = filtered_data[filtered_data['Stage'] == stage]
    if competition != 'All':
        filtered_data = filtered_data[filtered_data['Competition'] == competition]
    if weight != 'All':
        filtered_data = filtered_data[filtered_data['Weight'] == weight]
    if method != 'All':
        filtered_data = filtered_data[filtered_data['Method'] == method]
    filtered_data = filtered_data[filtered_data['Year'] >= str(year)]

    # Fights per year Graphic
    st.subheader('Number of matches per year')
    st.bar_chart(filtered_data['Year'].value_counts())

    # Fights per Team graphic
    st.subheader('Teams with Most Fights')
    team_fights = filtered_data['Team'].value_counts()
    filtered_team_fights = team_fights[team_fights.index != '']  # Remove empty team names

    top_teams = filtered_team_fights.nlargest(10).sort_values(ascending=False)

    fig = px.bar(top_teams, x=top_teams.index, y=top_teams.values, labels={'x': 'Teams', 'y': 'Number of Fights'})
    st.plotly_chart(fig)