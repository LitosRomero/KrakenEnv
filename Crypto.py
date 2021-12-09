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

#Format unixtime stamp to human readable date:
#import datetime
#date = datetime.datetime.fromtimestamp(1637107200.0)
#print(date.strftime('%Y-%m-%d %H:%M:%S'))



#Obtneiendo datos
fecha = datetime.datetime(2019, 12, 1)
f1 = time.mktime(fecha.timetuple()) #fecha inicio
inter=5  # 60*24*7
cryp='BTC' #criptomoneda
met='USDT' #metálico
monedas=cryp+met

#construyendo el df final
def call_Kraken(par="BTCUSDT", i=5, f_ini=1575158400.0): #60*24*7
  df= api.get_ohlc_data(pair=par,interval=i, since=f_ini)

  db=df[0]
  db['date'] = db.index
  db.sort_values("date", inplace=True)
#Calculando el Vwap
  db['avg_price'] = pd.DataFrame((db.low+db.close+db.high)/3)
  db['avg_PricexVol'] = (db.avg_price * db.volume)
  db['Cum_Avg_PricexVol'] = np.cumsum(db.avg_PricexVol)
  db['Cum_Vol'] = np.cumsum(db.volume)
  db['VWap_'] = db.Cum_Avg_PricexVol/db.Cum_Vol
  return db

#definiendo el df
data=call_Kraken(par=monedas)

#criptos y coins
cryptos=['BTC', 'ETH', 'USDT', 'SOL', 'ADA', 'USDC', 'XRP', 'DOT', 'DOGE',
         'SHIB', 'MATIC', 'WBTC', 'LTC', 'UNI', 'ALGO', 'LINK', 'TRX', 'BCH',
         'MANA', 'XLM', 'AXS', 'DAI', 'ATOM', 'FIL', 'ETC']
coins=['USDT','USD', 'EUR', 'GBP','CNY', 'INR', 'JPY', 'SAR']

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
    html.Div( # TÍTULOS
                children=[html.H1(children= "Visualizando Criptomonedas", className="header-title"),
                          html.P(children="Gráficos del comportamiento del precio y del "
                                            "volúmen de una criptomoneda al precio de otra"
                                            "en un gráfico de Velas y un VWap",
                          className="header-description", ), ],
                className="header", ),

    html.Div( [dcc.Checklist(id='toggle-rangeslider', value=['slider'] ), ] ), #CHEQUE

    html.Div(  #FILTROS
            children=[
                html.Div(  # DatePicker (Fechas)
                    children=[
                        html.Div(children="Rango de Fechas", className="menu-title"),
                                  dcc.DatePickerRange(id="rango-fecha",
                                                      min_date_allowed=data.date.min().date(),
                                                      max_date_allowed=data.date.max().date(), #yo la calculo
                                                      start_date=data.date.min().date(),
                                                      end_date=data.date.max().date(), ), ]),
                html.Div(#dropdown1
                    children=[
                        html.Div(children="Criptomoneda", className="menu-title"),
                                  dcc.Dropdown(id="filtro-crypto",
                                               options=[{"label": crypto1, "value": crypto1}
                                                         for crypto1 in cryptos ],
                                               value=cryp,
                                               clearable=False,
                                               placeholder="Selecione una Criptomoneda",
                                               className="dropdown",) ] ),
                html.Div(  # dropdown2
                    children=[
                        html.Div(children="Moneda", className="menu-title"),
                                  dcc.Dropdown(id="filtro-Moneda",
                                               options=[{"label": coin1, "value": coin1}
                                                          for coin1 in coins ],
                                               value=met,
                                               clearable=False,
                                               placeholder="Selecione una moneda",
                                               className="dropdown",) ] )
                     ], className="menu", ),

    html.Div(# GRÁFICO
        children=[html.Div(children=dcc.Graph(id="graph",  # grafica-precio
                                              config={"displayModeBar": False}, ),
                           className="card", ),
                  ], className="wrapper", )
])


# """

@app.callback(Output("graph", "figure"),
              [Input("filtro-crypto","value"),  #  Input("toggle-rangeslider", "value"),
               Input("filtro-Moneda","value"),
               Input("rango-fecha", "start_date"),
               Input("rango-fecha", "end_date")], )

def display_candlestick(crypto1, coin1, start_date, end_date):
    cryp=crypto1
    met=coin1
    data1 = call_Kraken(par=crypto1+coin1)  #, i=5, f_ini=1575158400.0)
    mask = ((data1.date >= start_date) & (data1.date <= end_date))
    filtered_data = data1.loc[mask, :]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # incluyendo el gráfico de velas con rangeselector
    fig.add_trace(go.Candlestick(
                                 x=filtered_data['date'],
                                 open=filtered_data['open'],
                                 high=filtered_data['high'],
                                 low=filtered_data['low'],
                                 close=filtered_data['close'],
                                 legendgroup=cryp+met,
                                 name=crypto1+" en "+coin1,
                                 ),
                  secondary_y=True
                  )

    # incluyendo el vwap calcualdo
    fig.add_trace(go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['VWap_'],
        line_color='#053061',
        legendgroup="VWap",
        name="VWap"
    ),
        secondary_y=False
    )

    # detalles de visualización
    fig.update_layout(title_text=f"{crypto1} en {coin1} desde {start_date} hasta {end_date}", height=600)
    fig.layout.yaxis2.showgrid = False
    fig.update_yaxes(rangemode='normal', scaleanchor='y', secondary_y=True)
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