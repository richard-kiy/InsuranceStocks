from yahooquery import Ticker
import pandas as pd
from dash import dcc, html, clientside_callback, dash_table, ctx, no_update
from datetime import date
import math

# from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

import dash_mantine_components as dmc
import dash_trich_components as dtc

# import dash_daq as daq
from millify import millify

# import dash_bootstrap_components as dbc
import plotly.express as px

from dash_extensions.enrich import Dash, Input, Output, State

# # Connect to main app.py file
from app import app, server

# pd.set_option("display.max_columns", None)


def get_icon(icon):
    return DashIconify(icon=icon, height=16)


symbols = [
    "AXS",
    "BEZ.L",
    "FFH.TO",
    "RE",
    "HSX.L",
    "LRE.L",
    "MKL",
    "RNR",
    "AIG",
    "ALV.DE",
    "ACGL",
    "ARGO",
    "CB",
    "CINF",
    "MUV2.DE",
    "QBE.AX",
    "SREN.SW",
    "HIG",
    "TRV",
    "WRB",
    # "CS",
    "JRVR",
    "SPNT",
]
tickers = Ticker(symbols)
data = tickers.price
df = pd.json_normalize(data)

print(df.head())

carousel = (
    # dtc.Carousel(
    #     [
    #         html.Div(
    #             [
    #                 # This span shows the name of the stock.
    #                 html.Span(stock, style={"margin-right": "10px"}),
    #                 # This other one shows its variation.
    #                 html.Span(
    #                     "{}{:.2%}".format(
    #                         "+"
    #                         if round(
    #                             df["{}.regularMarketChange".format(stock)].iloc[0], 2
    #                         )
    #                         > 0
    #                         else "",
    #                         round(
    #                             df["{}.regularMarketChange".format(stock)].iloc[0], 2
    #                         ),
    #                     ),
    #                     style={
    #                         "color": "green"
    #                         if round(
    #                             df["{}.regularMarketChange".format(stock)].iloc[0], 2
    #                         )
    #                         > 0
    #                         else "red"
    #                     },
    #                 ),
    #             ]
    #         )
    #         for stock in symbols
    #     ],
    #     id="main-carousel",
    #     autoplay=True,
    #     slides_to_show=6,
    # ),
)

company_list = []
for ticker in symbols:
    stock_name = df["{}.longName".format(ticker)].iloc[0]
    stock_name = f"{stock_name} ({ticker})"
    stock_dict = {"value": f"{ticker}", "label": f"{stock_name}"}
    company_list.append(stock_dict)
    company_list = sorted(company_list, key=lambda d: d["label"])

historic_data = tickers.history(start="2019-05-01", end="2023-03-20")
historic_data = historic_data.reset_index()
all_company_fig = px.line(
    historic_data,
    x="date",
    y="close",
    color="symbol",
    hover_data={"date": "|%B %d, %Y"},
)
all_company_fig.update_layout(
    title="Insurance Stock Prices",
    font_family="convexFontLight",
    xaxis_title="Date",
    yaxis_title="Price",
    # plot_bgcolor= 'rgba(0, 0, 0, 0)',
    paper_bgcolor="rgba(0, 0, 0, 0)",
)
all_company_fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")


