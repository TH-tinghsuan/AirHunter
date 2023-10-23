import json, os
from flask import request,render_template, send_from_directory

from server import app
from server.models.flight import get_flights_info, get_airport_detail, get_flights_info_rt
from server.controllers.agent_url import get_url_ezFly, get_url_ezTravel_oneWay, get_url_ezTravel_return, get_url_lifeTour, get_url_richmond
from server.models.track import get_price_change_data, get_map_data

@app.route("/")
@app.route("/home")
def index(): 
    return render_template("home.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route("/search", methods=["GET"])
def search_price():
    return render_template("search.html")


@app.route("/flight/lists", methods=["GET"])
def get_flight_lists():
    schedule = request.args.get("schedule")
    departure_airports = request.args.get("departureAirports")
    arrive_airports = request.args.get("arriveAirports")
    departure_dates = request.args.get("departureDates")
    return_dates = request.args.get("returnDates")
    def handle_error(error_message):
        print(f"error {error_message}")
        return render_template("outcome.html", response_text="bad request.")
    
    if not (schedule and departure_airports and arrive_airports and departure_dates):
        return handle_error("Missing required parameters")

    try:
        depart_city = get_airport_detail(departure_airports)
        arrive_city = get_airport_detail(arrive_airports)
    except Exception as e:
        return handle_error(e)
    
    if schedule == "oneWay":
        try:
            flight_info_ow = get_flights_info(arrive_airports, departure_airports, departure_dates)
            if flight_info_ow != "No data":
                return render_template("outcome.html", schedule="oneWay", flight_info=flight_info_ow, depart=depart_city, arrive=arrive_city, date=departure_dates)
            else:
                return render_template("outcome.html", schedule="oneWay", depart=depart_city, arrive=arrive_city, date=departure_dates)
        except Exception as e:
            return handle_error(e)

    elif schedule == "return":
        if not return_dates:
            return handle_error("Missing returnDates parameter")
        try:
            flight_info_rt = get_flights_info_rt(arrive_airports, departure_airports, departure_dates, return_dates)
            if flight_info_rt != "No data":
                return render_template("outcome.html", schedule="return", flight_info=flight_info_rt, depart=depart_city, arrive=arrive_city, dp_date=departure_dates, rt_date=return_dates)
            else:
                return render_template("outcome.html", schedule="return", depart=depart_city, arrive=arrive_city, dp_date=departure_dates, rt_date=return_dates)
        except Exception as e:
            return handle_error(e)

    return handle_error("Invalid schedule parameter")
    
@app.route("/flight/agentUrl/get", methods=["POST"])
def get_agent_url():
    """ reuqest data: agent_name, 
                      start_date, 
                      return_date, 
                      depart_at, 
                      return_at, 
                      d_flight_code, 
                      r_flight_code
    """
    data = request.json
    schedule = data["schedule"]
    agent_name = data["agent_name"]
    start_date = data["start_date"]
    return_date = data["return_date"]
    depart_at = data["depart_at"]
    return_at = data["return_at"]
    d_flight_code = data["d_flight_code"]
    r_flight_code = data["r_flight_code"]
    
    if agent_name == "ezFly":
        data = {"url": get_url_ezFly(schedule, depart_at, return_at, start_date, return_date)}
        return json.dumps(data, ensure_ascii=False)
    
    elif agent_name == "ezTravel" and schedule == "return":
        data = {"url": get_url_ezTravel_return(start_date, return_date, depart_at, return_at, d_flight_code, r_flight_code)}
        return json.dumps(data, ensure_ascii=False)
    elif agent_name == "ezTravel" and schedule == "oneWay":
        data = {"url": get_url_ezTravel_oneWay(start_date, depart_at, return_at, d_flight_code)}
        return json.dumps(data, ensure_ascii=False)
    elif agent_name == "lifetour":
        data  = {"url": get_url_lifeTour(schedule, start_date, return_date, depart_at, return_at)}
        return json.dumps(data, ensure_ascii=False)
    elif agent_name == "richmond":
        data = {"url": get_url_richmond(schedule, start_date, return_date, depart_at, return_at)}
        return json.dumps(data, ensure_ascii=False)
    else:
        return "Bad request", 404


@app.route("/price/change/get", methods=["get"])
def get_price_change():
    data = get_price_change_data()
    if data:
        return json.dumps(data, ensure_ascii=False)
    else:
        json_data = {"data": None}
        return json.dumps(json_data, ensure_ascii=False)

@app.route("/map/get", methods=["get"])
def get_map():
    data = get_map_data()
    if data:
        return json.dumps(data, ensure_ascii=False)
    else:
        json_data = {"data": None}
        return json.dumps(json_data, ensure_ascii=False)
