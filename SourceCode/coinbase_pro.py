#!/usr/bin/env python3
"""Functions to use with Coinbase Pro"""
#
# Python Script:: coinbase_pro.py
#
# Linter:: pylint
#
# Copyright 2021, Matthew Ahrenstein, All Rights Reserved.
#
# Maintainers:
# - Matthew Ahrenstein: matt@ahrenstein.com
#
# See LICENSE
#

import base64
import datetime
import json
import time
import hmac
import hashlib
import requests
from requests.auth import AuthBase

API_URL = 'https://api.pro.coinbase.com/'
# API_URL = 'https://api-public.sandbox.pro.coinbase.com/'


# Create custom authentication for CoinbasePro
# as per https://docs.pro.coinbase.com/?python#creating-a-request
class CoinbaseProAuth(AuthBase):
    """
        Coinbase Pro provided authentication method with minor fixes
        """
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        try:
            message = timestamp + request.method + request.path_url + (request.body or b'').decode()
        except:
            message = timestamp + request.method + request.path_url + (request.body or b'')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


def get_cbpro_creds_from_file(credentials_file: str) -> [str, str, str]:
    """Open a JSON file and get Coinbase Pro credentials out of it
    Args:
        credentials_file: A JSON file containing Coinbase Pro credentials

    Returns:
        cbpro_api_key: An API key for Coinbase Pro
        cbpro_api_secret: An API secret for Coinbase Pro
        cbpro_api_passphrase: An API passphrase for Coinbase Pro
    """
    with open(credentials_file) as creds_file:
        data = json.load(creds_file)
    cbpro_api_key = data['coinbase']['api_key']
    cbpro_api_secret = data['coinbase']['api_secret']
    cbpro_api_passphrase = data['coinbase']['passphrase']
    return cbpro_api_key, cbpro_api_secret, cbpro_api_passphrase


def clear_to_proceed(credentials_file: str) -> bool:
    """Check if there are any open Coinbase Pro orders in the last 1000 hours
    Args:
        credentials_file: A JSON file containing Coinbase Pro credentials

    Returns:
        all_clear: A bool that returns true if there are no open orders
    """
    # Instantiate Coinbase API and query the price
    coinbase_creds = get_cbpro_creds_from_file(credentials_file)
    timestamp = (datetime.datetime.utcnow() - datetime.timedelta(hours=1000)).isoformat()
    coinbase_auth = CoinbaseProAuth(coinbase_creds[0], coinbase_creds[1], coinbase_creds[2])
    open_api_query = 'orders?status=open&before=%s' % timestamp
    open_result = json.dumps(requests.get(API_URL +
                                          open_api_query, auth=coinbase_auth).json(), indent=2)
    pending_api_query = 'orders?status=pending&before=%s' % timestamp
    pending_result = json.dumps(requests.get(API_URL
                                             + pending_api_query,
                                             auth=coinbase_auth).json(), indent=2)
    active_api_query = 'orders?status=active&before=%s' % timestamp
    active_result = json.dumps(requests.get(API_URL +
                                            active_api_query, auth=coinbase_auth).json(), indent=2)
    # Check open orders
    if open_result == "[]":
        print("LOG: No open orders detected.")
    else:
        print("LOG: Open orders detected.")
        print("LOG: Reason: %s" % open_result)
        return False

    # Check pending orders
    if pending_result == "[]":
        print("LOG: No pending orders detected.")
    else:
        print("LOG: Pending orders detected.")
        print("LOG: Reason: %s" % pending_result)
        return False
    # Check active orders
    if active_result == "[]":
        print("LOG: No active orders detected.")
    else:
        print("LOG: Active orders detected.")
        print("LOG: Reason: %s" % active_result)
        return False
    return True


def buy_coin(credentials_file: str, coin: str, trade_size: float) -> bool:
    """
    Conduct a trade on Coinbase Pro to trade a coin with USD

    Args:
        credentials_file: A JSON file containing Coinbase Pro credentials
        coin: The coin requested
        trade_size: The dollar value of the trade

    Returns:
        trade_success: A bool that is true if the trade succeeded
    """
    trade_success = False
    coinbase_creds = get_cbpro_creds_from_file(credentials_file)
    # Instantiate Coinbase API and query the price
    coinbase_auth = CoinbaseProAuth(coinbase_creds[0], coinbase_creds[1], coinbase_creds[2])
    buy_query = 'orders'
    order_config = json.dumps({'type': 'market',
                               'funds': trade_size, 'side': 'buy', 'product_id': '%s-USD' % coin})
    buy_result = requests.post(API_URL + buy_query, data=order_config, auth=coinbase_auth).json()
    if 'message' in buy_result:
        print("LOG: Buy order failed. Ending cycle....")
        print("LOG: Reason: %s" % buy_result['message'])
        trade_success = False
    else:
        print("LOG: Buy order succeeded.")
        print("LOG: Buy Results: %s" % json.dumps(buy_result, indent=2))
        trade_success = True
    return trade_success


