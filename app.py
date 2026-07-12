from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import plotly.express as px
from shiny import reactive
from shiny.express import render, input, ui, output
from shinywidgets import render_plotly

# db_all.csv file is available on zenodo repository of this work: https://zenodo.org/records/21105223
# keep the csv file and this file in the same directory
data = pd.read_csv('db_all.csv') 

data['year'] = data.date.apply(lambda x : int(x.split('-')[0]))

mapper = {'8':'Finite element analysis and numerical modelling',
'0':'Seismic and dynamic structural analysis',
'2':'Structural behaviour and connections',
'4':'Building information modelling and sustainable construction',
'5':'Structural elements and reinforced concrete design',
'6':'Composite structures and numerical modelling',
'3':'Corrosion, fatigue, and composite material damage',
'9':'Material durability and recycled concrete aggregates',
'1':'Cement and concrete materials science',
'7':'Asphalt and pavement engineering',
}

map_color = {7: '#b15928',0: '#ffff99',6: '#6a3d9a',4: '#ff7f00',5: '#fdbf6f',3: '#e31a1c',8: '#33a02c',1: '#b2df8a',9: '#1f78b4',2: '#a6cee3'}
data['labels']  = data.labels.astype(str)
data = data.rename(columns={'labels':'Topic'})
unique_topics = data["Topic"].unique()

ui.page_opts(fillable=True)
ui.HTML('<h1 style="color:blue;">Structural Engineering Research Navigator</h1>')

def update_data_with_patch(patch):
    df_copy = df().copy()
    fn = str if patch["column_index"] == 0 else int
    df_copy.iat[patch["row_index"], patch["column_index"]] = fn(patch["value"])
    df.set(df_copy)
    
@reactive.Calc
def filtered_data():
    # Get search string and field
    search_string = input.search_string().lower()

    sf = {'Abstract':"abstract", 'Title':"title","Keywords":'keywords'}
    if search_string:
        # Filter DataFrame based on the search
        mask = data[input.search_field()].str.contains(search_string, case=False, na=False)
        return data[mask]
    return data

with ui.layout_sidebar():
    with ui.sidebar():
        ui.input_text("search_string", "Enter search string:", "")
        ui.input_selectize(
        "search_field",
        "Search in:",
        ["abstract","title", "keywords"],
        selected="abstract",
        multiple=False,
        )
    @render_plotly
    def plot1():
        
        filtered = filtered_data()
            
        fig = px.scatter(
        filtered,
        x="x",
        y="y",
        color="Topic",  # Use 'topic' for the legend
        hover_data=["title", "doi", "topic", "year"],
        labels=mapper,)
        
        newnames = mapper
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],legendgroup = newnames[t.name],hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
   
        fig.update_traces(marker=dict(size=4, opacity=0.8))
        fig.update_layout(legend= {'itemsizing': 'constant'})
        fig.update_layout(legend=dict(title_font_family="Arial",
                              font=dict(size=20)))
        fig.update_layout(
                                font_family="Arial",
                                font_color="black",
                                legend_title_font_color="black"
                            )
        fig.update_layout(
                            xaxis=dict(
                            title=" ",  
                            linecolor="#BCCCDC",  # Sets color of Y-axis line
                            showgrid=True,  # Removes Y-axis grid lines  
                            zeroline = False, # thick line at x=0
                            showline = False, #removes Y-axis line
                            showticklabels=False, # axis ticklabels
                            visible = True,  # numbers below
                        ),
                            yaxis=dict(
                            title= "",  
                            linecolor="#BCCCDC",  # Sets color of Y-axis line
                            showgrid=True,  # Removes Y-axis grid lines  
                            zeroline = False, # thick line at x=0
                            showline = False, #removes Y-axis line
                            showticklabels=False, # axis ticklabels
                            visible = True,  # numbers below
                        )
                        )
        fig.update_layout(yaxis_range=[-4,10])
        fig.update_layout(xaxis_range=[-18,1.5])
        return fig
