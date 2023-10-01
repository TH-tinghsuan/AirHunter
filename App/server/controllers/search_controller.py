from server import app
from flask import request,render_template
from server.models.flight import get_flights_info, get_airport_detail, get_flights_info_rt

@app.route("/")
def index():
    return render_template("index.html")
        
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
    
