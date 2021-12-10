import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import krakenex
import time
from pykrakenapi import KrakenAPI
from dash import dcc
from dash import html
from dash.dependencies import Input, Output



# configurando api
k = krakenex.API()
# conectando con el api
api = KrakenAPI(k)

# Obtneiendo datos
fecha = datetime.datetime(2019, 12, 1)  # definimos esta fecha inicial para siempre poder ir al mayor tiempo
f1 = time.mktime(fecha.timetuple())  # atrás posible (720 intérvalos) y luego lo pasamos a unixtime
cryp = 'BTC'  # crypto
met = 'USDT'  # metálico
monedas = cryp + met
silder_etiqu = 1


# construyendo la función
def call_Kraken(par="BTCUSDT", i=5, f_ini=f1):
    df = api.get_ohlc_data(pair=par, interval=i, since=f_ini)

    db = df[0]  # la función get_ohlc_data retorna una tupla, con toda la información en la primera posición.
    db['date'] = db.index  # haciendo índices la columanda de fechas
    db['date'] = pd.to_datetime(db['date']).dt.date  # db['date'].date()
    db.sort_index(ascending=False)  # ordenando las fechas

    # Calculando el Vwap
    db['avg_price'] = pd.DataFrame((db.low + db.close + db.high) / 3)  # el promedio
    db['avg_PricexVol'] = (db.avg_price * db.volume)  # multiplicando el precio del intervalo x el volumen
    db['Cum_Avg_PricexVol'] = np.cumsum(db.avg_PricexVol)  # Acumulando las multiplicaciones (como un sumproduct)
    db['Cum_Vol'] = np.cumsum(db.volume)  # acumulando el volumen
    db['VWap_'] = db.Cum_Avg_PricexVol / db.Cum_Vol  # precip ponderado entre el volumen
    return db


# definiendo el df
data = call_Kraken(par=monedas)  # obteniendo los datos a usar

min_date_allowed1 = data.date.min(),
max_date_allowed1 = data.date.max(),
start_date1 = data.date.min(),  # start y end_date
end_date1 = data.date.max(),
data.head()

#criptos y coins
cryptos=['BTC', 'ETH', 'USDT', 'SOL', 'ADA', 'USDC', 'XRP', 'DOT', 'DOGE',
         'SHIB', 'MATIC', 'WBTC', 'LTC', 'UNI', 'ALGO', 'LINK', 'TRX', 'BCH',
         'MANA', 'XLM', 'AXS', 'DAI', 'ATOM', 'FIL', 'ETC']
coins=['USDT','USD', 'EUR', 'GBP', 'JPY']

# estilo
external_stylesheets = [{"href": "https://fonts.googleapis.com/css2?"
                                 "family=Lato:wght@400;700&display=swap",
                         "rel": "stylesheet",
                         }, ]

## datos intalación - inicio
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Análisis Cripto"
server = app.server


# da Dash
app.layout = html.Div(
    children=[
        html.Div(  # TÍTULOS
            children=[html.H1(children="Visualizando Criptomonedas", className="header-title"),
                      html.P(children="Gráficos del comportamiento del precio y del "
                                      "volúmen de una criptomoneda al precio de otra"
                                      "en un gráfico de Velas y un VWap.",
                             className="header-description",
                             ),
                      html.Div(  # slider para el largo de los elementos de la sesión
                          children=[
                              html.Div(children="Sesión", className="menu-title"),  # títulos del filtro
                              dcc.Slider(id='slider1',  # id dle filtro (necesario para el callback)
                                         min=0, max=8, step=None,  # configurando el slider
                                         marks={0: '1 minuto',  # predetermianndo opciones
                                                1: '5 minutos',  # para evitar inputs de datos
                                                2: '15 minutos',  # erróneos
                                                3: '30 minutos',
                                                4: '1 hora',
                                                5: '6 horas',
                                                6: '12 horas',
                                                7: '1 día',
                                                8: '1 semana'
                                                },
                                         value=silder_etiqu,  # esta variable se redefine en el callback
                                         className="rc-slider"
                                         ), ]), ],
            className="header", ),  # estas clases obtendrán formato con el css

        html.Div([dcc.Checklist(id='toggle-rangeslider', value=['slider']), ]),  # utilizando un rangeslider para
        # delimitar los datos a
        html.Div(  # FILTROS                                                          # visualizar sin filtrar o
            children=[  # modificar los datos
                # html.Div( # DatePicker (Fechas)
                # children=[
                # html.Div(children="Rango de Fechas", className="menu-title"),
                # dcc.DatePickerRange(id="rango-fecha", #filtro para las fechas
                # min_date_allowed=min_date_allowed1[0],
                # max_date_allowed=max_date_allowed1[0],
                # start_date= start_date1[0],       #start y end_date
                # end_date= end_date1[0]),         #se utilizan en
                # ], ),                                                 #el callback
                html.Div(  # dropdown1
                    children=[  # eligiendo el tipo de criptomonedas
                        html.Div(children="Criptomoneda", className="menu-title"),
                        dcc.Dropdown(id="filtro-crypto",
                                     options=[{"label": crypto1, "value": crypto1}
                                              for crypto1 in cryptos],  # utilizando la lista cryptos
                                     value=cryp,  # aquí redefinimos los datos
                                     clearable=False,  # nos aseguramos que no entren datos
                                     placeholder="Selecione una Criptomoneda",
                                     className="dropdown", )]),
                html.Div(  # dropdown2
                    children=[  # eligiendo monedas igual que el dropdown anterior
                        html.Div(children="Moneda", className="menu-title"),
                        dcc.Dropdown(id="filtro-Moneda",
                                     options=[{"label": coin1, "value": coin1}  # el value es el que
                                              for coin1 in coins],  # toma el callback
                                     value=met,
                                     clearable=False,
                                     placeholder="Selecione una moneda",
                                     className="dropdown", )])
            ], className="menu", ),  # ]),

        html.Div(  # Aquí posicionamos nuestro gráfico
            children=[html.Div(children=dcc.Graph(id="graph",  # graph será el Output
                                                  config={"displayModeBar": False}, ),
                               className="card", ),
                      ], className="wrapper", )
    ])


