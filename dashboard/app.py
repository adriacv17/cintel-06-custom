from pathlib import Path
import cufflinks as cf
import pandas as pd
import yfinance as yf
from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import output_ui
from shinywidgets import render_plotly
from shinyswatch import theme
from stocks import stocks
import plotly.graph_objects as go
from datetime import datetime
import plotly

# Default to the last 30 days
end = pd.Timestamp.now()
start = end - pd.Timedelta(days=30)

ui.page_opts(title="Adrian's Crypto Explorer", fillable=True)

theme.vapor()

# Implement a sidebar with inputs
with ui.sidebar():
    ui.input_selectize("crypto", "Select Crypto", choices=stocks, selected="ETH-USD")
    ui.input_date_range("dates", "Select Dates", start=start, end=end)
    

    ui.hr()

    ui.h6("Links:")

    ui.a(
        "GitHub Source",
        href="https://github.com/adriacv17/cintel-06-custom",
        target="_blank"
    )

    ui.a(
        "GitHub App",
        href="https://adriacv17.github.io/cintel-06-custom/",
        target="_blank"
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")

    ui.a("Market Data", href="https://finance.yahoo.com/crypto/?.tsrc-fin-srch",
         target="_blank")

with ui.layout_column_wrap(fill=False):
    with ui.value_box(
        showcase=icon_svg("dollar-sign"),
        theme="bg-gradient-green-red",
        ):
        "Current Price"

        @render.ui
        def price():
            close = get_data()["Close"]
            return f"{close.iloc[-1]:.2f}"

    with ui.value_box(
        showcase=output_ui("change_icon"),
        ):
        "Change"

        @render.ui
        def change():
            return f"${get_change():.2f}"


    with ui.value_box(
        showcase=icon_svg("percent"),
        theme="bg-gradient-green-red",):
        "Percent Change"

        @render.ui
        def change_percent():
            return f"{get_change_percent():.2f}%"
        
    with ui.value_box(
        showcase=icon_svg("user"),
        theme="bg-gradient-green-red",):
        "Volume"

        @render.ui
        def daily_volume():
            return f"{get_volume():.2f}"


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Price History and volume")

        @render_plotly
        def plot_history():
            crypto_data=get_data()
            name = input.crypto()
            colors= ['green' if row['Open']-row['Close'] >=0
                     else 'red' for index, row in crypto_data.iterrows()]

            fig =go.Figure()

            fig = plotly.subplots.make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.5,0.1,0.2,0.2])

            fig.add_trace(go.Candlestick(x=crypto_data.index,
                open=crypto_data['Open'], high=crypto_data['High'], low=crypto_data['Low'],
                close=crypto_data['Close'], name='Market Data'))
            
            fig.add_trace(go.Bar(x=crypto_data.index, y=crypto_data["Volume"],marker_color=colors),row=2, col=1)

            fig.update_layout(height=450, width=600, showlegend=False, title=str(name) +" Live Share Price:",template='plotly_dark', margin=dict(l=20, r=20, t=100, b=0))
            
            fig.update_xaxes(rangeslider_visible=False)

            fig.update_yaxes(title_text="Volume", row=2, col=1)

            fig.update_yaxes(title_text="Share Price", row=1, col=1)

            return fig


    with ui.card(full_screen=True):
        ui.card_header("Selected Crypto Historical DataTable")

        @render.data_frame
        def historical_data():
            y = get_data().reset_index().drop("Dividends", axis=1).drop("Stock Splits", axis=1)
            return y

@reactive.calc
def get_ticker():
    return yf.Ticker(input.crypto())


@reactive.calc
def get_data():
    dates = input.dates()
    return get_ticker().history(start=start, end=end)


@reactive.calc
def get_change():
    close = get_data()["Close"]
    return close.iloc[-1] - close.iloc[-2]


@reactive.calc
def get_change_percent():
    close = get_data()["Close"]
    change = close.iloc[-1] - close.iloc[-2]
    return change / close.iloc[-2] * 100

@reactive.calc
def get_volume():
    close=get_data()["Volume"]
    return close.iloc[0]

with ui.hold():

    @render.ui
    def change_icon():
        change = get_change()
        icon = icon_svg("arrow-up" if change >= 0 else "arrow-down")
        icon.add_class(f"text-{('success' if change >= 0 else 'danger')}")
        return icon