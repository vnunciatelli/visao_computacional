# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.graph_objs as go
# import psycopg2
# import pandas as pd
# from datetime import datetime, timedelta

# # Conectar ao banco de dados PostgreSQL
# conn = psycopg2.connect(
#     dbname='Vision',
#     user='postgres',
#     password="2Smx'P?8[#RA\#9Z",
#     host='192.168.210.40',
#     port='5432'
# )

# # Definir a consulta SQL para selecionar os dados no intervalo de datas especificado
# query = """
#     SELECT data::date as data, sum(qtd_person::integer) as qtd_person
#     FROM (
#         SELECT datahora::date as data, qtd_person
#         FROM headcount
#         WHERE datahora >= '2024-03-25'
#     ) subquery
#     GROUP BY data
#     ORDER BY data
# """

# # Executar a consulta SQL e carregar os resultados em um DataFrame pandas
# df = pd.read_sql_query(query, conn)

# # Fechar a conexão com o banco de dados
# conn.close()

# # Criar o aplicativo Dash
# app = dash.Dash(__name__)

# # Layout do aplicativo Dash
# app.layout = html.Div(className='container', style={'backgroundColor': '#ffffff', 'color': '#000000'}, children=[
#     html.H1('Quantidade de Pessoas Detectadas', className='title', style={'textAlign': 'center'}),
#     html.Img(src=r'C:\Users\ronaldo.pereira\Downloads\logoeletro.png', style={'width': '150px', 'height': 'auto', 'margin-left': '20px', 'margin-top': '20px'}),
#     dcc.DatePickerRange(
#         id='date-picker-range',
#         start_date=(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
#         end_date=datetime.now().strftime('%Y-%m-%d'),
#         className='date-picker'
#     ),
#     dcc.Graph(id='bar-chart', style={'backgroundColor': '#ffffff'}),
#     dcc.Graph(id='pie-chart', style={'backgroundColor': '#ffffff'}),
#     html.Div(id='total-people', className='total-people', style={'textAlign': 'center'})
# ])

# # Callback para atualizar os gráficos com base na seleção de datas
# @app.callback(
#     [Output('bar-chart', 'figure'),
#      Output('pie-chart', 'figure'),
#      Output('total-people', 'children')],
#     [Input('date-picker-range', 'start_date'),
#      Input('date-picker-range', 'end_date')]
# )
# def update_charts(start_date, end_date):
#     # Converter as strings de data para objetos datetime
#     start_date = datetime.strptime(start_date, '%Y-%m-%d')
#     end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
#     # Garantir que o intervalo de datas selecionado inclua exatamente 7 dias
#     if (end_date - start_date).days != 7:
#         start_date = end_date - timedelta(days=7)
    
#     start_date_str = start_date.strftime('%Y-%m-%d')
#     end_date_str = end_date.strftime('%Y-%m-%d')
    
#     filtered_df = df[(df['data'] >= start_date.date()) & (df['data'] <= end_date.date())]
    
#     # Gráfico de barras
#     trace_bar = go.Bar(
#         x=filtered_df['data'],
#         y=filtered_df['qtd_person'],
#         text=filtered_df['qtd_person'],
#         textposition='outside',
#         marker=dict(color='#8B008B')  # Cor lilás
#     )

#     layout_bar = go.Layout(
#         plot_bgcolor='#ffffff',  # Cor de fundo do gráfico
#         paper_bgcolor='#ffffff',  # Cor de fundo do papel
#         xaxis=dict(title='Data', color='#000000', showgrid=False, tickformat='%d/%m/%Y', tickangle=-45 ),  # Cor do texto e grade do eixo x
#         yaxis=dict(title='Quantidade de Pessoas Detectadas', color='#000000'),  # Cor do texto do eixo y
#         font=dict(color='#000000'),  # Cor do texto
#         margin=dict(t=50, l=50, r=50, b=50),  # Margens do gráfico
#     )

#     fig_bar = go.Figure(data=[trace_bar], layout=layout_bar)
    
#     # Gráfico de pizza
#     total_people = filtered_df['qtd_person'].sum()
#     if total_people == 0:
#         detection_percentage = 0
#     else:
#         detection_percentage = (len(filtered_df) / len(df)) * 100
    
#     trace_pie = go.Pie(
#         labels=['Detecção', 'Sem Detecção'],
#         values=[detection_percentage, 100 - detection_percentage],
#         hole=0.5,
#         marker=dict(colors=['#ff7f0e', '#d62728']),  # Cores das fatias
#         hoverinfo='label+percent'
#     )

#     layout_pie = go.Layout(
#         title='Porcentagem de Detecção',
#         plot_bgcolor='#ffffff',  # Cor de fundo do gráfico
#         paper_bgcolor='#ffffff',  # Cor de fundo do papel
#         font=dict(color='#000000'),  # Cor do texto
#     )

#     fig_pie = go.Figure(data=[trace_pie], layout=layout_pie)
    
