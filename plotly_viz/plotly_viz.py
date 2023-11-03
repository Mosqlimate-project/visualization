import pandas as pd
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from urllib.request import urlopen
import json
from plotly.subplots import make_subplots


def plot_heatmap_single(agravo = 'dengue'):
    """ Plot heatmap of incidence of a single disease

    :param agravo: Name of disease, defaults to 'dengue'
    :type agravo: str, optional
    :return: Plotly figure
    :rtype: plotly.graph_objects.Figure
    """
    
    # load the data
    df_end= pd.read_csv(f'../cases//data/{agravo}_br_2010-2022_quarter.csv')
    df_end.set_index('data_iniSE', inplace = True)
    df_end.index = pd.to_datetime(df_end.index)
    
    if agravo=='dengue':
        title = 'Dengue'
        color_scheme = [[0, "rgb(255, 255, 255)"], [0.25, "rgb(255, 218, 46)"], [0.75, "rgb(230, 0, 0)"], [1, "rgb(0, 0, 0)"]]

    if agravo == 'chik':
        title='Chikungunya'
        color_scheme = [[0, "rgb(255, 255, 255)"], [0.25, "rgb(255, 218, 46)"], [0.75, "rgb(230, 0, 0)"], [1, "rgb(0, 0, 0)"]]

    #multiply inc by 1000
    df_end['inc'] = df_end['inc']*100

    # create the figure
    fig = px.density_heatmap(df_end, x="trimestre-tick", 
                                y = "UF",
                                z="inc", 
                                color_continuous_scale=color_scheme, 
                                width=1100, height=800,
                                title = title,
                                labels = {'inc': 'Incidence'},
                                range_color=[0, 4],
                                )
    fig.update_yaxes(title = "Estados", 
                     categoryorder='array', 
                     categoryarray=df_end.sort_values('regiao')['UF'].unique(), 
    )
    
    fig.update_xaxes(title = "Trimestre")
    fig.update_traces(showscale=False)

    fig.update_layout(
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        
        updatemenus=[
            dict(
                type="buttons",
                direction="up",
                active=0,
                buttons=list([
                    dict(
                        args=[{"y": [df_end['UF']]},
                              {"title": title}],
                        label="Todos",
                        method="update",
                    ),
                    dict(
                        args=[{"y": [df_end[df_end.regiao == 'Sudeste']['UF']]},
                              {"title": title + " - Sudeste"}],
                        label="Sudeste",
                        method="update",
                    ),
                    dict(
                        args=[{"y": [df_end[df_end.regiao == 'Sul']['UF']]},
                              {"title": title + " - Sul"}],
                        label="Sul",
                        method="update",
                    ),
                    dict(
                        args=[{"y": [df_end[df_end.regiao == 'Nordeste']['UF']]},
                              {"title": title + " - Nordeste"}],
                        label="Nordeste",
                        method="update",
                    ),
                    dict(
                        args=[{"y": [df_end[df_end.regiao == 'Norte']['UF']]},
                              {"title": title + " - Norte"}],
                        label="Norte",
                        method="update",
                    ),
                    dict(
                        args=[{"y": [df_end[df_end.regiao == 'Centro-Oeste']['UF']]},
                              {"title": title + " - Centro-Oeste"}],
                        label="Centro-Oeste",
                        method="update",
                    ),
                ]),
            )

        ]
    )
    return fig

