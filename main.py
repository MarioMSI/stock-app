from taipy.gui import Gui, download
import pandas as pd
import io

# Carga el CSV
df = pd.read_csv("./data/forecast.csv")

# Convierte la columna de fecha a datetime
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
df_2 = df.copy()


# Inicialización de variables
#variables hoja 1
stores = df['store'].unique().tolist()
store = 'StoreA'
category = categories = df['category'].unique().tolist()
start_date = df['date'].max() - pd.DateOffset(weeks = 3)
end_date = df['date'].max()
start_date_prev = start_date - pd.DateOffset(weeks = 1)
end_date_prev = end_date - pd.DateOffset(weeks = 1)

#Variables de a hoja 2
df_stock = pd.DataFrame()  # DataFrame vacío inicial para evitar errores
pivot_df = pd.DataFrame()  # DataFrame vacío para pivot_df
table_stock = None
store_2 = 'StoreA'
start_date_2 = df['date'].max() - pd.DateOffset(weeks = 3)
end_date_2 = df['date'].max()
start_date_prev_2 = start_date_2 - pd.DateOffset(weeks = 1)
end_date_prev_2 = end_date_2 - pd.DateOffset(weeks = 1)

# Definición de la interfaz de usuario
my_page = """
<|toggle|theme|>

<center>
<|navbar|>
</center>

<|25 75|layout|gap=60px|
<|sidebar|

### Store
<|{store}|selector|lov={stores}|dropdown|label = Select the Store|on_change=on_filter|>

### Category
<|{category}|selector|lov={categories}|multiple|label = Select the Category|on_change=on_filter|>

### Dates
<|{start_date}|date|on_change=on_filter|>
<|{end_date}|date|on_change=on_filter|>

### Download the prediction
<download_file|
<|{None}|file_download|on_action=on_download|label=Download|>
|download_file>
|>

<main_page|
# Stock **prediction**{: .color-primary} 📊

<|2 2 1|layout|gap=45px|

<|card|
### **Total**{: .color-primary} sales 
Actual week
<|{int(filtered_df["sales"].sum())}|text|class_name=h3|> 
|>

<|card|
### **Total**{: .color-primary} sales 
Previous week
<|{int(filtered_df_prev["sales"].sum())}|text|class_name=h3|> 

|>
|>
<br/>

<|Sales Table|expandable|not expanded|
<|{filtered_df}|table|page_size=5|>
|>

<|Charts|expandable|expanded=False|
<|layout|columns=1 1|gap=45px|
<|
### Sales by **day**{: .color-primary} 
<|{sales_by_day}|chart|x=date|y=sales|type=bar|title=Sales by Day|>
|>

<|
### Sales by **item**{: .color-primary} 
<|{sales_by_item}|chart|x=item|y=sales|type=bar|title=Sales by Item|>
|>
|>
|>

|main_page>
|>
"""

my_page_2 = """
<|toggle|theme|>

<center>
<|navbar|>
</center>


<|25 75|layout|gap=60px|
<|sidebar|

### Upload your stock
<|{table_stock}|file_selector|label=Select File|on_action=on_upload|extensions=.csv|drop_message=Drop Message|>

### Store
<|{store_2}|selector|lov={stores}|dropdown|label = Select the Store|on_change=on_filter_2|>

### Dates
<|{start_date_2}|date|on_change=on_filter_2|>
<|{end_date_2}|date|on_change=on_filter_2|>

### Calculate
<|Button Label|button|on_action=on_stocks_resume|>

### Download the prediction
<download_file|
<|{None}|file_download|on_action=on_download|label=Download|>
|download_file>
|>


<main_page|
# Stock **prediction**{: .color-primary} 📊

<|2 2 1|layout|gap=45px|

|>
<br/>

<|Sales Table|expandable|not expanded|
<|{filtered_df_2}|table|page_size=5|>
|>

<|Stock Table|expandable|not expanded|
<|{df_stock}|table|rebuild|page_size=5|>
|>

<|Resume table|expandable|not expanded|
<|{pivot_df}|table|rebuild|page_size=5|>
|>

|main_page>
|>
"""

pages = {
    'ppal' : my_page, 
    'other': my_page_2
}

