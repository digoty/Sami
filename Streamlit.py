from altair.vegalite.v4.schema.core import Legend
import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta, datetime
import pickle
import numpy as np
import os
import base64

st.set_page_config(layout = 'wide')

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

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
min_date = date.today() - timedelta(days=21)
max_date = date.today()

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
col7  = '#50e29b-#2cc95b-#6cda7d-#95de91-#7ad062-#75c743-#9dd062-#afd572-#c3de92-#cee2a0'.split('-')
col2  = '#a8201a-#a03828-#985036-#906844-#8c744b-#7e714e-#877d5a-#928a63-#a39d7a-#aba686'.split('-')
col9  = '#dad2d8-#c7c0c5-#beb7bc-#b9b3b7-#b4aeb2-#b6b2a9-#bdb9b1-#cdcac4-#d2cfc9-#e3e2de'.split('-')
col1  = '#143642-#5d686f-#717c84-#7c858d-#8f959c-#9b9ea5-#a4a7ad-#acafb4-#b4b6bb-#bbbdc1'.split('-')
col5  = '#d05011-#cd5e27-#c96b3d-#c57853-#d6ae99-#be7f60-#cc9a82-#ca967d-#dab6a4-#e8d0c5'.split('-')
col4  = '#0b5d1e-#3c5e21-#545e22-#67662d-#7f7839-#796d37-#877c4b-#a19973-#bcb69b-#cac4af'.split('-')
col6  = '#ee6055-#d8604f-#c95540-#b8563d-#c56751-#cd7b68-#d28877-#dca395-#e6bdb4-#ebcac3'.split('-')
col8  = '#0f8b8d-#42817e-#538c8a-#649895-#76a3a1-#87afad-#98bab9-#a9c6c4-#bad1d0-#cbdddc'.split('-')
col3  = '#42253b-#52354b-#61455b-#71556b-#81657b-#90758a-#a0859a-#b095aa-#bfa5ba-#cfb5ca'.split('-')
col10 = '#ffb30f-#efa51a-#e8a12c-#e09c3e-#de9636-#dc902e-#e7bc85-#eecfa9-#f4e2cc-#f7ebde'.split('-')
col11 = '#800f2f-#a4133c-#b71643-#c9184a-#ff4d6d-#ff617e-#ff758f-#ff8fa3-#ffb3c1-#ffccd5'.split('-')
paleta = [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11]

#Pega cor pra cada subcategoria
colores_cat = {}
colores_sub = {}
for n in range(len(Categão['Categoria'])):
    N = 0
    try:
        colores_cat[Categão['Categoria'][n]]= paleta[n][N]
    except:
        colores_cat[Categão['Categoria'][n]]= paleta[n-1][N]
    # valor do incremento para as cores (se a lista tem 2 subs só pego as duas cores mais opostas)
    incremento = 9//(len(Cat_filtrada_total[Categão['Categoria'][n]]))

    for Subcat in Cat_filtrada_total[Categão['Categoria'][n]].keys():
        if Subcat not in colores_sub.keys() and Subcat != 'Total':
            N += incremento
            try:
                colores_sub[Subcat] = paleta[n][N]
            except:
                colores_sub[Subcat] = paleta[n-1][N]

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
subcat_chart = alt.Chart(Categão_mekk, height=350, width=695).transform_stack(
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
    x=alt.X('x1:Q', title='', axis=alt.Axis(labels=False, grid=False, ticks = False)),
    x2='x2:Q',
    y=alt.Y('y1:Q', title='', axis=alt.Axis(labels=False, grid=False, ticks = False)),
    y2='y2:Q',
    tooltip=['Categoria:N', 'subcategoria:N'],
    color = alt.Color('subcategoria:N', scale=alt.Scale(domain=list(colores_sub.keys()), range=list(colores_sub.values())), legend = None),opacity=alt.value(0.85),
    order = alt.Order('Categoria:Q', sort = 'ascending')
)
text2 = subcat_chart.mark_text(dx=0, dy=-8, align='left', fontSize=9).encode(
    text=alt.Text('subcategoria:N'), color = alt.condition(alt.datum.Quantidade_total > qtd_cat, alt.value('White'),  alt.value('')
))

