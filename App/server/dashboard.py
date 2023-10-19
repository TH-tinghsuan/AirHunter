import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from server import app
from server.models.track import get_price_trend, get_price_record
from server.models.flight import get_price_df
from datetime import date, datetime, timedelta
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
dash_app.title = "AirHunter | 票價趨勢查詢"
depart_options = [
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
                                                options=depart_options,
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
                        
                                dcc.Loading(children=[html.Div([
                                    html.Div([
                                    html.H2(style={
                                                'textAlign': 'center',
                                                'color': '#FFFFF',
                                                'backgroundColor': '#00000'
                                            }, id='avg-price-chart-title'), 
                                    dcc.Graph(id = 'avg-price-chart')]
                                    )]),  
                                
                                html.Div([
                                    html.Div([
                                        html.H2(style={
                                                    'textAlign': 'center',
                                                    'color': '#FFFFF',
                                                    'backgroundColor': '#00000'
                                                }, id='price-trend-chart-title'), 
                                        dcc.Graph(id = 'price-trend-chart')]
                                        )]),
                                
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

                                        dcc.Graph(id = 'price-history-chart')]
                                        )]),
                                        dcc.Interval(
                                                id='interval-component',
                                                interval=3*3600*1000, # in milliseconds
                                                n_intervals=0
                                            )], id="loading",type="default")
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
    

    @dash_app.callback(
        [Output("avg-price-chart", "figure"), Output("price-trend-chart", "figure"), Output("price-history-chart", "figure"),
         Output("avg-price-chart-title", "children"), Output("price-trend-chart-title", "children"), Output("price-history-chart-title", "children")],
        [Input("depart-dropdown", "value"), Input("arrive-dropdown", "value"), Input('date-range-picker', 'date'), Input('interval-component', 'n_intervals')])
    def update_charts(selected_depart, selected_arrive, date_value, n_intervals):
        def get_filterd_df(dataframe):
            condition = (dataframe["出發地"] == selected_depart) & (dataframe["目的地"] == selected_arrive)
            df_filtered = dataframe[condition]
            return df_filtered
        df1 = get_price_df()
        df2 = get_price_trend()
        df3 = get_price_record()
        
        fig1 = px.line(get_filterd_df(df1), x='出發日', y= '平均價格', color='旅行社')
        fig2 = px.bar(get_filterd_df(df2), x='出發日', y= '最低價格')
        df3_condition = (df3["出發地"] == selected_depart) & (df3["目的地"] == selected_arrive) & (df3["出發日"] == date_value)
        filtered_fig3 = df3[df3_condition]
        filtered_fig3['搜尋時間_x'] = [(str((datetime.today().date() - item).days)  + "天前")if (datetime.today().date() -item).days > 0 else "今天" for item in filtered_fig3['搜尋時間']]
        
        fig3 = px.line(filtered_fig3, x='搜尋時間_x', y= '最低價格', labels={'搜尋時間_x':'搜尋時間'})
        airports = {'MZG':'澎湖', 'KHH':'高雄', 'KNH':'金門', 
            'RMQ':'台中', 'TSA':'台北', 'TNN':'台南',
            'MFK':'馬祖', 'LZN':'馬祖(南竿)', 'TTT':'台東',
            'HUN':'花蓮', 'CYI':'嘉義'}
        if selected_depart is not None and selected_arrive is not None:
            title1 = f"{airports[selected_depart]} - {airports[selected_arrive]} 機票平均價格"
            title2 = f"{airports[selected_depart]} - {airports[selected_arrive]} 票價趨勢"
            title3 = f"{airports[selected_depart]} - {airports[selected_arrive]} 票價紀錄"
        else:
            title1 = "機票平均價格"
            title2 = "票價趨勢"
            title3 = "票價紀錄"
            
        return [fig1, fig2, fig3, title1, title2, title3]
    
