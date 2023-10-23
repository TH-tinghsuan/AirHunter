import dash
import plotly.express as px
from dash import dcc, html, Input, Output, callback
from datetime import date, datetime, timedelta

from server import app
from server.models.track import get_price_trend, get_price_record
from server.models.flight import get_price_df


dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
dash_app.title = "AirHunter | 票價趨勢查詢"

DEPART_OPTIONS = [
    {"label": "台北", "value": "TSA"},
    {"label": "高雄", "value": "KHH"},
    {"label": "花蓮", "value": "HUN"},
    {"label": "台東", "value": "TTT"},
    {"label": "台南", "value": "TNN"},
    {"label": "台中", "value": "RMQ"},
    {"label": "嘉義", "value": "CYI"},
    {"label": "澎湖", "value": "MZG"},
    {"label": "金門", "value": "KNH"},
    {"label": "馬祖(北竿)", "value": "MFK"},
    {"label": "馬祖(南竿)", "value": "LZN"}
]

AIRPORTS = {'MZG':'澎湖', 'KHH':'高雄', 'KNH':'金門', 
            'RMQ':'台中', 'TSA':'台北', 'TNN':'台南',
            'MFK':'馬祖', 'LZN':'馬祖(南竿)', 'TTT':'台東',
            'HUN':'花蓮', 'CYI':'嘉義'}