@app.callback(
    Output("stock_name", "children"),
    Output("stock_price", "children"),
    Output("stock_price_change", "children"),
    Output("stock_price_change", "style"),
    Output("stock_price_percentchange", "children"),
    Output("stock_price_percentchange", "style"),
    Output("stock_history_chart", "figure"),
    Output("stock_company_profile", "children"),
    Output("stock_summary_detail", "children"),
    Input("stock_search", "value"),
)
def populate_from_ticker(ticker):
    ### Create ticker for specific stock ###
    stock_specific_ticker = Ticker(ticker)
    # Price Profile #
    price_data = stock_specific_ticker.price
    price_df = pd.json_normalize(price_data)
    symbol = price_df["{}.symbol".format(ticker)].iloc[0]
    stock_name = price_df["{}.longName".format(ticker)].iloc[0]
    price = price_df["{}.regularMarketPrice".format(ticker)].iloc[0]
    price_change = round(price_df["{}.regularMarketChange".format(ticker)].iloc[0], 2)
    percent_change = round(
        (price_df["{}.regularMarketChangePercent".format(ticker)].iloc[0] * 100), 2
    )
    currency_symbol = price_df["{}.currencySymbol".format(ticker)].iloc[0]
    if float(price_change) > 0:
        price_change_colour = {"color": "green"}
        arrow = "⬆"
    else:
        price_change_colour = {"color": "red"}
        arrow = "⬇"

    price = f"{currency_symbol}{price}"
    price_change = f"{arrow}{currency_symbol}{price_change}"
    percent_change = f"{arrow}{percent_change}%"
    stock_name = f"{stock_name} ({symbol})"

    # Summary Profile #
    data_summary = stock_specific_ticker.summary_profile
    df_summary = pd.json_normalize(data_summary)

    address_line_1 = df_summary["{}.address1".format(ticker)].iloc[0]
    sector = df_summary["{}.sector".format(ticker)].iloc[0]
    industry = df_summary["{}.industry".format(ticker)].iloc[0]
    city = df_summary["{}.city".format(ticker)].iloc[0]
    # if f'{ticker}.state' in df_summary:
    #         state = df_summary["{}.state".format(ticker)].iloc[0]
    # else:
    #     state = None
    zip = df_summary["{}.zip".format(ticker)].iloc[0]
    country = df_summary["{}.country".format(ticker)].iloc[0]
    # phone = df_summary["{}.phone".format(ticker)].iloc[0]
    website = df_summary["{}.website".format(ticker)].iloc[0]
    address_div = html.Div(
        [
            dmc.Text("Company Profile", weight=700, underline=True, size="lg"),
            dmc.Text(f"{address_line_1}"),
            dmc.Text(f"{city}"),
            # dmc.Text(f"{state}"),
            dmc.Text(f"{zip}"),
            dmc.Text(f"{country}"),
            dmc.Anchor(f"{website}", href=f"{website}", target="_blank"),
            dmc.Text(f"Sector: {sector}"),
            dmc.Text(f"Industry: {industry}"),
        ]
    )

    ## Summary Detail
    data_summary_detail = stock_specific_ticker.summary_detail
    df_summary_detail = pd.json_normalize(data_summary_detail)
    market_cap = df_summary_detail[f"{ticker}.marketCap"].iloc[0]
    previous_close = df_summary_detail[f"{ticker}.previousClose"].iloc[0]
    open = df_summary_detail[f"{ticker}.open"].iloc[0]
    market_cap = millify(market_cap, precision=3)

    data_financial = stock_specific_ticker.income_statement()
    data_financial = data_financial[data_financial["periodType"].str.contains("TTM")]

    if data_financial.empty or math.isnan(data_financial["TotalRevenue"].iloc[0]):
        total_revenue = ""
    else:
        total_revenue = data_financial["TotalRevenue"].iloc[0] or 0
        total_revenue = millify(total_revenue, precision=3)

    summary_detail = html.Div(
        [
            dmc.Text("Company Detail", weight=700, underline=True, size="lg"),
            dmc.Text(f"Market Cap: {market_cap}"),
            dmc.Text(f"Previous Close: {currency_symbol}{previous_close}"),
            dmc.Text(f"Open: {currency_symbol}{open}"),
            dmc.Text(f"Total Revenue: {currency_symbol}{total_revenue}"),
        ]
    )

    # #### Balance Sheet ####
    # data_balance_sheet = stock_specific_ticker.balance_sheet()
    # print(data_balance_sheet.head())

    # ### All Financial Data ###
    # all_financial_data = stock_specific_ticker.all_financial_data('a')
    # print(all_financial_data.head())

    ### Update stock history chart ###

    # Default period = ytd, interval = 1d
    df2 = stock_specific_ticker.history(start="2019-05-01")
    df2 = df2.reset_index()
    # df2 = df2[df2['symbol'] == 'aapl']
    fig = px.line(df2, x="date", y="close")
    fig.update_layout(
        title=f"{stock_name} Stock Prices",
        font_family="convexFontLight",
        xaxis_title="Date",
        yaxis_title=f"Price ({currency_symbol})",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    return (
        stock_name,
        price,
        price_change,
        price_change_colour,
        percent_change,
        price_change_colour,
        fig,
        address_div,
        summary_detail,
    )


#### functions ####
money = dash_table.FormatTemplate.money(0)
percentage = dash_table.FormatTemplate.percentage(2)

dark_table_style_data = [
    {
        "if": {"row_index": "even"},
        "backgroundColor": "#515151",
    },
    {
        "if": {"row_index": "odd"},
        "backgroundColor": "rgb(26, 27, 30)",
    },
]
light_table_style_data = [
    {
        "if": {"row_index": "odd"},
        "backgroundColor": "white",
    },
    {
        "if": {"row_index": "even"},
        "backgroundColor": "rgb(220, 220, 220)",
    },
]


def create_home_link(label):
    return dmc.Text(
        label,
        size="xl",
        color="gray",
    )


app.layout = dmc.MantineProvider(
    dmc.MantineProvider(
        # withGlobalStyles=True,
        # withNormalizeCSS=True,
        inherit=True,
        theme={
            "fontFamily": "convexFontLight",
            "fontFamilyMonospace": "convexFontLight",
            "colors": {
                "convex": [
                    "#125049",
                    "#248F86",
                    "#83C7AF",
                    "#192322",
                    "#125049",
                    "#125049",
                    "#125049",
                    "#125049",
                    "#125049",
                    "#125049",
                ]
            },
            "primaryColor": "convex",
            "headings": {
                "fontFamily": "convexFontLight",
            },
        },
        id="mantine_theme",
        children=[
            dtc.Carousel(
                [
                    html.Div(
                        [
                            html.Span(
                                "{}".format(
                                    "⬆"
                                    if round(
                                        df[
                                            "{}.regularMarketChangePercent".format(
                                                stock
                                            )
                                        ].iloc[0]
                                        * 100,
                                        2,
                                    )
                                    > 0
                                    else "⬇",
                                ),
                                style={
                                    "color": "green"
                                    if round(
                                        df["{}.regularMarketChange".format(stock)].iloc[
                                            0
                                        ],
                                        2,
                                    )
                                    > 0
                                    else "red"
                                },
                            ),
                            # This span shows the name of the stock.
                            html.Span(
                                "{}".format(
                                    stock,
                                ),
                                style={"margin-right": "10px"},
                            ),
                            # This other one shows its variation.
                            html.Span(
                                "{}{}%".format(
                                    "+"
                                    if round(
                                        df[
                                            "{}.regularMarketChangePercent".format(
                                                stock
                                            )
                                        ].iloc[0]
                                        * 100,
                                        2,
                                    )
                                    > 0
                                    else "",
                                    round(
                                        df[
                                            "{}.regularMarketChangePercent".format(
                                                stock
                                            )
                                        ].iloc[0]
                                        * 100,
                                        2,
                                    ),
                                ),
                                style={
                                    "color": "green"
                                    if round(
                                        df["{}.regularMarketChange".format(stock)].iloc[
                                            0
                                        ],
                                        2,
                                    )
                                    > 0
                                    else "red"
                                },
                            ),
                        ]
                    )
                    for stock in symbols
                ],
                id="main-carousel",
                autoplay=True,
                slides_to_show=7,
                arrows=False,
                # center_mode=True,
            ),
            dmc.Drawer(
                title=html.Img(
                    src=app.get_asset_url("convexLogo.svg"),
                    style={
                        "width": "100%",
                        # "height": "auto",
                        # "padding-right": "50px",
                    },
                ),
                id="sidebar",
                # withCloseButton=False,
                # padding="md",
                size="240px",
                zIndex=10000,
                children=[
                    html.Div(
                        [
                            dmc.NavLink(
                                label="Home",
                                icon=get_icon(icon="bi:house-door-fill"),
                                rightSection=get_icon(icon="tabler-chevron-right"),
                                active=True,
                                variant="filled",
                            ),
                            dmc.NavLink(
                                label="Company Details",
                                icon=get_icon(icon="bi:house-door-fill"),
                                rightSection=get_icon(icon="tabler-chevron-right"),
                                # active=True,
                                variant="filled",
                            ),
                            dmc.NavLink(
                                label="Test",
                                icon=get_icon(icon="bi:house-door-fill"),
                                rightSection=get_icon(icon="tabler-chevron-right"),
                                # active=True,
                                variant="filled",
                            ),
                            dmc.NavLink(
                                label="More Stuff",
                                icon=get_icon(icon="bi:house-door-fill"),
                                rightSection=get_icon(icon="tabler-chevron-right"),
                                # active=True,
                                variant="filled",
                            ),
                        ],
                        style={"width": 240},
                    ),
                ],
            ),
            dcc.Location(id="url", refresh=False),
            dmc.Button(id="theme-changed", style={"display": "none"}),
            dmc.Button(id="initial-theme-check", style={"display": "none"}),
            dcc.Store(id="theme-store", storage_type="local"),
            dmc.Header(
                style={"overflow-x": "auto", "overflow-y": "hidden", "padding": "0px"},
                height=75,
                p="md",
                children=[
                    dmc.Container(
                        style={"min-width": "max-content"},
                        fluid=True,
                        children=[
                            dmc.Group(
                                position="apart",
                                # position="flex-start",
                                # align="baseline",
                                children=[
                                    dmc.Group(
                                        [
                                            dmc.ActionIcon(
                                                id="sidebar_button",
                                                # className="menu_button",
                                                variant="transparent",
                                                size="xl",
                                                children=[
                                                    DashIconify(
                                                        icon="majesticons:menu",
                                                        className="menu_button_icon",
                                                    )
                                                ],
                                            ),
                                            dmc.Title(
                                                "Insurance Finance Details",
                                                style={"font-family": "convexFont"},
                                            ),
                                        ]
                                    ),
                                    dmc.Group(
                                        align="right",
                                        style={"align-items": "center"},
                                        position="center",
                                        spacing="xl",
                                        # style={"padding-top": "30px"},
                                        children=[
                                            dmc.Select(
                                                id="stock_search",
                                                data=company_list,
                                                value="AXS",
                                                label="Search Company / Symbol",
                                                searchable=True,
                                                clearable=True,
                                                style={"width": 500},
                                                icon=DashIconify(
                                                    icon="radix-icons:magnifying-glass"
                                                ),
                                                # rightSection=DashIconify(
                                                #     icon="radix-icons:chevron-down"
                                                # ),
                                            ),
                                            dmc.Tooltip(
                                                dmc.ActionIcon(
                                                    id="color-scheme-toggle",
                                                    radius=30,
                                                    size=36,
                                                    variant="outline",
                                                    style={"align-items": "center"}
                                                    # color="gray",
                                                ),
                                                label="Dark/Light Theme",
                                                position="bottom",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            html.Div(
                id="page-content",
                style={"margin": "1%", "display": "grid"},
                children=[
                    dmc.Grid(
                        [
                            dmc.Col(
                                [
                                    #     dmc.Paper(
                                    #         [
                                    dmc.Stack(
                                        [
                                            dmc.Title(
                                                id="stock_name",
                                                order=2,
                                                style={"align-self": "center"},
                                            ),
                                            dmc.Group(
                                                [
                                                    html.Div(
                                                        id="stock_price",
                                                        style={
                                                            "font-size": "200%",
                                                        },
                                                    ),
                                                    html.Div(id="stock_price_change"),
                                                    html.Div(
                                                        id="stock_price_percentchange"
                                                    ),
                                                ],
                                                style={"align-self": "center"},
                                            ),
                                            dmc.SimpleGrid(
                                                [
                                                    html.Div(
                                                        id="stock_company_profile"
                                                    ),
                                                    html.Div(id="stock_summary_detail"),
                                                ],
                                                cols=2,
                                            ),
                                        ],
                                    )
                                ],
                                #         shadow="sm",
                                #         p="xs",
                                #         radius="sm",
                                #         style={
                                #             "background-color": "transparent",
                                #             "height": "100%",
                                #         },
                                #     )
                                # ],
                                span=4,
                            ),
                            dmc.Col([dcc.Graph(id="stock_history_chart")], span=8),
                            dmc.Col(
                                [dcc.Graph(id="all_stocks", figure=all_company_fig)],
                                span=12,
                            ),
                        ]
                    )
                ],
            ),
        ],
    ),
    theme={"colorScheme": "light"},
    id="mantine-docs-theme-provider",
    withGlobalStyles=True,
    withNormalizeCSS=True,
)


@app.callback(
    Output("color-scheme-toggle", "children"),
    Output("color-scheme-toggle", "color"),
    Output("all_stocks", "figure"),
    Input("color-scheme-toggle", "n_clicks"),
    State("theme-store", "data"),
    # prevent_initial_callback=True,
)
def change_image(n, value):
    light_icon = [
        DashIconify(
            icon="radix-icons:moon",
            width=22,
        )
    ]
    dark_icon = [
        DashIconify(
            icon="radix-icons:sun",
            width=22,
        )
    ]
    if n:
        if value == "dark":
            all_company_fig.update_layout(font_color="black")
            return light_icon, "gray", all_company_fig
        else:
            all_company_fig.update_layout(font_color="white")
            return dark_icon, "yellow", all_company_fig
    else:
        if value == "light":
            all_company_fig.update_layout(font_color="black")
            return light_icon, "gray", all_company_fig
        else:
            all_company_fig.update_layout(font_color="white")
            return dark_icon, "yellow", all_company_fig


@app.callback(
    Output("theme-store", "data"),
    Output("theme-changed", "n_clicks"),
    Input("color-scheme-toggle", "n_clicks"),
    State("theme-store", "data"),
)
def theme_store_check(n, data):
    if data:
        if n:
            if data == "dark":
                data = "light"
            else:
                data = "dark"
            return data, n
        else:
            raise PreventUpdate
    else:
        return "light", n


@app.callback(
    Output("sidebar", "opened"),
    Input("sidebar_button", "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    return True


@app.callback(
    Output("mantine-docs-theme-provider", "theme"),
    Input("theme-store", "data"),
)
def theme(data):
    if data:
        return {"colorScheme": data}
    else:
        return {"colorScheme": "light"}


if __name__ == "__main__":
    app.run_server(debug=True)
