import requests
import json
import streamlit as st
import json
import pandas as pd
import unicodedata
import numpy as np
import pydeck as pdk
import plotly.express as px
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
 

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')

@st.cache(persist=True)
def load_data(values,api_key):
    response = requests.get('https://api.desarrolladores.energiaabierta.cl/bencina-en-linea/v1/combustibles/vehicular/estaciones.json/?auth_key='+api_key)
    if response.status_code==200:
        s=json.loads(response.text,encoding='utf-8',strict=False)
        data=pd.DataFrame(s['data'],columns=s['headers'])
        lowercase = lambda x: str(x).lower().replace(' ', '_')
        data.rename(lowercase, axis="columns", inplace=True)
        data.rename(strip_accents, axis="columns", inplace=True)
        data.rename(columns={
            'latitud':'lat',
            'longitud':'lon',
            'gasolina_93_$/l':'gasolina_93',
            'gasolina_95_$/l':'gasolina_95',
            'gasolina_97_$/l':'gasolina_97',
            'petroleo_diesel_$/l':'petroleo_diesel'},inplace=True)
        data.set_index('id',inplace=True)
        data['ultima_actualizacion']=pd.to_datetime(data['ultima_actualizacion'],infer_datetime_format=True)
        for v in values:
            data[v] = pd.to_numeric(data[v], errors='coerce')
        data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
        data['lon'] = pd.to_numeric(data['lon'], errors='coerce')
        data['region'] = data['region'].astype('category')
        data['id_region'] = data['id_region'].astype('category')
        data.dropna(how="any",inplace=True)
        return data
    else:
        data=pd.read_csv('precios_bencinas.csv')
        data['region'] = data['region'].astype('category')
        data['id_region'] = data['id_region'].astype('category')
    return data

def main():
    api_key='02f23d8e1dd050539725ce70b158e81bf6416cec'
    val=['gasolina_93','gasolina_97','gasolina_95','petroleo_diesel']
    data=load_data(val,api_key)

    st.title("Precios de Combustibles")


    if data is not None:
        scaler = lambda x : (x-x.min())/(x.max()-x.min())
        data.to_csv('precios_bencinas.csv')
        st.markdown("Esta es una aplicacion web para monitorear precios de combustibles")

        option = st.selectbox('Que tipo de combustible desea revisar?',val)
        st.write('You selected:', option)
        sns.catplot(x="id_region", y=option, kind="bar", data=data)
        st.pyplot()


        midpoint = (-35.4264, -71.65542)
        r=pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": midpoint[0],
                "longitude": midpoint[1],
                "zoom": 12,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                "HexagonLayer",
                data=data[[option, 'lat', 'lon']],
                get_position=["lon", "lat"],
                auto_highlight=True,
                radius=400,
                extruded=True,
                pickable=True,
                elevation_scale=3,
                elevation_range=[0, 2000],
                ),
            ],
            tooltip=True
        )
        st.write(r)

        st.header("Top 5 Precios")
        values = np.unique(data['id_region'].cat.categories)
        options = np.unique(data['region'].cat.categories)

        region = st.selectbox('Seleccione region',  options)
        st.bar_chart(data.loc[data['region']==region][val].sort_values(by=[option], ascending=False)[:5])
        #if st.checkbox("Show raw data", False):
        #    st.write(data)

    else:
        st.markdown("Esta aplicacion no esta disponible en este momento")

if __name__ == '__main__':
	main()