#FUNTIONS FOR PAGE 1
# -------------------------------------------------------------------------------------------------------
def filter_data(store, category, start_date, end_date):

    start_date_prev = start_date - pd.DateOffset(weeks = 1)
    end_date_prev = end_date - pd.DateOffset(weeks = 1)

    filtered_df = df[df['store'] == store] 
    filtered_df = filtered_df[filtered_df['category'].isin(category)]
    filtered_df_prev = filtered_df[(filtered_df['date'] >= start_date_prev) & (filtered_df['date'] <= end_date_prev)]
    filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
    
    # SALES BY DAY BAR CHART
    sales_by_day = (
        filtered_df.groupby('date')['sales'].sum().reset_index()
    )

    #SALES BY ITEM
    sales_by_item = (
        filtered_df.groupby('item')['sales'].sum().reset_index()
        .sort_values(by='sales', ascending=False)  # Asumiendo que quieres ordenar descendientemente por ventas
    )   

    return filtered_df, filtered_df_prev, sales_by_day, sales_by_item

def on_filter(state):
    state.start_date = pd.to_datetime(state.start_date)
    state.end_date = pd.to_datetime(state.end_date)
    state.filtered_df, state.filtered_df_prev, state.sales_by_day, state.sales_by_item = filter_data(state.store, state.category, state.start_date, state.end_date)


def on_download(state):
    # Utiliza StringIO para crear un buffer de texto en memoria para el DataFrame
    buffer = io.StringIO()
    state.filtered_df.to_csv(buffer, index=False)
    buffer.seek(0)  # Vuelve al comienzo del buffer
    
    # Usa la función download de Taipy para permitir la descarga del CSV
    download(state, content=bytes(buffer.getvalue(), "UTF-8"), name="filtered_forecast.csv")

#FUNCTIONS FOR PAGE 2
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def on_upload(state):
    print('ok')
    state.df_stock = pd.read_csv(state.table_stock)
    return state.df_stock

def filtered_data_2(store_2, start_date_2, end_date_2):
    #Filtramos el df
    filtered_df_2 = df_2[df_2['store'] == store_2]
    filtered_df_2 = filtered_df_2[(filtered_df_2['date'] >= start_date_2) & (filtered_df_2['date'] <= end_date_2)]
    return filtered_df_2

def on_filter_2(state):
    state.start_date_2 = pd.to_datetime(state.start_date_2)
    state.end_date_2 = pd.to_datetime(state.end_date_2)
    state.filtered_df_2 = filtered_data_2(state.store_2, state.start_date_2, state.end_date_2)
'''
def create_stocks_resume(filtered_df_2, df_stock):
    #Creamos el pivot_df
    pivot_df = filtered_df_2.pivot_table(values='sales', index='item', columns='date', fill_value=0)
    # Agregar la columna 'Total' que es la suma de todas las ventas por fila
    pivot_df['Total'] = pivot_df.sum(axis=1)

    #Mergeamos el df_stock
    pivot_df = pivot_df.merge(df_stock, on = 'item')

    #Calculamos las unidades que hay que pedir
    pivot_df['Pedido'] = pivot_df['stock'] - pivot_df['Total']

    return pivot_df'''


def create_stocks_resume(filtered_df_2, df_stock):
    # Creamos el pivot_df
    pivot_df = filtered_df_2.pivot_table(values='sales', index='item', columns='date', fill_value=0)
    
    # Convertir los nombres de las columnas de fecha a string si son Timestamp
    pivot_df.columns = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in pivot_df.columns]
    
    # Agregar la columna 'Total' que es la suma de todas las ventas por fila
    pivot_df['Total'] = pivot_df.sum(axis=1)

    # Merge con df_stock
    pivot_df = pivot_df.merge(df_stock, on='item', how='left')
    pivot_df['Pedido'] =  pivot_df['Total'] - pivot_df['stock'] 

    return pivot_df

def on_stocks_resume(state):
    state.pivot_df = create_stocks_resume(state.filtered_df_2, state.df_stock)

# Ejecutar la GUI
if __name__ == "__main__":

    filtered_df, filtered_df_prev, sales_by_day, sales_by_item = filter_data(store, category, start_date, end_date)
    filtered_df_2 = filtered_data_2(store_2, start_date_2, end_date_2)

    stylekit_1 = {
        'color_primary' : '#3189CB',
        'color_secondary' : '#FF462B',
        'color_background_light' : '#D0EBE6',
        'color_background_dark' : '#6B6363',
        'color_paper_light' : '#AFE7DD',
        'color_paper_dark' : '#414141'
    }

    stylekit_2 = {
        'color_primary' : '#3189CB',
        'color_secondary' : '#FF462B',
        'color_background_light' : '#D8D8D8',
        'color_background_dark' : '#6B6363',
        'color_paper_light' : '#E8E8E8',
        'color_paper_dark' : '#414141'
    }

    #Gui(page=my_page).run(title="Inventary App", dev = True, stylekit=stylekit_2)
    Gui(pages=pages).run(title="Inventary App", use_reloader=True, stylekit=stylekit_2)

