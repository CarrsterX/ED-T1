import requests
import json
import streamlit as st
import pandas as pd
import unicodedata
import numpy as np
import pydeck as pdk
import plotly.express as px
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from haversine import haversine

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
    if unicodedata.category(c) != 'Mn')

@st.cache(persist=True)
def load_data(values,api_key):
    response = requests.get('https://api.desarrolladores.energiaabierta.cl/bencina-en-linea/v1/combustibles/vehicular/estaciones.json/?auth_key='+api_key)
    if response.status_code==200:##consulta si obtiene una respuesta de la api
        s=json.loads(response.text,encoding='utf-8',strict=False)
        data=pd.DataFrame(s['data'],columns=s['headers'])
        lowercase = lambda x: str(x).lower().replace(' ', '_')
        data.rename(lowercase, axis="columns", inplace=True)##cambia todo a minusculas
        data.rename(strip_accents, axis="columns", inplace=True)##quita todos los acentos 
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

def contador_reg01(region):
    indice_reg = region['id_region']
    aux = 0
    for temp in indice_reg:
        if(temp == '01'):
            aux+=1
    return aux    

def grafo(tarapaca): #Funcion que inicia la creacion del grafo        
    lon = tarapaca['lon']
    lat = tarapaca['lat']
    
    vencineras = contador_reg01(tarapaca)
    H = nx.Graph()

    aux = 1
    while(aux < vencineras+1):
        H.add_node(aux, pos = [lon[aux-1],lat[aux-1]])
        aux+=1       
        i = 1
        while(i < vencineras):
            j=i+1
            while(j < vencineras+1):
                #administrar datos para obtener peso 
                p1 = (lon[i-1],lat[i-1])
                p2 = (lon[j-1],lat[j-1])
                dist = haversine(p1,p2)
                H.add_edge(i,j, weight = dist)

                j+=1
            i+=1
   
    #print(H.nodes.data())
    #print(H.get_edge_data(1,2))
    #print(list(nx.dijkstra_path(H, source=26, target=1, weight= None)))

    return H

def arbol(H):#genera el arbol
    T = nx.Graph()
    T = nx.minimum_spanning_tree(H)

    #nx.draw(T)
    #plt.show()

    return T

def conectors_H(H):#genera los conectores para mostrar el grafo en el mapa
    
    datosTo_mapa = []
    diccionario = {}

    i = 1
    while(i<26):
        j = i+1
        while(j<27):
            #generacion del diccionario
            nodep = H.nodes[i]['pos']
            nodeh = H.nodes[j]['pos']
            diccionario = {"start":nodep,"end":nodeh,"name":"" + i.__str__()+"-"+j.__str__()} 
            datosTo_mapa.append(diccionario)
            j+=1
        i+=1
    #print(datosTo_mapa)
    return datosTo_mapa

def conectorG(arbol):#genera los conectores para mostrar el arbol en el mapa
    
    datos_arbol = []
    diccionario = {}

    aristas = arbol.edges()

    for aux in aristas:
        nodep = arbol.nodes[aux[0]]['pos']
        nodeh = arbol.nodes[aux[1]]['pos']
        diccionario = {"start":nodep,"end":nodeh,"name":"" + aux[0].__str__()+"-"+aux[1].__str__()} 
        datos_arbol.append(diccionario)
    return datos_arbol

def pesoA(T):
    peso = 0

    aristas = T.edges()

    for aux in aristas:
        var = T.get_edge_data(aux[0],aux[1])
        peso += var['weight'] 

    return peso

def main():
    api_key='02f23d8e1dd050539725ce70b158e81bf6416cec'
    val=['gasolina_93','gasolina_97','gasolina_95','petroleo_diesel']
    data=load_data(val,api_key)

    ##titulo inicial de la pagina
    st.title("Precios de Combustibles")

    ## Comienzo de las 3 etapas de la pagina
    if data is not None:##consulta si existen datos
        
        data.to_csv('precios_bencinas.csv')#guarda los datos en un archivo 
        H = grafo(data)#LLama a la funcion Grafo
        #nx.draw(H)
        #plt.show()

        T = arbol(H)

        datos_arbol = conectorG(T)
        
        peso_arbol = pesoA(T)
        
        datosTo_mapa = conectors_H(H)

        st.markdown("Esta es una aplicacion web para monitorear precios de combustibles")

        option = st.selectbox('Que tipo de combustible desea revisar?',val)#llamada al creador de la casilla de seleccion
        st.write('You selected:', option)
        sns.catplot(x="id_region", y=option, kind="bar", data=data)
        st.pyplot()##llamdo de streamlit hacia pyplot para generar la grafica 
        #fin de la generacion de la grafica

        #comienzo del mapa
        st.write('Mapa representarivo de geolocalizacion de vencineras\n')
        midpoint = (-20.25879, -70.13311)#situa el mapa en la primera region a trabajar 
        ##generador del mapa
        r=pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",##selecciona el formato del mapa
        initial_view_state={##selecciona vista inicial del mapa
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 13,
            "pitch": 50,
        },
        layers=[##genera una capa para agregar figuras o popup en el mapa
            pdk.Layer(
            "HexagonLayer",
            data=data[[option, 'lat', 'lon']],##obtiene la longitud y latitud de cada vencinera
            get_position=["lon", "lat"],##situa la generacion en la ubicacion obtenida antes 
            auto_highlight=True,
            radius=20,##radio del objeto generado
            extruded=True,
            pickable=True
            ),

            ##nuevo layer que permite la generacion de lineas 
            pdk.Layer(#las lineas se generan con un inicio y fin 
            "LineLayer",
            data = datos_arbol, #si se quiere mostrar el grafo en el mapa, solo debe reemplazar "datos_arbol" por "datosTo_mapa"
            get_source_position = "start",
            get_target_position = "end",  
            picking_radius=8,
            get_width=2,
            get_color=255,
            highlight_color=[255, 255, 0],
            auto_highlight=True,
            pickable=True, 
            ),
        ],
        tooltip=True
        )
        st.write(r)##escribe el mapa con su respectivos objetos en la pagina
        #fin del mapa
        st.write('El recorrido del arbol representa '+ str(peso_arbol) +'km\n')

        ##top de precios (al final de la pagina)
        st.header("Top 5 Precios")
        values = np.unique(data['id_region'].cat.categories)
        options = np.unique(data['region'].cat.categories)

        region = st.selectbox('Seleccione region', options)
        st.bar_chart(data.loc[data['region']==region][val].sort_values(by=[option], ascending=False)[:5])

        #fin del top 5 precios

    else:
        ##mensaje en el caso de que los datos no sean cargados
        st.markdown("Esta aplicacion no esta disponible en este momento")

##inicio del programa
if __name__ == '__main__':
    main()##llamado a la funcion contenedora
