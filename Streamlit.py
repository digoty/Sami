import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
import geopandas as gpd
from folium.plugins import HeatMap

#@st.cache

st.set_page_config(layout = 'wide')

#######################
##   Prepara dados   ##
#######################

endereços_meus = pd.read_excel('endereços_meus.xlsx')

# base municipios
url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-35-mun.json"
df = gpd.read_file(url)
SP = df[df.name == 'São Paulo'].reset_index(drop=True)
df = df[df.id != '3550308'].drop(columns = ['description']) #tira o municipio de SP
# base bairros
url =  "https://raw.githubusercontent.com/codigourbano/subprefeituras-sp/master/data/subprefeituras-sp.geojson"
df2 = gpd.read_file(url)
df2 = df2[['id', 'name', 'geometry']]
# junta ambas
df_mapa = df.append(df2).reset_index(drop=True)
# state_datas
state_data = endereços_meus[['Endereço', 'id_mun', 'id_bairro']]
state_data['id_mun'] = state_data.apply(lambda x: x.id_mun if x.id_bairro == None else x.id_bairro, axis=1)
state_data = state_data.drop(columns = 'id_bairro')

#Beneficiários
state_data_benefi = pd.read_excel('state_data_benefi.xlsx')
state_data_benefi.id = state_data_benefi.id.astype(str)
state_data_benefi['id'] = state_data_benefi.apply(lambda x: '0'+x.id if len(x.id)==1 else x.id, axis=1)
df_mapa_benefi = df_mapa.merge(state_data_benefi, on='id')
df_mapa_benefi.Quantidade = df_mapa_benefi.Quantidade.str.replace(',', '.').astype(float)

benefi = pd.read_excel('benefi.xlsx')
benefi = benefi.drop(columns='Endereço').values.tolist()

#Especialidades
state_data_espcl = pd.read_excel('state_data_espcl.xlsx')
state_data_espcl['id'] = state_data_espcl['id'].astype(str)
state_data_espcl['id'] = state_data_espcl.apply(lambda x: '0'+x.id if len(x.id)==1 else x.id, axis=1)
df_mapa_espcl = df_mapa.merge(state_data_espcl, on='id')
df_mapa_espcl.Quantidade = df_mapa_espcl.Quantidade.str.replace(',', '.').astype(float)

espcl = pd.read_excel('espcl.xlsx')
espcl = espcl.drop(columns=['Endereço', 'DS_ESPECIALIDADE']).values.tolist()

#Prestadores
state_data_prest = pd.read_excel('state_data_prest.xlsx')
state_data_prest.id = state_data_prest.id.astype(str)
state_data_prest['id'] = state_data_prest.apply(lambda x: '0'+x.id if len(x.id)==1 else x.id, axis=1)
df_mapa_prest = df_mapa.merge(state_data_prest, on='id')

prest = pd.read_excel('prest.xlsx')
prest = prest.drop(columns=['Endereço', 'NM_FANTASIA_PRESTADOR', 'DS_TIPO_PRESTADOR']).values.tolist()

#######################



## Desenha o dash:

st.markdown("# Heatmap prestadores, especialidades e membros")
st.sidebar.markdown("## Filtros para visão detalhada:")



## Pega informações para listas de seleções

Lista_prestador = ['']
Lista_bairro = ['']
Lista_especialidade = ['']




st.sidebar.markdown("### Bairros:")
Bairro_selec = st.sidebar.multiselect('Selecione os bairros/municípios que deseja visualizar', Lista_bairro, Lista_bairro[0])
st.sidebar.markdown('___')

st.sidebar.markdown("### Prestadores:")
Prestador_selec = st.sidebar.multiselect('Selecione os prestadores que deseja visualizar', Lista_prestador, Lista_prestador[0])
st.sidebar.markdown('___')

st.sidebar.markdown("### Especialidades:")
Especialidade_selec = st.sidebar.multiselect('Selecione as especialidades que deseja visualizar', Lista_especialidade, Lista_especialidade[0])
st.sidebar.markdown('___')




## Faz mapa
df_mapa_benefi = df_mapa_benefi.fillna(0)
df_mapa_espcl = df_mapa_espcl.fillna(0)
df_mapa_prest = df_mapa_prest.fillna(0)

final_df = df_mapa_benefi.rename(columns = {'Quantidade': 'QTD_BEN'})
final_df['QTD_ESP'] = df_mapa_espcl.Quantidade
final_df['QTD_PRE'] = df_mapa_prest.Quantidade

