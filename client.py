import json
import pandas as pd
import datetime as dt
from os import environ
from collections import deque

from binance.client import Client
from binance.enums import KLINE_INTERVAL_1MINUTE
from binance.websockets import BinanceSocketManager
from binance.exceptions import BinanceAPIException, BinanceOrderException

api_key = environ.get('BINANCE_API_KEY')
api_secret = environ.get('BINANCE_SECRET_KEY')
client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'

stream_cache = deque(maxlen=10)
price_df = {'BTCUSDT': pd.DataFrame(columns=['date', 'price']), 'error':False}

def main():

  # Init manager and start socket
  bsm = init_socket_manager()
  conn_key = bsm.start_kline_socket('BTCUSDT', process_message, interval=KLINE_INTERVAL_1MINUTE)
  bsm.start()

#   execute_order()
#   get_account_balance()


def get_account_balance():
  account_stats = client.get_account()
  print(json.dumps(account_stats))

def execute_order():
  try:
      limit_order = client.create_order(
          symbol='BTCUSDT',
          side='BUY',
          type='MARKET',
          quantity=0.01,
          newOrderRespType='FULL')
      print(limit_order)
  except BinanceAPIException as e:
      # error handling goes here
      print(e)
  except BinanceOrderException as e:
      # error handling goes here
      print(e)

def init_socket_manager():
  # if environ.get('BINANCE_API_KEY') or environ.get('BINANCE_SECRET_KEY') is None:
  #   raise Exception('Binance API credentials not set')
  return BinanceSocketManager(client)

def process_message(msg):
    if msg['e'] == 'error':
        # close and restart the socket
        print('Socket error')
        close_socket()
    else:
        print(convert_time(msg['k']['t']))
        filtered_msg = {}
        cols = {'Date': 't', 'Open': 'o', 'High': 'h',
            'Low': 'l', 'Close': 'c', 'Volume': 'v'}
        for key, value in cols.items():
            filtered_msg[key] = msg['k'][value]
        stream_cache.append(filtered_msg)
        price_df['BTCUSDT'].loc[len(price_df['BTCUSDT'])] = [pd.Timestamp.now(), float(msg['k']['c'])]
        print(price_df)

def convert_time(timestamp):
    return dt.datetime.fromtimestamp(int(timestamp)/1000)

def close_socket():
    bsm.stop_socket(conn_key)

main()