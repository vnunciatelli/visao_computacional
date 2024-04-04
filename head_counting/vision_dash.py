import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Carregar os dados do CSV para um DataFrame
vision = pd.read_csv(r"C:\Users\ronaldo.pereira\Downloads\vision_table (2).csv")

# Converter a coluna 'data_hora' para o tipo datetime
vision['data_hora'] = pd.to_datetime(vision['data_hora'])

# Dividir a coluna 'data_hora' em duas colunas de data e hora
vision['data'] = vision['data_hora'].dt.date
vision['hora'] = vision['data_hora'].dt.time

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)

# Layout do dashboard
app.layout = html.Div([
    html.H1("Visão Computacional - Dashboard Interativo"),
    
    dcc.Graph(id='graph'),

    # Adicionar filtros interativos
    html.Div([
        html.Label('Escolha o intervalo de datas e horários:'),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=vision['data_hora'].min(),
            end_date=vision['data_hora'].max(),
            display_format='YYYY-MM-DD HH:mm:ss',  # Inclui a hora na exibição
        ),
    ], style={'margin-top': '20px'}),

    # Exibir a quantidade de pessoas detectadas
    html.Div(id='total-detected', style={'margin-top': '20px', 'font-size': '20px'})
])

# Callback para atualizar o gráfico e a quantidade total de pessoas detectadas com base no intervalo de datas selecionado
@app.callback(
    [Output('graph', 'figure'),
     Output('total-detected', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(start_date, end_date):
    filtered_data = vision[(vision['data_hora'] >= start_date) & (vision['data_hora'] <= end_date)]
    total_detected = filtered_data['qtd_pessoas_detectadas'].sum()
    fig = px.line(filtered_data, x='data_hora', y='qtd_pessoas_detectadas', title='Quantidade de Pessoas Detectadas ao Longo do Tempo')
    return fig, f"Total de Pessoas Detectadas: {total_detected}"

# Executar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)