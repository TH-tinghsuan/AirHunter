from server import db
from sqlalchemy.sql import func
import pandas as pd
from datetime import datetime, timedelta


class FlightsDomestic(db.Model):
    __tablename__= "flights_domestic_main"
    arrive_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    arrive_time = db.Column(db.DateTime(), nullable=False)
    depart_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    depart_time = db.Column(db.DateTime(), primary_key=True, nullable=False)
    clsType = db.Column(db.String(10))
    airlineName = db.Column(db.String(10), primary_key=True, nullable=False)
    flightCode = db.Column(db.String(10), primary_key=True, nullable=False)
    price = db.Column(db.Integer)
    agentName = db.Column(db.String(20), primary_key=True, nullable=False)
    search_date = db.Column(db.DateTime(), primary_key=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP(), server_default = func.now())

    def __init__(self, arrive_airport_code, arrive_time, 
                 depart_airport_code, depart_time, clsType, airlineName,
                 flightCode, price, search_date, created_at):
        self.arrive_airport_code = arrive_airport_code
        self.arrive_time = arrive_time
        self.depart_airport_code = depart_airport_code
        self.depart_time = depart_time
        self.clsType = clsType
        self.airlineName = airlineName
        self.flightCode = flightCode
        self.price = price
        self.search_date = search_date
        self.created_at = created_at

class Airline(db.Model):
    __tablename__= "airlines"
    name = db.Column(db.String(10), primary_key=True, nullable=False)
    airline_code = db.Column(db.String(2), nullable=False)
    country = db.Column(db.String(10), nullable=False)
    images = db.Column(db.String(200))
    def __init__(self, name, airline_code, country, images):
        self.name = name
        self.airline_code = airline_code
        self.country = country
        self.images = images

class Airport(db.Model):
    __tablename__ = "airports"
    airport_name = db.Column(db.String(100), nullable=False)
    IATA_code = db.Column(db.String(3), primary_key=True, nullable=False)
    city_name = db.Column(db.String(10), nullable=False)
    city_ID = db.Column(db.String(3), nullable=False)
    image = db.Column(db.String(200))
    def __init__(self, airport_name, IATA_code, city_name, city_ID, image):
        self.airport_name = airport_name
        self,IATA_code = IATA_code
        self.city_name = city_name
        self.city_ID = city_ID
        self.image = image
    

def get_airline_detail(airlineName):
    db.session.commit()
    query = Airline.query.filter_by(name=airlineName)
    airline_info = {"name": query[0].name, "airline_code": query[0].airline_code, "country": query[0].country, "images": query[0].images}
    return airline_info

def get_airport_detail(airport_code):
    db.session.commit()
    query = Airport.query.filter_by(IATA_code=airport_code)
    airport_info = {"airport_name": query[0].airport_name, "IATA_code": query[0].IATA_code, "city_name": query[0].city_name, "city_ID": query[0].city_ID, "image": query[0].image}
    return airport_info

def get_utc_8_date():
    utc_date = datetime.utcnow()
    utc_8_date = utc_date + timedelta(hours=8)
    formatted_date = utc_8_date.strftime('%Y-%m-%d')
    return formatted_date

def check_data():
    db.session.commit()
    search_date = get_utc_8_date()
    query = FlightsDomestic.query.filter(FlightsDomestic.search_date == search_date)
    data = query.all()
    if data:
        return True
    else:
        return False


def get_flights_info(search_arrive_airport_code, search_depart_airport_code, search_depart_time):
    db.session.commit()
    check_if_exist_data = check_data()
    if check_if_exist_data == True:
         search_date = get_utc_8_date()
    else:
        date_str = get_utc_8_date()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        search_date_obj = date_obj - timedelta(days=1)
        search_date = search_date_obj.strftime('%Y-%m-%d')
    query = db.session.query(
        FlightsDomestic.arrive_time,
        FlightsDomestic.depart_time,
        FlightsDomestic.arrive_airport_code,
        FlightsDomestic.depart_airport_code,
        func.group_concat(FlightsDomestic.price).label('prices'),
        func.group_concat(FlightsDomestic.airlineName).label('airlineNames'),
        func.group_concat(FlightsDomestic.flightCode).label('flightCodes'),
        func.group_concat(FlightsDomestic.agentName).label('agentNames')
    )

    query = query.filter(
        FlightsDomestic.arrive_airport_code == search_arrive_airport_code,
        FlightsDomestic.depart_airport_code == search_depart_airport_code,
        func.DATE(FlightsDomestic.depart_time) == search_depart_time,
        FlightsDomestic.search_date == search_date,
        FlightsDomestic.price.isnot(None)
    )

    query = query.group_by(
        FlightsDomestic.arrive_time,
        FlightsDomestic.depart_time,
        FlightsDomestic.arrive_airport_code,
        FlightsDomestic.depart_airport_code
    )

    flight_info = query.all()
    if flight_info:
        return search_result_to_dict(flight_info)
    else:
        return "No data"

