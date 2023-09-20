from server import app
from server.models.flights import get_search_result, get_airport_detail
from flask import jsonify, request,render_template

@app.route("/")
def hello_world():
    return "Hello, MVC."

@app.route("/search", methods=["GET"])
def search_price():
    return render_template("search.html")


@app.route("/flight/lists", methods=["GET"])
def search_api():
    if request.args.get("departureAirports") and request.args.get("arriveAirports") and request.args.get("departureDates"):
        departureAirports = request.args.get("departureAirports")
        arriveAirports = request.args.get("arriveAirports")
        departureDates = request.args.get("departureDates")
        flight_info = get_search_result(arriveAirports, departureAirports, departureDates)
        if flight_info != "No data":
            return render_template("outcome.html", flight_info=flight_info, depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), date=departureDates)
        else:
            return render_template("outcome.html", depart=get_airport_detail(departureAirports), arrive=get_airport_detail(arriveAirports), date=departureDates)
    else:
        return "Bad request"
    

