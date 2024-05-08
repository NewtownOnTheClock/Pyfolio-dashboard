import streamlit as st
from st_supabase_connection import SupabaseConnection
import datetime as dt
from utils import get_yfinance_latest, get_user, yfinance_info

conn = st.connection("supabase", type=SupabaseConnection)

if get_user() == "not connected":
    st.switch_page("main.py")


def upsert_to_user_data_db(data):
    conn.table("user_data").upsert(data).execute()


def add_new_holding_to_db(asset_name, date_acquired, number_acquired, total_cost):
    industry, sector = yfinance_info(asset_name)
    data = {
        "user_id": get_user(),
        "ticker": asset_name,
        "industry": industry,
        "sector": sector,
        "date_acquired": date_acquired,
        "number_acquired": number_acquired,
        "total_cost": total_cost,
    }

    return upsert_to_user_data_db(data=data)


st.title("New asset")

asset_adder = st.form("Add new asset to the portfolio", clear_on_submit=True)

with asset_adder:
    asset_val = st.text_input("Enter the ticker", placeholder="Enter a ticker... (i.e. AAPL)").upper()
    date_acquired_val = st.date_input("Select the date you aquired the asset").strftime("%Y-%m-%d")
    number_of_asset = st.number_input("Enter the how much are in holding", step=1)
    total_cost = st.number_input("Enter the total cost of the transaction", min_value=0.0000)

    if st.form_submit_button("Add"):
        if not get_yfinance_latest(asset_val, date_acquired_val).empty:
            add_new_holding_to_db(asset_name=asset_val, date_acquired=date_acquired_val, number_acquired=number_of_asset, total_cost=total_cost)
            st.toast("Asset added to your portfolio!")
        else:
            st.toast("Ticker unavailable, please try another one")

