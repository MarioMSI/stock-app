from taipy.gui import Gui, download
import pandas as pd
import io

# Carga el CSV
df = pd.read_csv("./data/forecast.csv")

# Convierte la columna de fecha a datetime
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

# Inicialización de variables
stores = df['store'].unique().tolist()
store = 'StoreA'
category = categories = df['category'].unique().tolist()
start_date = df['date'].min() + pd.DateOffset(weeks = 1)
end_date = df['date'].max()
start_date_prev = start_date - pd.DateOffset(weeks = 1)
end_date_prev = end_date - pd.DateOffset(weeks = 1)

# Definición de la interfaz de usuario
my_page = """
<|toggle|theme|>

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

# Ejecutar la GUI
if __name__ == "__main__":

    filtered_df, filtered_df_prev, sales_by_day, sales_by_item = filter_data(store, category, start_date, end_date)

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

    Gui(page=my_page).run(title="Inventary App", dev = True, stylekit=stylekit_2)
