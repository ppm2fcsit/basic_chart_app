from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

def mychartapp(SB):
  # -*- coding: utf-8 -*-

  import os
  import sys
  import csv

  # -----------------------------------------------------------------------------

  import ccxt  # noqa: E402


  # -----------------------------------------------------------------------------

  def retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
      num_retries = 0
      try:
          num_retries += 1
          ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
          # print('Fetched', len(ohlcv), symbol, 'candles from', exchange.iso8601 (ohlcv[0][0]), 'to', exchange.iso8601 (ohlcv[-1][0]))
          return ohlcv
      except Exception:
          if num_retries > max_retries:
              raise  # Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')


  def scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
      timeframe_duration_in_seconds = exchange.parse_timeframe(timeframe)
      timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
      timedelta = limit * timeframe_duration_in_ms
      now = exchange.milliseconds()
      all_ohlcv = []
      fetch_since = since
      while fetch_since < now:
          ohlcv = retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, fetch_since, limit)
          fetch_since = (ohlcv[-1][0] + 1) if len(ohlcv) else (fetch_since + timedelta)
          all_ohlcv = all_ohlcv + ohlcv
          if len(all_ohlcv):
              print(len(all_ohlcv), 'candles in total from', exchange.iso8601(all_ohlcv[0][0]), 'to', exchange.iso8601(all_ohlcv[-1][0]))
          else:
              print(len(all_ohlcv), 'candles in total from', exchange.iso8601(fetch_since))
      return exchange.filter_by_since_limit(all_ohlcv, since, None, key=0)


  def write_to_csv(filename, data):
      with open(filename, mode='w') as output_file:
          csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
          csv_writer.writerows(data)


  def scrape_candles_to_csv(filename, exchange_id, max_retries, symbol, timeframe, since, limit):
      # instantiate the exchange by id
      exchange = getattr(ccxt, exchange_id)()
      # convert since from string to milliseconds integer if needed
      if isinstance(since, str):
          since = exchange.parse8601(since)
      # preload all markets from the exchange
      exchange.load_markets()
      # fetch all candles
      ohlcv = scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
      # save them to csv file
      write_to_csv(filename, ohlcv)
      print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', filename)


  # -----------------------------------------------------------------------------
  # Binance's BTC/USDT candles start on 2017-08-17
  scrape_candles_to_csv('binance.csv', 'binance', 3, SB, '1d', '2017-08-17T00:00:00Z', 100)

  import datetime
  import plotly.graph_objects as go
  import pandas as pd
  df = pd.read_csv('binance.csv', 
                          index_col=0,
                          parse_dates=[0],
                          header=None,
                          names=['Datetime','Open','High','Low','Close','Volume'],
                          date_parser=lambda x: datetime.datetime.utcfromtimestamp(int(x)/1000),
                              )
  #df.columns=['date','open','high','low','close','volume']
  df.reset_index(inplace=True)
  fig = go.Figure(data=go.Ohlc(x=df['Datetime'],
                      open=df['Open'],
                      high=df['High'],
                      low=df['Low'],
                      close=df['Close']))
  
  # Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

## add new app
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
  
  
