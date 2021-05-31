from altair.vegalite.v4.schema.core import Legend
import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta, datetime
import pickle
import numpy as np
import os


st.set_page_config(layout = 'wide')


#Carrega dados
with open("Dados/Full.txt", 'rb') as f:
    Cat_full = pickle.load(f)

# Faz título para sidebar e cria seleção do assunto
assuntos = ['CX', 'Guias', 'Pós-vendas']
st.sidebar.markdown('## Assunto')
tema_selec = st.sidebar.radio('Selecione:', assuntos)
st.sidebar.markdown('___')





## Seleciona range de datas
st.markdown("# Motivos de contato")
min_date = date(2021,1,1)
max_date = date(2021,6,1)

a_date = st.date_input("Selecione o range de datas:", (min_date, max_date))
min_date = a_date[0]
max_date = a_date[1]

data = min_date

######################
### Valores totais ###
######################

#### Trata dados #####
## Pega infos selecionadas e filtra base full
#pega último domingo
while data.weekday() != 0:
    data = data - timedelta(days=1)
#pega todos os domingos
datas_select = [data]
while data <= max_date:
    data = data + timedelta(days=7)
    if data <= max_date:
        datas_select.append(data)
        
Cat_full_filtrada = []
for ele in Cat_full:
    if ele['referência'] in datas_select:
        Cat_full_filtrada.append(ele)

#conta total dentro do range
Cat_filtrada_total = {}
for ele in Cat_full_filtrada:
    Cat_semana = ele['infos']
    
    for cat in Cat_semana.keys():
        if cat not in Cat_filtrada_total.keys():
            Cat_filtrada_total[cat]  = {} 
            Cat_filtrada_total[cat]['Total']  = Cat_semana[cat]['Total']
        else:
            Cat_filtrada_total[cat]['Total'] += Cat_semana[cat]['Total']

        for subcat in Cat_semana[cat].keys():
            if subcat != 'Total':
                if subcat not in Cat_filtrada_total[cat].keys():
                    Cat_filtrada_total[cat][subcat]  = {} 
                    Cat_filtrada_total[cat][subcat]['Total']  = Cat_semana[cat][subcat]['Total']
                else:
                    Cat_filtrada_total[cat][subcat]['Total'] += Cat_semana[cat][subcat]['Total']

                for subcat2 in Cat_semana[cat][subcat].keys():
                    if subcat2 != 'Total':
                        if subcat2 not in Cat_filtrada_total[cat][subcat].keys():
                            Cat_filtrada_total[cat][subcat][subcat2]  = {} 
                            Cat_filtrada_total[cat][subcat][subcat2]['Total']  = Cat_semana[cat][subcat][subcat2]['Total']
                        else:
                            Cat_filtrada_total[cat][subcat][subcat2]['Total'] += Cat_semana[cat][subcat][subcat2]['Total']

#conta categorias
Categão = {}
for cat in Cat_filtrada_total.keys():
    if cat not in Categão.keys():
        Categão[cat] = Cat_filtrada_total[cat]['Total']
Categão = pd.DataFrame([Categão]).transpose().sort_values(by = 0, ascending=False).reset_index().rename(columns={0: 'Qtd', 'index': 'Categoria'})

#conta subcategorias
Subcategão = {}
for cat in Categão['Categoria']:
    Subcategão[cat] = {}
    for Subcat in Cat_filtrada_total[cat].keys():
        if Subcat not in Subcategão.keys() and Subcat != 'Total':
            Subcategão[cat][Subcat] = Cat_filtrada_total[cat][Subcat]['Total']
            
for Subcat in Subcategão.keys():
        Subcategão[Subcat]['DF'] = pd.DataFrame([Subcategão[Subcat]]).transpose().sort_values(by = 0, ascending=False).reset_index().rename(columns={0: 'Qtd', 'index': 'Subcategoria'})

### Mekko ####
# paleta de cores
col1 = '#001219-#617166-#6f7e74-#7c8a81-#88958c-#939f96-#9da8a0-#a6b0a9-#aeb7b1-#b5beb8'.split('-')
col2 = '#004e5f-#005769-#005f73-#2e7785-#5b8f96-#729b9f-#88a7a7-#9fb3b0-#aab9b4-#b0bcb6'.split('-')
col3 = '#087a7c-#098688-#0a9396-#5da8a6-#87b2ae-#9cb7b2-#a6bab4-#abbbb5-#b0bcb6-#b7c2bd'.split('-')
col4 = '#55776a-#5d8375-#669081-#709e8e-#7bae9c-#87bfac-#94d2bd-#a2c7ba-#a9c2b8-#adbfb7'.split('-')
col5 = '#6f7964-#757f69-#7a856e-#8a7e66-#9a765e-#a47860-#ae7962-#b58570-#bc907d-#c29a89'.split('-')
col6 = '#9f9372-#afa27d-#b4a680-#b8aa83-#c1b289-#cbbb90-#d4c497-#dfce9f-#e9d8a6-#ebdcae'.split('-')
col7 = '#bb3e03-#be480e-#c15218-#c7652c-#ca6f37-#cd7841-#d28b55-#d69664-#daa072-#dda97f'.split('-')
col8 = '#ae2012-#b83915-#c96d44-#d2875b-#d6926a-#da9c78-#dda584-#e0ad8f-#e3b499-#e6bba2'.split('-')
col9 = "#91412c-#ac5a42-#b36048-#b9664d-#bf745d-#c27b65-#c5816c-#ca8c79-#cf9685-#d3a090".split('-')
col10= '#74191d-#801c20-#8d1f23-#9b2226-#b24835-#c67257-#d6977d-#daa089-#dda994-#e0b19e'.split('-')
paleta = [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10]