subcat_chart2 = alt.layer(subcat_chart, text2)
cat_chart2 = alt.layer(cat_chart, text)
st.markdown('## Visão geral')
col1, col2 = st.beta_columns(2)
col1.markdown('### Mekko categorias e subcategorias')
col1.altair_chart(cat_chart2, use_container_width=True)
col1.altair_chart(subcat_chart2, use_container_width=True)

col1.write("### Download ")


DF = pd.DataFrame({})
for ref in Cat_full_filtrada:
    Semana = ref['referência']

    for categoria in ref['infos'].keys():
        record = {}
        record['Semana'] = Semana
        record['Categoria'] = categoria
        record['Qtd_categoria'] = ref['infos'][categoria]['Total']

        if categoria != 'Total':
            for subcategoria in ref['infos'][categoria].keys():
                if subcategoria != 'Total':
                    record[subcategoria] = ref['infos'][categoria][subcategoria]['Total']

        DF = pd.concat([DF, pd.DataFrame([record])], ignore_index=True).reset_index(drop=True)

DF = DF.fillna(0)
if st.button(' Download base em CSV'):
  tmp_download_link = download_link(DF, 'Categão.csv', 'Clique aqui para baixar os dados!')
  st.markdown(tmp_download_link, unsafe_allow_html=True)


area_cat = {'Referência': [], 'Categoria': [], 'Qtd': []}
for ele in Cat_full_filtrada:
    ref = ele['referência']
    for cat in ele['infos'].keys():
        area_cat['Referência'].append(ref)
        area_cat['Categoria'].append(cat)
        area_cat['Qtd'].append(ele['infos'][cat]['Total'])
area_cat = pd.DataFrame(area_cat)     

refs = area_cat['Referência'].drop_duplicates().reset_index(drop=True)
refs2 = {'ref':[], 'semana':[]}
for ref in refs:
    refs2['ref'].append(ref)
    refs2['semana'].append(str(ref)[2:]+" a "+str(ref+timedelta(days=6))[2:])
refs2 = pd.DataFrame(refs2)
area_cat = area_cat.merge(refs2, how='left', left_on='Referência', right_on='ref')

area_cat.Referência = pd.to_datetime(area_cat.Referência)
area_cat.Qtd = pd.to_numeric(area_cat.Qtd)

time_cat =alt.Chart(area_cat,height=450).mark_bar().encode(
    x=alt.X("semana", axis=alt.Axis(labelAngle = 30, labelFontSize=12)),
    y="Qtd:Q",
    color=alt.Color('Categoria:N', scale=alt.Scale(domain=list(colores_cat.keys()), range=list(colores_cat.values())), legend=alt.Legend(orient='right')),
                    opacity=alt.value(0.6),
    tooltip=['Categoria:N', 'Qtd:Q', 'semana']
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
refs = area_subcatcat['Referência'].drop_duplicates().reset_index(drop=True)
refs2 = {'ref':[], 'semana':[]}
for ref in refs:
    refs2['ref'].append(ref)
    refs2['semana'].append(str(ref)[2:]+" a "+str(ref+timedelta(days=6))[2:])
refs2 = pd.DataFrame(refs2)
area_subcatcat = area_subcatcat.merge(refs2, how='left', left_on='Referência', right_on='ref')
area_subcatcat= area_subcatcat.drop(columns = ['Referência', 'ref'])
total_sem = pd.DataFrame(area_subcatcat.groupby('semana')['Qtd'].sum())
area_subcatcat = area_subcatcat.merge(total_sem.rename(columns = {'Qtd': 'qtot'}), how='left', on = 'semana')
area_subcatcat['%'] = (area_subcatcat.Qtd/area_subcatcat.qtot*100).round(0)



# area_subcatcat.Referência = pd.to_datetime(area_subcatcat.Referência)
area_subcatcat.Qtd = pd.to_numeric(area_subcatcat.Qtd)


time_subcat = alt.Chart(area_subcatcat, title = 'Evolução temporal subcategorias da categoria '+Cat_select,width=800, height=500).mark_bar().encode(
    x=alt.X("semana", axis=alt.Axis(labelAngle = -30, labelFontSize=12)),
    y="Qtd:Q",
    color=alt.Color('Subcategoria:N', 
                            legend=alt.Legend(orient='right')),
                            opacity=alt.value(.9),
    tooltip=['Subcategoria:N', 'Qtd:Q', 'semana', '%']
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