def get_coin_price(credentials_file: str, coin: str) -> float:
    """
    Get the USD price of a coin from Coinbase Pro

    Args:
        credentials_file: A JSON file containing Coinbase Pro credentials
        coin: The coin requested

    Returns:
        coin_price: The price the coin currently holds in USD
    """
    # Instantiate Coinbase API and query the price
    coinbase_creds = get_cbpro_creds_from_file(credentials_file)
    coinbase_auth = CoinbaseProAuth(coinbase_creds[0], coinbase_creds[1], coinbase_creds[2])
    api_query = "products/%s-USD/ticker" % coin
    result = requests.get(API_URL + api_query, auth=coinbase_auth)
    coin_price = float(result.json()['price'])
    return coin_price


def get_coin_total(credentials_file: str, coin: str) -> float:
    """
    Get the current total amount of your coin

    Args:
        credentials_file: A JSON file containing Coinbase Pro credentials
        coin: The coin requested

    Returns:
        coin_total: The total amount of the coin you hold in your account
    """
    # Instantiate Coinbase API and query the price
    coin_total = 0
    coinbase_creds = get_cbpro_creds_from_file(credentials_file)
    coinbase_auth = CoinbaseProAuth(coinbase_creds[0], coinbase_creds[1], coinbase_creds[2])
    api_query = "accounts"
    result = requests.get(API_URL + api_query, auth=coinbase_auth).json()
    for account in result:
        if account['currency'] == coin:
            coin_total = float(account['balance'])
    return coin_total


def sell_coin(credentials_file: str, coin: str, coin_price: float, coin_count: float) -> bool:
    """
    Conduct a trade on Coinbase Pro to sell X-USD

    Args:
        credentials_file: A JSON file containing Coinbase Pro credentials
        coin: The coin requested
        coin_price: The current price of the coin
        coin_count: How much of the coin is held

    Returns:
        trade_status: A bool that is true if the trade succeeded
    """
    trade_success = False
    coinbase_creds = get_cbpro_creds_from_file(credentials_file)
    # Instantiate Coinbase API and query the price
    coinbase_auth = CoinbaseProAuth(coinbase_creds[0], coinbase_creds[1], coinbase_creds[2])
    buy_query = 'orders'
    # Set the stop loss to a loss of 7% and take profit to a gain of 10%
    # stop_loss = round(coin_price - (coin_price * 7) / 100, 2)
    take_profit = round(coin_price + (coin_price * 10) / 100, 2)
    order_config = json.dumps({'type': 'limit', 'size': coin_count, 'side': 'sell',
                               'product_id': '%s-USD' % coin, 'price': take_profit})
    # 'stop': 'loss', 'stop_price': stop_loss})
    sell_result = requests.post(API_URL + buy_query, data=order_config, auth=coinbase_auth).json()
    if 'message' in sell_result:
        print("LOG: Sell order failed. Ending cycle....")
        print("LOG: Reason: %s" % sell_result['message'])
        trade_success = False
    else:
        print("LOG: Sell order succeeded. Continuing cycle....")
        print("LOG: Sell Results: %s" % json.dumps(sell_result, indent=2))
        trade_success = True
    return trade_success


def engage_trade(credentials_file: str, coin: str, trade_size: float):
    """
    Conduct trades on Coinbase Pro to buy a coin for USD and trigger a sell order

    Args:
        credentials_file: A JSON file containing Coinbase Pro credentials
        coin: The coin requested
        trade_size: The dollar value of the trade
    Returns:
        trade_status: A bool that is true if the trade succeeded
    """
    clear_to_start = clear_to_proceed(credentials_file)
    coin_total = get_coin_total(credentials_file, coin)
    clear_to_sell = False
    if (clear_to_start is True) and (coin_total <= 0.001):
        clear_to_sell = buy_coin(credentials_file, coin, trade_size)
    else:
        print("LOG: Buy order restricted. Ending cycle....")
        print("LOG: Current %s balance is %s" % (coin, coin_total))
    if clear_to_sell is True:
        print("LOG: Sleeping 10 seconds before attempting to sell...")
        time.sleep(10)
        coin_current_price = get_coin_price(credentials_file, coin)
        coin_total = get_coin_total(credentials_file, coin)
        sell_coin(credentials_file, coin, coin_current_price, coin_total)
    else:
        print("LOG: Sell order restricted. Ending cycle....")
