import time

import yfinance as yf
import streamlit as st
import datetime as dt
from st_supabase_connection import SupabaseConnection

conn = st.connection("supabase", type=SupabaseConnection)


def get_yfinance_latest(ticker, start=None, end=None):
    try:
        df = yf.download(ticker, start=start, end=end)
    except Exception as e:
        return st.toast(f'Ticker {ticker} unavailable, please try a different one')
    else:
        return df


def get_user():
    try:
        id = conn.auth.get_user().user.id
    except Exception as e:
        return "not connected"
    else:
        return id


def yfinance_live(ticker):
        live_price = {}
        df = yf.download(tickers=ticker, period="1d", interval="1m")
        live = df.iloc[-1]["Adj Close"]
        return live


def yfinance_info(ticker):
    industry = yf.Ticker(ticker).info["industry"]
    sector = yf.Ticker(ticker).info["sector"]
    return industry, sector

@st.cache_resource
def yfinance_current(tickers: list[str]):
    current_prices = []
    prv_close_price = []
    for t in tickers:
        stock_info = yf.Ticker(t).info
        current_prices.append(yfinance_live(t))
        prv_close_price.append(stock_info["previousClose"])
    return current_prices, prv_close_price

@st.cache_resource
def yfinance_daily_chg(tickers: list[str]):
    pct_chg = []
    for t in tickers:
        stock_info = yf.Ticker(t).info
        pct_chg.append((yfinance_live(t) / stock_info["previousClose"]) -1)
    return pct_chg