def plot_map(agravo = 'dengue'):
    """Plot map of incidence of a single disease

    :param agravo: Name of disease, defaults to 'dengue'
    :type agravo: str, optional
    :return: Plotly figure
    :rtype: plotly.graph_objects.Figure
    """

    with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
        Brazil = json.load(response) # Javascrip object notation 

    state_id_map = {}
    for feature in Brazil ['features']:
        feature['id'] = feature['properties']['sigla']
        state_id_map[feature['properties']['sigla']] = feature['id']

    df = pd.read_csv(f'../cases/data/{agravo}_br_2010-2022_quarter.csv')
    df.set_index('data_iniSE', inplace = True)
    df['inc'] = df['inc']*100

    fig = px.choropleth(
        df, #database
        locations = 'UF', #define the limits on the map/geography
        geojson = Brazil, #shape information
        color = "inc", #defining the color of the scale through the database
        hover_name = 'UF', #the information in the box
        color_continuous_scale = [[0, "rgb(255, 255, 255)"], [0.25, "rgb(255, 218, 46)"], [0.75, "rgb(230, 0, 0)"], [1, "rgb(0, 0, 0)"]], #color scale
        labels = {'inc': 'Incidence'}, #label of the scale
        animation_frame = 'trimestre-tick', #creating the application based on the year
        height=1000,
        range_color=[0, 4]
    )
    fig.update_geos(fitbounds = "locations", visible = False)
    
    return fig

def plot_forecasts(df, df_for):
    """Plot forecasts

    :param df: Dataframe with data values
    :type df: pandas.DataFrame
    :param df_for: Dataframe with forecasts
    :type df_for: pandas.DataFrame
    :return: Plotly figure
    :rtype: plotly.graph_objects.Figure
    """

    #Creating a figure with two subplots using FigureWidget
    sub = make_subplots(rows=1, cols=2)

    f = go.FigureWidget(sub)
    for model in df_for.model.unique(): 
        df_for_model = df_for[df_for.model == model]
        f.add_trace(go.Scatter(x=df_for_model.dates, y=df_for_model.predictions, mode='lines', name=model))

    default_linewidth = 2
    highlighted_linewidth_delta = 2

    def update_trace(trace, points, selector):
        """Update trace
        """

        # this list stores the points which were clicked on
        # in all but one trace they are empty
        m = dict()
        for model in df_for.model.unique():
            df_for_model = df_for[df_for.model == model]
            m[model] = df_for_model

        if len(points.point_inds) == 0:
            return
            
        for i,_ in enumerate(f.data):
            f.data[i]['line']['width'] = default_linewidth + highlighted_linewidth_delta * (i == points.trace_index)

        if len(f.data) > 6:
            f.data = f.data[:6]

        #redraw the clicked trace on the second subplot
        trace = points.trace_index
        model = f.data[trace].name
        df_for_model = m[model]
        x = m[model].dates.to_list()
        x_rev = x[::-1]

        y = m[model].predictions.to_list()
        y_upper = m[model].upper.to_list()
        y_lower = m[model].lower.to_list()
        y_rev = y[::-1]

        color_hex = f.data[trace]['line']['color'].replace('#','')
        color_rgba = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        color_rgba = 'rgba' + str(color_rgba).replace(')', ', 0.2)')

        f.add_trace(go.Scatter(
            name="var1",
            x=x+x_rev,
            y=y_upper,
            fill='none',
            fillcolor=color_rgba,
            line_color='rgba(255,255,255,0)',
            showlegend=False,
        ), row=1, col=2)

        f.add_trace(go.Scatter(
            name="var2",
            x = df_for.dates,
            y=y_lower,
            fillcolor=color_rgba,
            line_color='rgba(255,255,255,0)',
            fill='tonexty',
            showlegend=False,),  row=1, col=2)
        
        f.add_trace(go.Scatter(x=df_for_model.dates, 
                            y=df_for_model.predictions, 
                            mode='lines', 
                            line_color=f.data[trace]['line']['color'],
                            name=model, 
                            showlegend=False,), 
                                row=1, col=2)

    # we need to add the on_click event to each trace separately       
    for i in range( len(f.data) ):
        f.data[i].on_click(update_trace)

    f.add_trace(go.Scatter(x=df.dates, y=df.target,
                            mode='markers', 
                            marker={'color':'rgba(50,50,50,0.7)'},
                            name='Data'), row=1, col=1)
    f.add_trace(go.Scatter(x=df.dates, y=df.target, 
                        mode='markers',
                        name='Data',
                        marker={'color':'rgba(50,50,50,0.7)'},
                        showlegend=False), row=1, col=2)

    f.update_yaxes(range=[0, 3300])

    f.update_layout(title_text="Forecast",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',)

    return f