df_mapa_benefi.Quantidade = df_mapa_benefi.Quantidade.apply(lambda x: None if x == 0 else x)
df_mapa_espcl.Quantidade = df_mapa_benefi.Quantidade.apply(lambda x: None if x == 0 else x)
df_mapa_prest.Quantidade = df_mapa_benefi.Quantidade.apply(lambda x: None if x == 0 else x)

from folium.plugins import StripePattern

# final_df['Quantidade'] = final_df['Quantidade'].fillna(0)

# We create another map called sample_map2.
sample_map2 = folium.Map(location=[-23.639170, -46.552019], zoom_start=10,tiles=None)
folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(sample_map2)



#Adiciona mapas de calor
#1- Beneficiários
folium.Choropleth(  geo_data=df_mapa_benefi,
                    data=df_mapa_benefi,
                    columns=['id',"Quantidade"],
                    key_on="feature.properties.id",
                    fill_color='YlGnBu',
                    fill_opacity=.7,
                    line_opacity=0.2,
                    legend_name="Quantidade beneficiários",
                    smooth_factor=0,
                    Highlight= True,
                    line_color = "#0000",
                    name = "Mapa -Beneficiarios",
                    show=True,
                    overlay=True,
                    nan_fill_color = "White"
                    ).add_to(sample_map2)

HeatMap(benefi).add_to(folium.FeatureGroup(name='Heat Map - Beneficiarios', show=False).add_to(sample_map2))

#2- especialidade
folium.Choropleth(  geo_data=df_mapa_espcl,
                    data=df_mapa_espcl,
                    columns=['id',"Quantidade"],
                    key_on="feature.properties.id",
                    fill_color='YlGnBu',
                    fill_opacity=.7,
                    line_opacity=0.2,
                    legend_name="Quantidade especialidade",
                    smooth_factor=0,
                    Highlight= True,
                    line_color = "#0000",
                    name = "Mapa - Especialidade",
                    show=False,
                    overlay=True,
                    nan_fill_color = "White"
                    ).add_to(sample_map2)

HeatMap(espcl).add_to(folium.FeatureGroup(name='Heat Map - especialidades distintas', show=False).add_to(sample_map2))

#3- Prestadores
folium.Choropleth(  geo_data=df_mapa_prest,
                    data=df_mapa_prest,
                    columns=['id',"Quantidade"],
                    key_on="feature.properties.id",
                    fill_color='YlGnBu',
                    fill_opacity=.7,
                    line_opacity=0.2,
                    legend_name="Quantidade prestadores",
                    smooth_factor=0,
                    Highlight= True,
                    line_color = "#0000",
                    name = "Mapa - Prestadores",
                    show=False,
                    overlay=True,
                    nan_fill_color = "White"
                    ).add_to(sample_map2)

HeatMap(prest).add_to(folium.FeatureGroup(name='Heat Map - Pontos de atendimentos', show=False).add_to(sample_map2))






# Here we add cross-hatching (crossing lines) to display the Null values.
nans = final_df[final_df["QTD_BEN"].isnull()]['id'].values
gdf_nans = final_df[final_df['id'].isin(nans)]
sp = StripePattern(angle=45, color='grey', space_color='white')
sp.add_to(sample_map2)
# folium.features.GeoJson(name="Cidades sem membros",data=gdf_nans, style_function=lambda x :{'fillPattern': sp},show=True).add_to(sample_map2)



#Plota a cidade de SP
folium.features.GeoJson(name="Cidade de São Paulo",data=SP,show=True, style_function = lambda x: {'fillOpacity': 0} ).add_to(sample_map2)


# Add hover functionality.
style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}
NIL = folium.features.GeoJson(
    data = final_df,
    style_function=style_function, 
    control=False,
    highlight_function=highlight_function, 
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name', 'QTD_BEN','QTD_ESP', 'QTD_PRE'],
        aliases=['Cidade/Bairro: ','Quantidade de beneficiários: ', 'Quantidade de especialidades distintas: ', 'Quantidade de pontos de atendimentos: ' ],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
    )
)
sample_map2.add_child(NIL)
sample_map2.keep_in_front(NIL)




# We add a layer controller. 
folium.LayerControl(collapsed=True, ).add_to(sample_map2)

folium_static(sample_map2, width=1500, height=700)
