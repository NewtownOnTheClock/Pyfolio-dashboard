import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import plotly.express as px
from utils import get_yfinance_latest, get_user, yfinance_current, yfinance_daily_chg

conn = st.connection("supabase", type=SupabaseConnection)

if get_user() == "not connected":
    st.switch_page("main.py")


def query(user_id):
    rows = conn.query("*", table="user_data", ttl="5m").eq("user_id", user_id).execute()
    df = pd.DataFrame(rows.data)
    return df


def days_since_bought(date_bought):
    date_bought_setted = pd.to_datetime(date_bought)
    today = pd.to_datetime(dt.date.today())
    return (today - date_bought_setted).dt.days


def process_data(user_id):
    df = query(user_id).set_index("user_id")
    df["days_since_bought"] = days_since_bought(df["date_acquired"])
    df["weighted_days"] = df["days_since_bought"] * df["number_acquired"]

    summary = df.groupby(["ticker", "industry", "sector"], as_index=False).agg(
        total_cost=('total_cost', 'sum'),
        number_acquired=('number_acquired', 'sum'),
        total_weighted_days=('weighted_days', 'sum'),
    )
    summary["average_days_per_asset"] = summary["total_weighted_days"] / summary["number_acquired"]
    summary["average_cost_per_unit"] = summary["total_cost"] / summary["number_acquired"]
    summary["live_price"] = yfinance_current(summary["ticker"])[0]
    summary["unralized_p&l"] = (summary["live_price"] / summary["average_cost_per_unit"]) -1
    summary["previous_close"] = yfinance_current(summary["ticker"])[1]
    summary["daily_change"] = yfinance_daily_chg(summary["ticker"])

    return summary


def total_p_and_l(live_price, number_acquired, asset_cost):
    live_pft_value = (live_price * number_acquired).sum()
    pft_cost = asset_cost.sum()
    return round(live_pft_value - pft_cost,2)


def total_p_and_l_pct(live_price, number_acquired, asset_cost):
    live_pft_value = (live_price * number_acquired).sum()
    pft_cost = asset_cost.sum()
    return round(((live_pft_value / pft_cost) -1) * 100,2)


def daily_p_and_l(previous_close, number_acquired, live_price):
    live_pft_value = (live_price * number_acquired).sum()
    open_pft_value = (previous_close * number_acquired).sum()
    return round(live_pft_value - open_pft_value,2)


def daily_p_and_l_pct(previous_close, number_acquired, live_price):
    live_pft_value = (live_price * number_acquired).sum()
    open_pft_value = (previous_close * number_acquired).sum()
    return round((live_pft_value / open_pft_value) - 1,2)


st.title("Stock portfolio Dashboard")
user_id = get_user()
df_summary = process_data(user_id)
st.dataframe(df_summary, use_container_width=True, hide_index=True)


st.subheader("Portfolio Overview")
colm1, colm2, colm3 = st.columns((0.3, 0.3, 0.3))

colm1.metric(
    "Total portfolio P&L",
    value=f'{total_p_and_l(df_summary["live_price"],df_summary["number_acquired"], df_summary["total_cost"])}$',
    delta=f'{total_p_and_l_pct(df_summary["live_price"],df_summary["number_acquired"], df_summary["total_cost"])}%'
)

colm2.metric(
    "Daily portfolio P&L",
    value=f'{daily_p_and_l(df_summary["previous_close"],df_summary["number_acquired"], df_summary["live_price"])}$',
    delta=f'{daily_p_and_l_pct(df_summary["previous_close"],df_summary["number_acquired"], df_summary["live_price"])}%'
)

colm3.metric(
    "Total portfolio value",
    value=f'{round((df_summary["number_acquired"] * df_summary["live_price"]).sum(),2)}$',
)



st.subheader("Portfolio Allocation")
col1, col2, col3 = st.columns((0.4,0.2,0.4)) # pie chart column

fig_ticker = px.pie(df_summary, values="total_cost", names="ticker", hole=.3, title="Stock Allocation")
fig_ticker.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))

fig_indutry = px.pie(df_summary, values="total_cost", names="industry", hole=.3, title="Industry Allocation")
fig_indutry.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))

df_test = px.data.iris()

fig_p_l_asset = px.bar(df_summary, x="ticker", y="average_cost_per_unit",
             color='live_price', barmode='group', facet_col="live_price",
             height=400)

col1.plotly_chart(fig_ticker, use_container_width=True)
col3.plotly_chart(fig_indutry, use_container_width=True)
st.plotly_chart(fig_p_l_asset, use_container_width=True)


st.dataframe(df_test, use_container_width=True)
ig = px.bar(df_summary, x="live_price", y="average_cost_per_unit",
             color="ticker", barmode = 'group')
st.plotly_chart(ig, use_container_width=True)