# aqui utiliza el callback y "da un refresh" a los datos. Realmente toma los inputs, hace las transformaciones
# de la función de abajo (display_candlestick())
@app.callback(Output("graph", "figure"),
              [Input("slider1", "value"),
               Input("filtro-crypto", "value"),
               Input("filtro-Moneda", "value"),
               # Input("rango-fecha", "start_date"),
               # Input("rango-fecha", "end_date"),
               Input("toggle-rangeslider", "value"),
               ], )
# , start_date, end_date,f1):
def display_candlestick(intervalo, crypto1, coin1, v1):  # s_date1,e_date1#utilizamos los inputs como argumentos

    silder_etiqu = intervalo  # gestinamos el primer input
    if silder_etiqu == 0:  # damos un intérvalos a los elementos d ela sesión
        tiempos = 1  # de acuerdo con lo que seleccionó el usuario
    elif silder_etiqu == 1:
        tiempos = 5
    elif silder_etiqu == 2:
        tiempos = 15
    elif silder_etiqu == 3:
        tiempos = 30
    elif silder_etiqu == 4:
        tiempos = 60
    elif silder_etiqu == 5:
        tiempos = 6 * 60
    elif silder_etiqu == 6:
        tiempos = 60 * 12
    elif silder_etiqu == 7:
        tiempos = 60 * 24
    elif silder_etiqu == 8:
        tiempos = 60 * 24 * 7
    else:
        tiempos = 5

    cryp = crypto1  # tomamos la criptomoneda
    met = coin1  # y moneda seleccionadas

    data1 = call_Kraken(par=crypto1 + coin1, i=tiempos)  # volvemos a llamar datos para actualizar el dashbaord

    min_date1 = data1.date.min()  # redefinimos la fecha mínima y máxima, de inicio y fin
    max_date1 = data1.date.max()
    # fe1 =s_date1
    # fe2 =e_date1
    # mask = ( >= fe1 )
    #        &(pd.to_datetime(data1['date']).dt.date <= fe2 )) #hacemos una máscara para filtrar los datos
    filtered_data = data1  # .loc[mask, :]     #Obtenemos el nuevo dataset

    fig = make_subplots(specs=[[{"secondary_y": True}]])  # definimos el tipo de plot a hacer (en este caso)
    # subplots para Graficar el VWAP junto con el par

    # incluyendo el gráfico de velas con rangeselector y obtendiendo datos de filtered_data
    fig.add_trace(go.Candlestick(
        x=filtered_data.index,
        open=filtered_data['open'],
        high=filtered_data['high'],
        low=filtered_data['low'],
        close=filtered_data['close'],
        legendgroup=cryp + met,
        name=crypto1 + " en " + coin1,
    ),
        secondary_y=True  # esta línea nos permite  eje
    )

    # incluyendo el vwap calcualdo en el mísmo gráfico de velas y obtendiendo datos de filtered_data
    fig.add_trace(go.Scatter(
        x=filtered_data.index,
        y=filtered_data['VWap_'],
        line_color='#053061',  # le damos otro color
        legendgroup="VWap",
        name="VWap"
    ),
        secondary_y=False
    )

    # detalles de visualización, ponerle
    fig.update_layout(title_text=f"{crypto1} en {coin1} desde {min_date1} hasta {max_date1}", height=600)
    fig.layout.yaxis2.showgrid = False
    fig.update_yaxes(rangemode='normal', scaleanchor='y')  # , secondary_y=True)
    fig.update_yaxes(matches='y')
    fig.update_layout(legend=dict(orientation="h",
                                  title="Haga doble click en una variable para aislarla:",
                                  yanchor="bottom",
                                  y=1,
                                  xanchor="right",
                                  x=1))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)