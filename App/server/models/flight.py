from server import db
from sqlalchemy.sql import func

class Batch_version(db.Model):
    __tablename__ = "batch_version"
    version = db.Column(db.String(20), primary_key=True)
    region = db.Column(db.String(20))

    def __init__(self, version, region):
        self.version = version
        self.region = region


class Flights_domestic(db.Model):
    __tablename__= "flights_domestic"
    arrive_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    arrive_time = db.Column(db.DateTime(), nullable=False)
    depart_airport_code = db.Column(db.String(3), primary_key=True, nullable=False)
    depart_time = db.Column(db.DateTime(), primary_key=True, nullable=False)
    clsType = db.Column(db.String(10))
    airlineName = db.Column(db.String(10), primary_key=True, nullable=False)
    flightCode = db.Column(db.String(10), primary_key=True, nullable=False)
    price = db.Column(db.Integer)
    agentName = db.Column(db.String(20), primary_key=True, nullable=False)
    batch_version = db.Column(db.String(20), primary_key=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP(), server_default = func.now())

    def __init__(self, arrive_airport_code, arrive_time, 
                 depart_airport_code, depart_time, clsType, airlineName,
                 flightCode, price, batch_version, created_at):
        self.arrive_airport_code = arrive_airport_code
        self.arrive_time = arrive_time
        self.depart_airport_code = depart_airport_code
        self.depart_time = depart_time
        self.clsType = clsType
        self.airlineName = airlineName
        self.flightCode = flightCode
        self.price = price
        self.batch_version = batch_version
        self.created_at = created_at

class Airline(db.Model):
    __tablename__= "airlines"
    name = db.Column(db.String(10), primary_key=True, nullable=False)
    airline_code = db.Column(db.String(2), nullable=False)
    country = db.Column(db.String(10), nullable=False)

    def __init__(self, name, airline_code, country):
        self.name = name
        self.airline_code = airline_code
        self.country = country

class Airport(db.Model):
    __tablename__ = "airports"
    airport_name = db.Column(db.String(100), nullable=False)
    IATA_code = db.Column(db.String(3), primary_key=True, nullable=False)
    city_name = db.Column(db.String(10), nullable=False)
    city_ID = db.Column(db.String(3), nullable=False)

    def __init__(self, airport_name, IATA_code, city_name, city_ID):
        self.airport_name = airport_name
        self,IATA_code = IATA_code
        self.city_name = city_name
        self.city_ID = city_ID
    

def get_batch_version(region):
    db.session.commit()
    query = Batch_version.query.filter_by(region=region)
    return query[0].version


def get_airline_detail(airlineName):
    db.session.commit()
    query = Airline.query.filter_by(name=airlineName)
    airline_info = {"name": query[0].name, "airline_code": query[0].airline_code, "country": query[0].country}
    return airline_info

def get_airport_detail(airport_code):
    db.session.commit()
    query = Airport.query.filter_by(IATA_code=airport_code)
    airport_info = {"airport_name": query[0].airport_name, "IATA_code": query[0].IATA_code, "city_name": query[0].city_name, "city_ID": query[0].city_ID}
    return airport_info


def get_flights_info(search_arrive_airport_code, search_depart_airport_code, search_depart_time):
    db.session.commit()
    newest_batch_version = get_batch_version("domestic")
    query = db.session.query(
        Flights_domestic.arrive_time,
        Flights_domestic.depart_time,
        Flights_domestic.arrive_airport_code,
        Flights_domestic.depart_airport_code,
        func.group_concat(Flights_domestic.price).label('prices'),
        func.group_concat(Flights_domestic.airlineName).label('airlineNames'),
        func.group_concat(Flights_domestic.flightCode).label('flightCodes'),
        func.group_concat(Flights_domestic.agentName).label('agentNames')
    )

    query = query.filter(
        Flights_domestic.arrive_airport_code == search_arrive_airport_code,
        Flights_domestic.depart_airport_code == search_depart_airport_code,
        func.DATE(Flights_domestic.depart_time) == search_depart_time,
        Flights_domestic.batch_version == newest_batch_version,
        Flights_domestic.price.isnot(None)
    )

    query = query.group_by(
        Flights_domestic.arrive_time,
        Flights_domestic.depart_time,
        Flights_domestic.arrive_airport_code,
        Flights_domestic.depart_airport_code
    )

    flight_info = query.all()
    if flight_info:
        return search_result_to_dict(flight_info)
    else:
        return "No data"