def calcuate_duration(start_time, end_time):
    time_difference = end_time - start_time
    days = time_difference.days
    seconds = time_difference.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days == 0 and hours != 0 and minutes == 0:
        return f"{hours} 小時"
    elif days == 0 and hours == 0:
        return f"{minutes} 分鐘"
    elif days == 0 and hours != 0:
        return f"{hours} 小時 {minutes} 分鐘"
    return f"{days} 天 {hours} 小時 {minutes} 分鐘"

def get_non_empty_value(lst):
    for item in lst:
        if item != "":
            return item
    return None

def search_result_to_dict(flight_info):
    total = []
    for item in flight_info:
        return_json = {}
        return_json['type'] = "直達"
        return_json['duration'] = calcuate_duration(item.depart_time, item.arrive_time)
        return_json['depart_time'] = item.depart_time.strftime('%H:%M')
        return_json['depart_airport'] = get_airport_detail(item.depart_airport_code)
        return_json['arrive_time'] = item.arrive_time.strftime('%H:%M')
        return_json['arrive_airport'] = get_airport_detail(item.arrive_airport_code)
        airlineName_list = item.airlineNames.split(",")
        airlineName = get_non_empty_value(airlineName_list)
        return_json["airline"] = airlineName
        ariline_detail = get_airline_detail(airlineName)
        return_json["flight_code"] = ariline_detail['airline_code'] +item.flightCodes.split(",")[0]
        return_json["airline_img"] = ariline_detail['images']
        return_json['items'] = []
        prices = item.prices.split(",")
        agNames =  item.agentNames.split(",")
        for i in range(len(prices)):
            airlines = {}
            airlines["price"] = prices[i]
            airlines["agentName"] = agNames[i]
            return_json['items'].append(airlines)
        return_json['items'] = sorted(return_json['items'], key= lambda s: s["price"])
        return_json['minPrice'] = min(return_json['items'], key= lambda s: s["price"])["price"]
        total.append(return_json)
    return sorted(total, key= lambda s: s["minPrice"])

def get_flights_info_rt(search_arrive_airport_code, search_depart_airport_code, search_depart_time, search_return_time):
    db.session.commit()
    check_if_exist_data = check_data()
    if check_if_exist_data == True:
         search_date = get_utc_8_date()
    else:
        date_str = get_utc_8_date()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        search_date_obj = date_obj - timedelta(days=1)
        search_date = search_date_obj.strftime('%Y-%m-%d')
    subquery_A = (
    db.session.query(
        FlightsDomestic.depart_airport_code.label('A_depart_airport_code'),
        FlightsDomestic.depart_time.label('A_depart_time'),
        FlightsDomestic.arrive_airport_code.label('A_arrive_airport_code'),
        FlightsDomestic.arrive_time.label('A_arrive_time'),
        FlightsDomestic.airlineName.label('A_airlineName'),
        FlightsDomestic.flightCode.label('A_flightCode'),
        FlightsDomestic.agentName.label('A_agentName'),
        FlightsDomestic.price.label('A_price')
    )
    .filter(
        FlightsDomestic.search_date == search_date,
        func.DATE(FlightsDomestic.depart_time) == search_depart_time,
        FlightsDomestic.depart_airport_code == search_depart_airport_code,
        FlightsDomestic.arrive_airport_code == search_arrive_airport_code,
        FlightsDomestic.price.isnot(None)
    )
    .subquery()
    )

    subquery_B = (
    db.session.query(
        FlightsDomestic.depart_airport_code.label('B_depart_airport_code'),
        FlightsDomestic.depart_time.label('B_depart_time'),
        FlightsDomestic.arrive_airport_code.label('B_arrive_airport_code'),
        FlightsDomestic.arrive_time.label('B_arrive_time'),
        FlightsDomestic.airlineName.label('B_airlineName'),
        FlightsDomestic.flightCode.label('B_flightCode'),
        FlightsDomestic.agentName.label('B_agentName'),
        FlightsDomestic.price.label('B_price')
    )
    .filter(
        FlightsDomestic.search_date == search_date,
        func.DATE(FlightsDomestic.depart_time) == search_return_time,
        FlightsDomestic.depart_airport_code == search_arrive_airport_code,
        FlightsDomestic.arrive_airport_code == search_depart_airport_code,
        FlightsDomestic.price.isnot(None)
    )
    .subquery()
    )
    
    query = (
    db.session.query(
        subquery_A.c.A_flightCode,
        subquery_A.c.A_depart_airport_code,
        subquery_A.c.A_depart_time,
        subquery_A.c.A_arrive_airport_code,
        subquery_A.c.A_arrive_time,
        subquery_A.c.A_airlineName,
        subquery_B.c.B_flightCode,
        subquery_B.c.B_depart_airport_code,
        subquery_B.c.B_depart_time,
        subquery_B.c.B_arrive_airport_code,
        subquery_B.c.B_arrive_time,
        func.group_concat(subquery_A.c.A_price + subquery_B.c.B_price).label('price'),
        func.group_concat(subquery_A.c.A_agentName).label('agentName')
    )
    .select_from(
        subquery_A
        .join(
            subquery_B,
            (subquery_A.c.A_airlineName == subquery_B.c.B_airlineName) &
            (subquery_A.c.A_agentName == subquery_B.c.B_agentName)
        )
    )
    .group_by(
        subquery_A.c.A_depart_time,
        subquery_A.c.A_arrive_time,
        subquery_A.c.A_airlineName,
        subquery_B.c.B_depart_time,
        subquery_B.c.B_arrive_time
        )
    )

    results = query.all()
    if results:
        return rt_search_result_to_dict(results)
    else:
        return "No data"