with app.app_context():  
    dash_app.layout = html.Div([
                                html.Link(rel='stylesheet', href='/static/dash_style.css'),
                                html.Link(rel='icon', href='assets/favicon.ico', type='image/x-icon'),
                                    html.Div([
                                            html.Div([
                                                html.A([
                                                    html.Img(src="https://side-project-flights-bucket.s3.ap-southeast-2.amazonaws.com/imgs/new_logo.png")
                                                ], href="/"),
                                        html.Nav([
                                            html.Ul([
                                                html.Li(html.A("搜機票", href="/search")),
                                                html.Li(html.A("看趨勢", href="/dashboard")),
                                                html.Li(html.A("票價追蹤", href="/user/favorites"))
                                            ])], id="left-nav"),
                                        html.Nav([
                                            html.Ul([
                                                html.Li(html.A("回首頁", href="/")),
                                            ], id="right-nav")
                                        ])
                                        ], className="navbar")
                                    ], className="container"),
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                html.P("出發地"),
                                                dcc.Dropdown(
                                                id="depart-dropdown",
                                                options=DEPART_OPTIONS,
                                                placeholder='請選擇',
                                                multi=False)
                                            ], className="spot-container"),
                                            html.Div([
                                                html.P("目的地"),
                                                dcc.Dropdown(
                                                id="arrive-dropdown",
                                                placeholder='請先選擇出發地',
                                                multi=False)
                                            ], className="spot-container")
                                        ], id="spot-selector"), 
                        
                                html.Div([
                                    html.Div([
                                    html.H2(style={
                                                'textAlign': 'center',
                                                'color': '#FFFFF',
                                                'backgroundColor': '#00000'
                                            }, id='avg-price-chart-title'), 
                                    dcc.Loading(
                                        children=[dcc.Graph(id = 'avg-price-chart')],
                                        id="chart1-loading"
                                    )
                                   
                                    ])]),  
                                
                                html.Div([
                                    html.Div([
                                        html.H2(style={
                                                    'textAlign': 'center',
                                                    'color': '#FFFFF',
                                                    'backgroundColor': '#00000'
                                                }, id='price-trend-chart-title'), 
                                        dcc.Loading(
                                            children=[dcc.Graph(id = 'price-trend-chart')],
                                            id="chart2-loading"
                                        )
                                        ])]),
                                
                                html.Div([
                                    html.Div([
                                        html.H2(style={
                                                    'textAlign': 'center',
                                                    'color': '#FFFFF',
                                                    'backgroundColor': '#00000'
                                                }, id='price-history-chart-title'), 
                                                html.Div([
                                                    html.P(children="出發日",
                                                style={
                                                    'textAlign': 'left',
                                                    'color': '#FFFFF',
                                                    'backgroundColor': '#00000'
                                                }),
                                                dcc.DatePickerSingle(
                                                    id='date-range-picker',
                                                    min_date_allowed=date.today(),
                                                    max_date_allowed=date.today() + timedelta(days=60),
                                                    initial_visible_month=date.today(),
                                                    date=date.today()
                                                )], id="date-selector"),
                                        dcc.Loading(
                                            children=[dcc.Graph(id = 'price-history-chart')],
                                            id="chart3-loading"
                                        )
                                        
                                        ])])
                                ], id="dashboard-layout",style={'padding': '10px', 'width':'60%', 'margin-left': '20%', 'margin-right': '20%'}),
                                html.Footer([
                                    html.Div([
                                        html.P("Contact me", style={"color": "white"}),
                                        html.A("Github", href="https://github.com/TH-tinghsuan", style={"color": "white", "border": "solid white 0.5px", "padding": "2px", "border-radius": "5px"}),
                                        html.A("Linkedin", href="#", style={"color": "white", "border": "solid white 0.5px", "padding": "2px", "border-radius": "5px"})
                                    ], className="web-info"),

                                    html.Div([
                                        html.P("© 2023 AirHunter All rights reserved", style={"color": "white"})
                                    ], className="copy-right")
                                ], id="footer", style={"margin-top": "50px"})
                            ])


    @dash_app.callback(
    [Output("arrive-dropdown", "options"),Output("arrive-dropdown", "value")],
    Input("depart-dropdown", "value")
    )
    def update_arrive_options(selected_depart):
        destination_map = {
            'TSA': [{"label": "台東", "value": "TTT"}, 
                    {"label": "澎湖", "value": "MZG"}, 
                    {"label": "花蓮", "value": "HUN"}, 
                    {"label": "金門", "value": "KNH"}, 
                    {"label": "馬祖(北竿)", "value": "MFK"}, 
                    {"label": "馬祖(南竿)", "value": "LZN"}],
            'KHH': [{"label": "澎湖", "value": "MZG"}, 
                    {"label": "花蓮", "value": "HUN"}, 
                    {"label": "金門", "value": "KNH"}],
            'HUN': [{"label": "台中", "value": "RMQ"}, 
                    {"label": "台北", "value": "TSA"}, 
                    {"label": "高雄", "value": "KHH"}],
            'TTT': [{"label": "台北", "value": "TSA"}],
            'TNN': [{"label": "澎湖", "value": "MZG"}, 
                    {"label": "金門", "value": "KNH"}],
            'RMQ': [{"label": "澎湖", "value": "MZG"}, 
                    {"label": "花蓮", "value": "HUN"}, 
                    {"label": "金門", "value": "KNH"}],
            'CYI': [{"label": "澎湖", "value": "MZG"}, 
                    {"label": "金門", "value": "KNH"}],
            'MZG': [{"label": "台中", "value": "RMQ"}, 
                    {"label": "台北", "value": "TSA"}, 
                    {"label": "台南", "value": "TNN"}, 
                    {"label": "嘉義", "value": "CYI"}, 
                    {"label": "金門", "value": "KNH"}, 
                    {"label": "高雄", "value": "KHH"}],
            'KNH': [{"label": "台中", "value": "RMQ"}, 
                    {"label": "台北", "value": "TSA"}, 
                    {"label": "台南", "value": "TNN"}, 
                    {"label": "嘉義", "value": "CYI"}, 
                    {"label": "澎湖", "value": "MZG"}, 
                    {"label": "金門", "value": "KNH"}],
            'MFK': [{"label": "台北", "value": "TSA"}],
            'LZN': [{"label": "台中", "value": "RMQ"}, {"label": "台北", "value": "TSA"}]}

        return[destination_map.get(selected_depart, []), None]
    
    def get_filterd_df(dataframe, selected_depart, selected_arrive):
            condition = (dataframe["出發地"] == selected_depart) & (dataframe["目的地"] == selected_arrive)
            df_filtered = dataframe[condition]
            return df_filtered
    
    @dash_app.callback(
            [Output("avg-price-chart-title", "children"), Output("price-trend-chart-title", "children"), Output("price-history-chart-title", "children")],
            [Input("depart-dropdown", "value"), Input("arrive-dropdown", "value")]
     )
    def update_title(selected_depart, selected_arrive):
        if selected_depart is not None and selected_arrive is not None:
            title1 = f"{AIRPORTS[selected_depart]} - {AIRPORTS[selected_arrive]} 機票平均價格"
            title2 = f"{AIRPORTS[selected_depart]} - {AIRPORTS[selected_arrive]} 票價趨勢"
            title3 = f"{AIRPORTS[selected_depart]} - {AIRPORTS[selected_arrive]} 票價紀錄"
        else:
            title1 = "機票平均價格"
            title2 = "票價趨勢"
            title3 = "票價紀錄"
            
        return [title1, title2, title3]

    @dash_app.callback(
         Output("avg-price-chart", "figure"),
        [Input("depart-dropdown", "value"), Input("arrive-dropdown", "value")])
    def update_charts(selected_depart, selected_arrive):
        df_avg_price = get_filterd_df(get_price_df(), selected_depart, selected_arrive)
        fig_avg_price = px.line(df_avg_price, x='出發日', y= '平均價格', color='旅行社')
            
        return fig_avg_price
    
    @dash_app.callback(
         Output("price-trend-chart", "figure"),
        [Input("depart-dropdown", "value"), Input("arrive-dropdown", "value")])
    def update_charts(selected_depart, selected_arrive):
        df_price_trend = get_filterd_df(get_price_trend(), selected_depart, selected_arrive)
        fig_price_trend = px.bar(df_price_trend, x='出發日', y= '最低價格')

        return fig_price_trend
    
    @dash_app.callback(Output("price-history-chart", "figure"),
                    [Input("depart-dropdown", "value"), Input("arrive-dropdown", "value"), Input('date-range-picker', 'date')])
    def update_price_history_chart(selected_depart, selected_arrive, date_value):
        df_price_record = get_price_record()
        df_price_record_condition = (df_price_record["出發地"] == selected_depart) & (df_price_record["目的地"] == selected_arrive) & (df_price_record["出發日"] == date_value)
        filtered_fig = df_price_record[df_price_record_condition]
        filtered_fig['搜尋時間_x'] = [(str((datetime.today().date() - item).days)  + "天前")if (datetime.today().date() -item).days > 0 else "今天" for item in filtered_fig['搜尋時間']]
        fig_price_record = px.line(filtered_fig, x='搜尋時間_x', y= '最低價格', labels={'搜尋時間_x':'搜尋時間'})
        
        return fig_price_record

