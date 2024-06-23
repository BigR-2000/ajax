import pandas as pd
import streamlit as st
from scipy.stats import percentileofscore
import numpy as np
from soccerplots.radar_chart import Radar

st.set_page_config(
                   page_icon = ':ajax:',
                   layout="wide")

#functies

def radar(df, lijst):
        #st.dataframe(df)
        lijst2 = list(reversed(lijst))
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            options1 = st.radio('Land1', options=lijst)
        with col3:
            options2 = st.radio('Land2', options=lijst2)

        test = df.loc[(df['Land'] == options1) | (df['Land'] == options2)]
        df1 = test.dropna(axis=1, how='any')

        numerieke_df = df.select_dtypes(include='number')
        gemiddelden = numerieke_df.mean()
        df_parameters = df.fillna(gemiddelden)
        
        df1.reset_index(drop=True, inplace= True)
        params = list(df1.columns)
        params = params[1:]
        params
        df2 = pd.DataFrame()
        df2 = df1.set_index('Land')
        
        ranges = []
        a_values = []
        b_values = []
        #st.markdown(df1[params])
        for x in params:
            if x == 'Totaalscore':
                a = 0
            else:
                a = min(df_parameters[params][x])
                a = a * 0.98
            
            if x == 'Totaalscore':
                b = 10
            else:
                b = max(df_parameters[params][x])
                b = b * 1.1
            
            ranges.append((a, b))
            a_values.append(a)
            b_values.append(b)

        #st.dataframe(a_values)
        player_1 = df1.iloc[0,0]
        player_2 = df1.iloc[1,0]

        for x in range(len(df1['Land'])):
            x = x - 1
            if df1.iloc[x, 0] == df1.iloc[0,0]:
                a_values = df1.iloc[x].values.tolist()
            if df1.iloc[x, 0] == df1.iloc[1,0]:
                b_values = df1.iloc[x].values.tolist()

        a_values = a_values[1:]
        b_values = b_values[1:]
        values = (a_values, b_values)

        title = dict(
        title_name=f'{player_1} (red)',
        title_color='#B6282F',
        title_name_2=f'{player_2} (blue)',
        title_color_2='#344D94',
        title_fontsize=15,
        subtitle_fontsize=11
        )

        radar = Radar()

        fig, ax = radar.plot_radar(ranges= ranges, params= params, values= values, 
                                radar_color=['red','blue'], 
                                title = title,
                                alphas = [0.3, 0.3],  
                                compare=True)
        fig.set_size_inches(12, 12)
        st.dataframe(df2)
        with col2:
            st.pyplot(fig)

def bereken_percentiel_score(B):
        percentiel_scores_dict = {}
        for kolomnaam in B.columns:
            percentiel_scores_dict[kolomnaam] = B[kolomnaam].apply(lambda x: percentileofscore(B[kolomnaam], x))
        return pd.DataFrame(percentiel_scores_dict)

#inlezen bestand
data = pd.read_excel('ajax.xlsx')

#opstellen dataframe
data['% Doorstroom eerste ploeg Ajax (vanaf 21+)'] = data['% Doorstroom eerste ploeg Ajax (vanaf 21+)'] *100
data = data.round(2)
data2 = data.transpose()

#weergeven dataframes
#####st.dataframe(data, hide_index=True)
#beoordelingen maken

criteria = data.drop(columns=['Gemiddelde leeftijd aangetrokken jeugdspelers', 'Aantal doorstroom eerste ploeg ', 'Gemiddeld aantal minuten eerste ploeg (doorgestroomde spelers)', 'Gemiddelde totale kost ', 'Gemiddelde totale opbrengst'])
criteria = criteria.set_index('Land', drop=True)
####st.dataframe(criteria)
rangorde = bereken_percentiel_score(criteria)
rangorde = rangorde/10
rangorde = rangorde.round(0)
rangorde['Totaalscore'] = (rangorde['Aantal aangetrokken jeugdspelers (u15-u21)']*0.1)+ (rangorde['Gemiddeld aantal jaren bij de club']*0.1)+ (rangorde['% Doorstroom eerste ploeg Ajax (vanaf 21+)']*0.2)+ (rangorde['Gemiddeld aantal matchen eerste ploeg (doorgestroomde spelers)']*0.2)+ (rangorde['Gemiddelde winst']*0.2)+ (rangorde['Markup ratio']*0.2)

st.title('Voorbeeldcase Ajax')
st.divider()
st.write("")
st.subheader('Dataset jeugdspelers Ajax gegroepeerd volgens verschillende landen (bvb voor de laatste 10 jaar):')
#st.write('')
st.write('')
st.dataframe(data2)
st.write("")
st.write("")
st.subheader("Rangschikking landen op basis van de criteria:")
st.write("")
st.dataframe(rangorde)
st.write("")
st.write("")
st.subheader("Datavisualisatie:")
st.write("")
#visualisatie
lijst_landen= ['Senegal', 'Nederland', 'Zwitserland', 'België', 'Duitsland', 'Argentinië', 'Nigeria', 'Brazilië', 'Denemarken', 'Gemiddelde Landen']
merge_criteria = pd.merge(criteria, rangorde[['Totaalscore']], on= 'Land', how='left')
merge_criteria = merge_criteria.rename(columns={'Aantal aangetrokken jeugdspelers (u15-u21)': 'Aantal jeugdspelers', 'Gemiddeld aantal jaren bij de club': 'Aantal jaren club', '% Doorstroom eerste ploeg Ajax (vanaf 21+)': '% Doorstroom 1e ploeg', 'Gemiddeld aantal matchen eerste ploeg (doorgestroomde spelers)': 'Aantal matchen 1e ploeg'})
kopie = merge_criteria.copy(deep=True)
kopie.reset_index(inplace=True)
kopie['Land'] = 'Gemiddelde Landen'
kopie = kopie.groupby('Land').mean()
kopie = kopie.round(1)
test = pd.concat([merge_criteria, kopie])
test = test.reset_index()

#st.dataframe(merge_criteria)
rangorde2 = rangorde.reset_index()
criteria2 = merge_criteria.reset_index()
radar(test, lijst_landen)
