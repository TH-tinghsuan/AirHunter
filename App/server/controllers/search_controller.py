from server import app
#from server.models.flights import get_search_result, get_airport_detail
from flask import jsonify, request,render_template, redirect
from server.models.flight import get_flights_info, get_airport_detail

@app.route("/")
def index():
    return render_template("index.html")
        
@app.route("/search", methods=["GET"])
def search_price():
    return render_template("search.html")


@app.route("/flight/lists", methods=["GET"])
def get_flight_lists():
    if request.args.get("departureAirports") and request.args.get("arriveAirports") and request.args.get("departureDates"):
        departureAirports = request.args.get("departureAirports")
        arriveAirports = request.args.get("arriveAirports")
        departureDates = request.args.get("departureDates")
        flight_info = get_flights_info(arriveAirports, departureAirports, departureDates)
        if flight_info != "No data":
            return render_template("outcome.html", flight_info=flight_info, depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), date=departureDates)
        else:
            return render_template("outcome.html", depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), date=departureDates)
    else:
        return "Bad request"
    
