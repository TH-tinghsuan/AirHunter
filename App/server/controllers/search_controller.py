from server import app, dash_app
from flask import request,render_template
from server.models.flight import get_flights_info, get_airport_detail, get_flights_info_rt, get_price_df
from server.controllers.agent_url import get_url_ezFly, get_url_ezTravel_oneWay, get_url_ezTravel_return, get_url_lifeTour
from dash import html, dcc
import plotly.express as px
import json

@app.route("/")
def index(): 
    return render_template("search.html")

@app.route("/home")
def home(): 
    return render_template("search.html")

@app.route("/price/graph", methods=["GET"])
def price_graph():
    if request.args.get("depart") and request.args.get("arrive"):
        depart_at = request.args.get("depart").upper()
        arrive_at = request.args.get("arrive").upper()
        df = get_price_df(depart_at, arrive_at)
        if df.empty != True:
            fig = px.line(df, x='日期', y= '平均價格', color='旅行社')
            fig.update_xaxes(rangeslider_visible=True)
            fig.update_layout(title=f"{depart_at} - {arrive_at} 機票平均價格")
            dash_app.layout = html.Div([                            
                                        html.Div([
                                            dcc.Graph(id = 'line=chart', figure=fig)])
                                        ], style={'border': '1px solid #ccc', 'padding': '10px', 'width': '80%', 'margin': 'auto'})
            dash_html = dash_app.index()
            return render_template("dashboard.html", dash_html=dash_html)
        else:
            return render_template("dashboard.html", text=f"無{depart_at} - {arrive_at}的票價資訊")
    else:
        return render_template("dashboard.html")

@app.route("/search", methods=["GET"])
def search_price():
    return render_template("search.html")


@app.route("/flight/lists", methods=["GET"])
def get_flight_lists():
    if request.args.get("schedule") and request.args.get("departureAirports") and request.args.get("arriveAirports") and request.args.get("departureDates"):
        schedule = request.args.get("schedule")
        departureAirports = request.args.get("departureAirports")
        arriveAirports = request.args.get("arriveAirports")
        departureDates = request.args.get("departureDates")
        if schedule == "oneWay":  
            flight_info_ow = get_flights_info(arriveAirports, departureAirports, departureDates)
            if flight_info_ow != "No data":
                return render_template("outcome.html", schedule = "oneWay", flight_info=flight_info_ow, depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), date=departureDates)
            else:
                return render_template("outcome.html", schedule = "oneWay", depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), date=departureDates)
        elif schedule == "return":
            returnDates = request.args.get("returnDates")
            flight_info_rt =  get_flights_info_rt(arriveAirports, departureAirports, departureDates, returnDates)
            if flight_info_rt != "No data":
                 return render_template("outcome.html", schedule = "return", flight_info=flight_info_rt, depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), dp_date=departureDates, rt_date=returnDates)
            else:
                return render_template("outcome.html", schedule = "return", depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), dp_date=departureDates, rt_date=returnDates)
    else:
        return "Bad request"
    
@app.route("/flight/agentUrl/get", methods=["POST"])
def get_agent_url():
    """ reuqest data: agent_name, start_date, return_date, depart_at, return_at, d_flight_code, r_flight_code"""
    data = request.json
    agent_name = data["agent_name"]
    start_date = data["start_date"]
    return_date = data["return_date"]
    depart_at = data["depart_at"]
    return_at = data["return_at"]
    d_flight_code = data["d_flight_code"]
    r_flight_code = data["r_flight_code"]
    if agent_name == "ezFly":
        data = {"url": get_url_ezFly(depart_at, return_at, start_date, return_date)}
        return json.dumps(data, ensure_ascii=False)
    elif agent_name == "ezTravel" and return_date != "":
        data = {"url": get_url_ezTravel_return(start_date, return_date, depart_at, return_at, d_flight_code, r_flight_code)}
        return json.dumps(data, ensure_ascii=False)
    elif agent_name == "ezTravel" and return_date == "":
        data = {"url": get_url_ezTravel_oneWay(start_date, depart_at, return_at, d_flight_code)}
        return json.dumps(data, ensure_ascii=False)
    elif agent_name == "lifetour":
        data  = {"url": get_url_lifeTour(start_date, return_date, depart_at, return_at)}
        return json.dumps(data, ensure_ascii=False)
    else:
        return "Bad request", 404



    