#Pega cor pra cada subcategoria
colores_cat = {}
colores_sub = {}
for n in range(len(Categão['Categoria'])):
    N = 0
    colores_cat[Categão['Categoria'][n]]= paleta[n][N]

    # valor do incremento para as cores (se a lista tem 2 subs só pego as duas cores mais opostas)
    incremento = 9//(len(Cat_filtrada_total[Categão['Categoria'][n]]))

    for Subcat in Cat_filtrada_total[Categão['Categoria'][n]].keys():
        if Subcat not in colores_sub.keys() and Subcat != 'Total':
            N += incremento
            colores_sub[Subcat] = paleta[n][N]

#Tamanho do eixo x
len_x = int(Categão.sum().Qtd/100)*100


Categão['Class'] = 'Cat'
Categão['Qtd_total'] = Categão.groupby(['Class'])['Qtd'].transform('sum')
Categão['Qtd_norm'] = Categão['Qtd']/Categão['Qtd_total']
Categão = Categão.drop(columns = ['Class', 'Qtd_total'])
Categão['tam'] = Categão.apply(lambda x: len(x['Categoria'])/x['Qtd_norm'], axis=1)
#categoria
cat_chart = alt.Chart(Categão, height=50, width=528).mark_bar(size = 55, height=45).encode(
    x=alt.X('Qtd:Q', stack='normalize',title="", axis=alt.Axis(labels=False, grid=False, ticks = False)),
    tooltip=['Categoria:N', 'Qtd:Q'],
    order=alt.Order('Qtd', sort = 'descending'),
    color = alt.Color('Categoria:N', scale=alt.Scale(domain=list(colores_cat.keys()), range=list(colores_cat.values())), legend=None))
    
text = cat_chart.mark_text(dx=-3, dy=4, align='right', fontSize=11).encode(
    text=alt.Text('Categoria:N'), color = alt.condition(alt.datum.tam < 100, alt.value('White'),  alt.value(''),
    stroke=alt.value('dark'))
)

Categão = Categão.drop(columns = ['tam', 'Qtd_norm'])
#subcategoria
Subcategão2 = {}
for cat in Categão['Categoria']:
    Subcategão2[cat] = {}
    for Subcat in Cat_filtrada_total[cat].keys():
        if Subcat not in Subcategão2.keys() and Subcat != 'Total':
            Subcategão2[cat][Subcat] = Cat_filtrada_total[cat][Subcat]['Total']

Subcategão_mekk = pd.DataFrame()           
for cat in Subcategão2.keys():
        df = pd.DataFrame([Subcategão2[cat]])
        df['Categoria'] = cat
        Subcategão_mekk = pd.concat([df, Subcategão_mekk], axis=0, ignore_index=True)

Subcategão_mekk = Subcategão_mekk.drop_duplicates().reset_index(drop=True)
Categão_mekk = Categão.merge(Subcategão_mekk, how='left', on='Categoria')

Categão_mekk[list(Categão_mekk.columns)[2:]] = Categão_mekk[list(Categão_mekk.columns)[2:]].fillna(0).astype('int64')




qtd_cat = Categão.Qtd.sum()/13
subcat_chart = alt.Chart(Categão_mekk, height=350, width=868).transform_stack(
    stack='Qtd',
    as_=['x1', 'x2'],
    groupby=[]
).transform_fold(
    list(Categão_mekk.columns)[2:],
    as_=['subcategoria', 'subcatecoria_weight']
).transform_stack(
    stack='subcatecoria_weight',
    groupby=['Categoria'],
    as_=['y1', 'Quantidade_total']
).transform_stack(
    stack='subcatecoria_weight',
    groupby=['Categoria'],
    offset='normalize',
    as_=['y1', 'y2']
).mark_rect(strokeWidth=0.3
).encode(
    x=alt.X('x1:Q', title='', axis=alt.Axis(labels=False, grid=False, ticks = False), scale=alt.Scale(domain=[0, 600])),
    x2='x2:Q',
    y=alt.Y('y1:Q', title='', axis=alt.Axis(labels=False, grid=False, ticks = False)),
    y2='y2:Q',
    tooltip=['Categoria:N', 'subcategoria:N', 'Quantidade_total:Q'],
    color = alt.Color('subcategoria:N', scale=alt.Scale(domain=list(colores_sub.keys()), range=list(colores_sub.values())), legend = None),opacity=alt.value(0.85),
    order = alt.Order('Categoria:Q', sort = 'ascending')
)
text2 = subcat_chart.mark_text(dx=0, dy=-8, align='left', fontSize=9).encode(
    text=alt.Text('subcategoria:N'), color = alt.condition(alt.datum.Quantidade_total > qtd_cat, alt.value('White'),  alt.value(''),
    stroke=alt.value('dark')
))