def rt_search_result_to_dict(flight_info):
    total = []
    for item in flight_info:
        return_json = {}
        airlineName_go = item.A_airlineName
        ariline_detail = get_airline_detail(airlineName_go)
        return_json['go_type'] = "直達"
        return_json['go_duration'] = calcuate_duration(item.A_depart_time, item.A_arrive_time)
        return_json["go_airline"] = airlineName_go
        return_json["go_flight_info"] = ariline_detail['airline_code'] +item.A_flightCode
        return_json['go_depart_time'] = item.A_depart_time.strftime('%H:%M')
        return_json['go_depart_airport'] = get_airport_detail(item.A_depart_airport_code)
        return_json['go_arrive_time'] = item.A_arrive_time.strftime('%H:%M')
        return_json['go_arrive_airport'] = get_airport_detail(item.A_arrive_airport_code)
        return_json['go_airline_img'] = ariline_detail['images']
        return_json['back_type'] = "直達"
        return_json['back_duration'] = calcuate_duration(item.B_depart_time, item.B_arrive_time)
        return_json["back_airline"] = airlineName_go
        return_json["back_flight_info"] = ariline_detail['airline_code'] +item.B_flightCode
        return_json['back_depart_time'] = item.B_depart_time.strftime('%H:%M')
        return_json['back_depart_airport'] = get_airport_detail(item.B_depart_airport_code)
        return_json['back_arrive_time'] = item.B_arrive_time.strftime('%H:%M')
        return_json['back_arrive_airport'] = get_airport_detail(item.B_arrive_airport_code)
        return_json['back_airline_img'] = ariline_detail['images']

        return_json['items'] = []
        prices = item.price.split(",")
        agNames =  item.agentName.split(",")
        for i in range(len(prices)):
            airlines = {}
            airlines["price"] = prices[i]
            airlines["agentName"] = agNames[i]
            return_json['items'].append(airlines)
        return_json['items'] = sorted(return_json['items'], key= lambda s: s["price"])
        return_json['minPrice'] = min(return_json['items'], key= lambda s: s["price"])["price"]
        total.append(return_json)
    return sorted(total, key= lambda s: s["minPrice"])   

def get_price_df():
    print("get_price_df")
    db.session.commit()
    check_if_exist_data = check_data()
    if check_if_exist_data == True:
         search_date = get_utc_8_date()
    else:
        date_str = get_utc_8_date()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        search_date_obj = date_obj - timedelta(days=1)
        search_date = search_date_obj.strftime('%Y-%m-%d')
    query = (
        db.session.query(
            func.date(FlightsDomestic.depart_time).label('depart_date'),
            FlightsDomestic.agentName.label('agentName'),
            func.round(func.avg(FlightsDomestic.price), 0).label('avg_price'), 
            FlightsDomestic.depart_airport_code,
            FlightsDomestic.arrive_airport_code
        )
        .filter(
            FlightsDomestic.search_date == search_date,
            FlightsDomestic.price != None)
        .group_by(
            func.date(FlightsDomestic.depart_time),
            FlightsDomestic.agentName,
            FlightsDomestic.depart_airport_code,
            FlightsDomestic.arrive_airport_code
        ))
    results = query.all()
    data_list = []
    for item in results:
       data = {}
       data['出發地'] = item.depart_airport_code
       data['目的地'] = item.arrive_airport_code
       data["出發日"] = item.depart_date
       data["平均價格"] = item.avg_price
       data["旅行社"] = item.agentName
       data_list.append(data)
    df = pd.DataFrame.from_dict(data_list)
    return df
    
