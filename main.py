import pandas as pd
import streamlit as st
from st_supabase_connection import SupabaseConnection
import yfinance as yf
import datetime
from utils import get_user, yfinance_current, yfinance_daily_chg


# Initialize connection.
conn = st.connection("supabase", type=SupabaseConnection)


def yfinance_news():
    return yf.Tickers(["^GSPC"]).news()

def process_yf_news(news):
    for new in news["^GSPC"]:
        st.subheader(*[new["title"]])
        st.write(new["link"])
        st.write(f'Published at: {datetime.datetime.fromtimestamp(new["providerPublishTime"]).strftime("%Y-%m-%d %H:%m")}')
        if "thumbnail" in new:
            st.image(new["thumbnail"]["resolutions"][0]["url"])
        else:
            pass
        st.divider()
    return

def create_new_user(email, password, fname):
    try:
        conn.auth.sign_up(dict(email=email, password=password, options=dict(data=dict(fname=fname,attribution=''))))
    except Exception as e:
        st.error(e)
    else:
        st.toast("Account Created")


def sign_in(email, password):
    try:
        conn.auth.sign_in_with_password(dict(email=email, password=password))
    except Exception as e:
        st.error(e)
    else:
        st.toast("Connection established")
        st.switch_page("pages/dashboard.py")
    return


@st.experimental_dialog("Sign in / Log in")
def connect_user():
        log_in_tab, sign_up_tab = st.tabs(['Log in', 'Sign up'])
        with log_in_tab:
            with st.form("Log In_t", clear_on_submit=True, border=False):
                email = st.text_input("Email")
                password = st.text_input("Password", type='password')

                if st.form_submit_button("Log In_t"):
                    sign_in(email=email, password=password)

        with sign_up_tab:
            with st.form("Sign Up_t", clear_on_submit=True, border=False):
                email = st.text_input("Email")
                username = st.text_input("Username")
                password = st.text_input("Password", type='password')
                confirm_password = st.text_input("Confirm Password", type='password')

                if st.form_submit_button("Sign Up_t"):
                    if password == confirm_password:
                        create_new_user(email=email, password=password, fname=username)
                    else:
                        st.error("Make sure the password are the same")



# def sign_up_frontend():
#     user = get_user()
#     if user == "not connected":
#         with st.sidebar:
#             with st.popover("Sign Up", use_container_width=True):
#                 with st.form("Sign Up", clear_on_submit=True, border=False):
#                     email = st.text_input("Email")
#                     username = st.text_input("Username")
#                     password = st.text_input("Password", type='password')
#                     confirm_password = st.text_input("Confirm Password", type='password')
#
#                     if st.form_submit_button("Sign Up"):
#                         if password == confirm_password:
#                             create_new_user(email=email, password=password, fname=username)
#                         else:
#                             st.error("Make sure the password are the same")
#     else:
#         st.sidebar.write(f"Welcome {user}")
#         if st.sidebar.button("Logout"):
#             conn.auth.sign_out()
#             st.rerun()


def sign_in_frontend():
    with st.sidebar:
        with st.popover("Log In", use_container_width=True):
            with st.form("Log In", clear_on_submit=True, border=False):
                email = st.text_input("Email")
                password = st.text_input("Password", type='password')

                if st.form_submit_button("Log In"):
                    sign_in(email=email, password=password)


# def sidebar():
#     st.sidebar.title("Pyfolio Analyser")
#     col1, col2, col3 = st.columns((0.4,0.2,0.4))
#     #sign_up_frontend()
#     #sign_in_frontend()
#     if st.sidebar.button("Add stocks to you account"):
#         st.switch_page("pages/stock-input.py")


def frontpage_metrics(ticker):
    return f'{round(yfinance_current([ticker])[0][0],2)}$', f'{round(yfinance_daily_chg([ticker])[0] * 100,2)}%'



def main():
    # sidebar()
    header_col1, header_col2 = st.columns((0.8, 0.2))
    header_col1.title("Pyfolio Analyser")

    if get_user() == "not connected":
        if header_col2.button("Log in / Sign up", type="primary"):
            connect_user()
    else:
        if header_col2.button("Log ou_t", type="primary"):
            conn.auth.sign_out()
            st.rerun()


    col_sp, col_nasq, col_btc = st.columns((0.3,0.3,0.3))
    current_sp = frontpage_metrics("^GSPC")[0]
    daily_chng_sp = frontpage_metrics("^GSPC")[1]

    # Metric for the S&P 500
    col_sp.metric(
        "S&P 500",
        value=frontpage_metrics("^GSPC")[0],
        delta=frontpage_metrics("^GSPC")[1]
    )

    # Metric for the Nasdaq
    col_nasq.metric(
        "NASDAQ",
        value=frontpage_metrics("^IXIC")[0],
        delta=frontpage_metrics("^IXIC")[1]
    )

    # Metric for the bitcoin
    col_btc.metric(
        "Bitcoin-USD",
        value=frontpage_metrics("BTC-USD")[0],
        delta=frontpage_metrics("BTC-USD")[1]
    )

    if st.button("get session"):
        print(conn.auth.get_session().user.aud)

    if st.button("get user"):
        st.toast(conn.auth.get_user().user.id)

    if st.button("logout"):
        print(conn.auth.sign_out())

    process_yf_news(yfinance_news())


if __name__ == '__main__':
    main()