subcat_chart2 = alt.layer(subcat_chart, text2)
cat_chart2 = alt.layer(cat_chart, text)
st.markdown('## Visão geral')
col1, col2 = st.beta_columns(2)
col1.markdown('### Mekko categorias e subcategorias')
col1.altair_chart(cat_chart2, use_container_width=True)
col1.altair_chart(subcat_chart2, use_container_width=True)



area_cat = {'Referência': [], 'Categoria': [], 'Qtd': []}
for ele in Cat_full_filtrada:
    ref = ele['referência']
    for cat in ele['infos'].keys():
        area_cat['Referência'].append(ref)
        area_cat['Categoria'].append(cat)
        area_cat['Qtd'].append(ele['infos'][cat]['Total'])
area_cat = pd.DataFrame(area_cat)     
area_cat.Referência = pd.to_datetime(area_cat.Referência)
area_cat.Qtd = pd.to_numeric(area_cat.Qtd)

time_cat =alt.Chart(area_cat,height=450).mark_area().encode(
    x="Referência:T",
    y="Qtd:Q",
    color=alt.Color('Categoria:N', scale=alt.Scale(domain=list(colores_cat.keys()), range=list(colores_cat.values())), legend=alt.Legend(orient='right')),
                    opacity=alt.value(0.6),
    tooltip=['Categoria:N', 'Qtd:Q', 'Referência']
).configure_axis(grid = False).interactive()

col2.markdown('### Evolução temporal categorias')
col2.altair_chart(time_cat, use_container_width=True)


st.markdown('## Deep na categoria')
col1, col2 = st.beta_columns(2)
#seleção de cat e subcat
Cat_select = 'Usando a Sami'
Subcat_select = 'Como agendar'
Cat_select = col1.selectbox('Selecione a categoria: ', list(Categão['Categoria']))



area_subcatcat = {'Referência': [], 'Subcategoria': [], 'Qtd': []}
for ele in Cat_full_filtrada:
    ref = ele['referência']
    for subcat in ele['infos'][Cat_select].keys():
        if subcat != 'Total':
            area_subcatcat['Referência'].append(ref)
            area_subcatcat['Subcategoria'].append(subcat)
            area_subcatcat['Qtd'].append(ele['infos'][Cat_select][subcat]['Total'])
area_subcatcat = pd.DataFrame(area_subcatcat)     

area_subcatcat.Referência = pd.to_datetime(area_subcatcat.Referência)
area_subcatcat.Qtd = pd.to_numeric(area_subcatcat.Qtd)


time_subcat = alt.Chart(area_subcatcat, title = 'Evolução temporal subcategorias da categoria '+Cat_select,width=800).mark_area().encode(
    x="Referência:T",
    y="Qtd:Q",
    color=alt.Color('Subcategoria:N', scale=alt.Scale(domain=list(area_subcatcat.Subcategoria.drop_duplicates()), 
                                                      range=[colores_sub[sub] for sub in list(area_subcatcat.Subcategoria.drop_duplicates())]), 
                    legend=alt.Legend(orient='right')),
                    opacity=alt.value(.9),
    tooltip=['Subcategoria:N', 'Qtd:Q', 'Referência']
).configure_axis(grid = False).interactive()

col1.altair_chart(time_subcat, use_container_width=True)




list_subcat = []
for subcat in list(Subcategão[Cat_select].keys()):
    if subcat != 'DF':
        list_subcat.append(subcat)

Subcat_select = list_subcat[0]
Subcat_select = col2.selectbox('Selecione a subcategoria: ', list_subcat)

#conta subcaregorias2 dado as categorias selecionadas
Subcateguinho = {}
for subcat2 in Cat_filtrada_total[Cat_select][Subcat_select].keys():
    if subcat2 != 'Total':
        Subcateguinho[subcat2]=Cat_filtrada_total[Cat_select][Subcat_select][subcat2]['Total']
Subcateguinho = pd.DataFrame([Subcateguinho]).transpose().sort_values(by = 0, ascending=False).reset_index().rename(columns={0: 'Qtd', 'index': 'Subcategoria2'})     



bars = alt.Chart(Subcateguinho,title = 'Relações subcategorias2 de '+ Cat_select+ " - " +Subcat_select).mark_bar().encode(
    x='Qtd:Q',
    y=alt.Y("Subcategoria2:N",title=None, sort='-x'),
    color = alt.Color('Subcategoria2', scale=alt.Scale(range= ['#002060']), legend = None),
    tooltip=['Subcategoria2:N', 'Qtd:Q']
)

text = bars.mark_text(
    align='left',
    baseline='middle',
    dx=3  # Nudges text to right so it doesn't appear on top of the bar
).encode(
    text='Qtd:Q'
)

subcat2_chart = (bars + text).properties()

col2.altair_chart(subcat2_chart, use_container_width=True)