def search_result_to_dict(flight_info):
    total = []
    for item in flight_info:
        return_json = {}
        return_json['depart_time'] = item.depart_time.strftime('%Y-%m-%d %H:%M')
        return_json['depart_airport'] = get_airport_detail(item.depart_airport_code)
        return_json['arrive_time'] = item.arrive_time.strftime('%Y-%m-%d %H:%M')
        return_json['arrive_airport'] = get_airport_detail(item.arrive_airport_code)
        airlineName = item.airlineNames.split(",")[0]
        return_json["flight_info"] = airlineName + " " + get_airline_detail(airlineName)['airline_code'] +item.flightCodes.split(",")[0]
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
    newest_batch_version = get_batch_version("domestic")

    subquery_A = (
    db.session.query(
        Flights_domestic.depart_airport_code.label('A_depart_airport_code'),
        Flights_domestic.depart_time.label('A_depart_time'),
        Flights_domestic.arrive_airport_code.label('A_arrive_airport_code'),
        Flights_domestic.arrive_time.label('A_arrive_time'),
        Flights_domestic.airlineName.label('A_airlineName'),
        Flights_domestic.flightCode.label('A_flightCode'),
        Flights_domestic.agentName.label('A_agentName'),
        Flights_domestic.price.label('A_price')
    )
    .filter(
        Flights_domestic.batch_version == newest_batch_version,
        func.DATE(Flights_domestic.depart_time) == search_depart_time,
        Flights_domestic.depart_airport_code == search_depart_airport_code,
        Flights_domestic.arrive_airport_code == search_arrive_airport_code
    )
    .subquery()
    )

    subquery_B = (
    db.session.query(
        Flights_domestic.depart_airport_code.label('B_depart_airport_code'),
        Flights_domestic.depart_time.label('B_depart_time'),
        Flights_domestic.arrive_airport_code.label('B_arrive_airport_code'),
        Flights_domestic.arrive_time.label('B_arrive_time'),
        Flights_domestic.airlineName.label('B_airlineName'),
        Flights_domestic.flightCode.label('B_flightCode'),
        Flights_domestic.agentName.label('B_agentName'),
        Flights_domestic.price.label('B_price')
    )
    .filter(
        Flights_domestic.batch_version == newest_batch_version,
        func.DATE(Flights_domestic.depart_time) == search_return_time,
        Flights_domestic.depart_airport_code == search_arrive_airport_code,
        Flights_domestic.arrive_airport_code == search_depart_airport_code
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
        return_json["go_flight_info"] = airlineName_go + " " + get_airline_detail(airlineName_go)['airline_code'] +item.A_flightCode
        return_json['go_depart_time'] = item.A_depart_time.strftime('%Y-%m-%d %H:%M')
        return_json['go_depart_airport'] = get_airport_detail(item.A_depart_airport_code)
        return_json['go_arrive_time'] = item.A_arrive_time.strftime('%Y-%m-%d %H:%M')
        return_json['go_arrive_airport'] = get_airport_detail(item.A_arrive_airport_code)
        return_json["back_flight_info"] = airlineName_go + " " + get_airline_detail(airlineName_go)['airline_code'] +item.B_flightCode
        return_json['back_depart_time'] = item.B_depart_time.strftime('%Y-%m-%d %H:%M')
        return_json['back_depart_airport'] = get_airport_detail(item.B_depart_airport_code)
        return_json['back_arrive_time'] = item.B_arrive_time.strftime('%Y-%m-%d %H:%M')
        return_json['back_arrive_airport'] = get_airport_detail(item.B_arrive_airport_code)
        
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
    