#     # Total de pessoas detectadas
#     total_people_div = html.H2(f'Total de Pessoas Detectadas: {total_people}', style={'color': '#000000'})

#     return fig_bar, fig_pie, total_people_div


# # Executar o aplicativo Dash
# if __name__ == '__main__':
#     app.run_server(debug=True)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

# Conectar ao banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname='Vision',
    user='postgres',
    password="2Smx'P?8[#RA\#9Z",
    host='192.168.210.40',
    port='5432'
)

# Definir a consulta SQL para selecionar os dados no intervalo de datas especificado
query = """
    SELECT data::date as data, sum(qtd_person::integer) as qtd_person
    FROM (
        SELECT datahora::date as data, qtd_person
        FROM headcount
        WHERE datahora >= '2024-03-25'
    ) subquery
    GROUP BY data
    ORDER BY data
"""

# Executar a consulta SQL e carregar os resultados em um DataFrame pandas
df = pd.read_sql_query(query, conn)

# Fechar a conexão com o banco de dados
conn.close()

# Criar o aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout do aplicativo Dash
app.layout = html.Div(className='container-fluid', style={'backgroundColor': '#ffffff', 'width': '100%' ,'height': '100%', 'color': '#000000'}, children=[
    dbc.Card([
        dbc.CardBody([
            html.Div(className='header', children=[
                html.Img(src=r'data:image/png;base64,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', style={'width': '200px', 'height': 'auto'}),
                html.H1('DASHBOARD VISÃO COMPUTACIONAL', className='title'),
            ]),
            html.Hr(),  # Adiciona uma linha horizontal para separar o cabeçalho do conteúdo principal
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                className='date-picker'
            ),
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(id='bar-chart', style={'height': '500px', 'margin-top': '5px'}), 
                            width=12
                        )
                    ])
                ])
            ], style={'margin': '20px', 'border': '1px solid' }),
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(id='pie-chart', style={'height': '400px'}), 
                            width=6
                        ),
                        dbc.Col(
                            html.Div(id='total-people', className='total-people', style={'textAlign': 'center'}), 
                            width=6
                        )
                    ])
                ])
            ], style={'margin': '20px', 'border': '1px solid' })
        ])
    ], style={'margin': '20px', 'border': '1px solid'})
])

# Callback para atualizar os gráficos com base na seleção de datas
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('total-people', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_charts(start_date, end_date):
    # Converter as strings de data para objetos datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Garantir que o intervalo de datas selecionado inclua exatamente 7 dias
    if (end_date - start_date).days != 6:
        start_date = end_date - timedelta(days=7)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    filtered_df = df[(df['data'] >= start_date.date()) & (df['data'] <= end_date.date())]
    
    # Gráfico de barras
    trace_bar = go.Bar(
        x=filtered_df['data'],
        y=filtered_df['qtd_person'],
        text=filtered_df['qtd_person'],
        textposition='outside',
        marker=dict(color='#8B008B')  # Cor lilás
    )

    layout_bar = go.Layout(
        plot_bgcolor='#ffffff',  # Cor de fundo do gráfico
        paper_bgcolor='#ffffff',  # Cor de fundo do papel
        xaxis=dict(title='Data', color='#000000', showgrid=False, tickformat='%d/%m/%Y', tickangle=-45),  # Cor do texto e grade do eixo x
        yaxis=dict(title='Quantidade de Pessoas Detectadas', color='#000000'),  # Cor do texto do eixo y
        font=dict(color='#000000'),  # Cor do texto
        margin=dict(t=50, l=50, r=50, b=50),  # Margens do gráfico
    )

    fig_bar = go.Figure(data=[trace_bar], layout=layout_bar)
    
    # Gráfico de pizza
    total_people = filtered_df['qtd_person'].sum()
    if total_people == 0:
        detection_percentage = 0
    else:
        detection_percentage = (len(filtered_df) / len(df)) * 100
    
    trace_pie = go.Pie(
        labels=['Detecção', 'Sem Detecção'],
        values=[detection_percentage, 100 - detection_percentage],
        hole=0.5,
        marker=dict(colors=['#ff7f0e', '#d62728']),  # Cores das fatias
        hoverinfo='label+percent'
    )

    layout_pie = go.Layout(
        title='Porcentagem de Detecção',
        plot_bgcolor='#ffffff',  # Cor de fundo do gráfico
        paper_bgcolor='#ffffff',  # Cor de fundo do papel
        font=dict(color='#000000'),  # Cor do texto
    )

    fig_pie = go.Figure(data=[trace_pie], layout=layout_pie)
    
    # Total de pessoas detectadas
    total_people_div = html.H2(f'Total de Pessoas Detectadas: {total_people}', style={'color': '#000000'})

    return fig_bar, fig_pie, total_people_div


# Executar o aplicativo Dash
if __name__ == '__main__':    app.run_server(debug=True)