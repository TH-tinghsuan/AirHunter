import requests, json
from datetime import datetime

"""a function that get url if eztravel
"""
def format_date(date_string):
    """parameter: %Y-%m-%d return %d/%m/%Y"""
    try:
        date_object = datetime.strptime(date_string, "%Y-%m-%d").date()
        formatted_date = date_object.strftime("%d/%m/%Y")
        return formatted_date
    except ValueError:
        print("invalid format", date_string)

def get_url_ezTravel_return(start_date, return_date, depart_at, return_at, d_flight_code, r_flight_code):
    """date format: %d/%m/%Y"""
    url = "https://flight.eztravel.com.tw/apiv2/flight/list"
    formated_start_date = format_date(start_date)
    formated_return_date = format_date(return_date)
    if depart_at == "TSA":
        depart_at = "TPE"
    elif return_at == "TSA":
        return_at = "TPE"

    depart_payload =  {"head":{"clientID":"03169439807751431x87",
                                "transactionID":"pzo05msktfsute1i",
                                "userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"},
                        "data":
                                {"JourneyType":2,
                                "CabinType":"tourist",
                                "AirlineCode":"",
                                "AdultCnt":1,
                                "ChildCnt":0,
                                "InfantCnt":0,
                                "IsDirectFlight":False,
                                "OutBoundDate":formated_start_date,
                                "InBoundDate":formated_return_date,
                                "FromCityCode":depart_at,
                                "ToCityCode":return_at,
                                "FromAirportCode":"",
                                "ToAirportCode":"",
                                "ResourceType":"eztravel"}
                        }
    
    r = requests.post(url, json=depart_payload)

    if r.status_code == 200:
        data = r.json()
        if data["data"]:
            item = data["data"]["flightList"]
            for i in item:
                if i['flightKey'] == d_flight_code:
                    paras = i['seats'][0]['selectedFlightParas']
                    r.close() 
                    break
    else:
        print(f"can't find depart flight code, request status code: {r.status_code}")
        url = f"https://flight.eztravel.com.tw/booking?journeytype=2&departurecode={depart_at}&arrivalcode={return_at}&outbounddate={formated_start_date}&inbounddate={formated_return_date}&dport=&aport=&adults=1&children=0&infants=0&direct=false&cabintype=tourist&airline=&routeSearchToken=&resourceType=EzTravel"
        return url
   

    paras1 = json.loads(paras)
    payload_2 =  {"head":
                    {"clientID":"03169439807751431x87",
                    "transactionID":"pzo05msktfsute1i",
                    "userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"},
             "data":{"JourneyType":2,
                    "CabinType":"tourist",
                    "AirlineCode":"",
                    "AdultCnt":1,
                    "ChildCnt":0,
                    "InfantCnt":0,
                    "IsDirectFlight":False,
                    "OutBoundDate":formated_start_date,
                    "InBoundDate":formated_return_date,
                    "FromCityCode":depart_at,
                    "ToCityCode":return_at,
                    "FromAirportCode":"",
                    "ToAirportCode":"",
                    "ResourceType":"eztravel",
                    "OutBoundToken":paras1['OutBoundToken'],
                    "RouteSearchToken":paras1['RouteSearchToken']}}

    r2 = requests.post(url, json=payload_2)
    if r2.status_code == 200:
        data = r2.json()
        if data["data"]:
            item = data["data"]["flightList"]
            for i in item:
                if i['flightKey'] == r_flight_code:
                    par = i['seats'][0]['selectedFlightParas']
                    token = json.loads(par)['RouteSearchToken']
                    url = f"https://flight.eztravel.com.tw/booking?journeytype=2&departurecode={depart_at}&arrivalcode={return_at}&outbounddate={formated_start_date}&inbounddate={formated_return_date}&dport=&aport=&adults=1&children=0&infants=0&direct=false&cabintype=tourist&airline=&routeSearchToken={token}&resourceType=EzTravel"
                    break
    else:
        url = f"https://flight.eztravel.com.tw/booking?journeytype=2&departurecode={depart_at}&arrivalcode={return_at}&outbounddate={formated_start_date}&inbounddate={formated_return_date}&dport=&aport=&adults=1&children=0&infants=0&direct=false&cabintype=tourist&airline=&routeSearchToken=&resourceType=EzTravel"
    
    return url

#test= get_url_ezTravel_return("04/12/2023", "08/12/2023", "TPE", "TTT","B78721", "B78722")
def get_url_ezTravel_oneWay(depart_date, depart_at, arrive_at, flight_code):
    """date format: %d/%m/%Y"""
    formated_depart_date = format_date(depart_date)
    url = "https://flight.eztravel.com.tw/apiv2/flight/list"
    payload = {"head":
                        {"clientID":"03169439807751431x87",
                        "transactionID":"mp6fzt20pieul2f3",
                        "userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"},
                    "data":
                        {"JourneyType":1,
                        "CabinType":"any",
                        "AirlineCode":"",
                        "AdultCnt":1,
                        "ChildCnt":0,
                        "InfantCnt":0,
                        "IsDirectFlight":True,
                        "OutBoundDate":formated_depart_date,
                        "FromCityCode":depart_at,
                        "ToCityCode":arrive_at,
                        "FromAirportCode":"",
                        "ToAirportCode":"",
                        "ResourceType":"eztravel"}}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        data = r.json()
        if data["data"]:
            item = data["data"]["flightList"]
            for i in item:
                if i['flightKey'] == flight_code:
                    par = i['seats'][0]['selectedFlightParas']
                    token = json.loads(par)['RouteSearchToken']
                    url = f"https://flight.eztravel.com.tw/booking?journeytype=1&departurecode={depart_at}&arrivalcode={arrive_at}&outbounddate={formated_depart_date}&dport=&aport=&adults=1&children=0&infants=0&direct=false&cabintype=tourist&airline=&routeSearchToken={token}&resourceType=EzTravel"
                    break
    else:
        print(r.status_code)
        url = f"https://flight.eztravel.com.tw/booking?journeytype=1&departurecode={depart_at}&arrivalcode={arrive_at}&outbounddate={formated_depart_date}&dport=&aport=&adults=1&children=0&infants=0&direct=false&cabintype=tourist&airline=&routeSearchToken=&resourceType=EzTravel"
    return url


def get_url_ezFly(schedule, dp_ct_name, ar_ct_name, dp_date, rt_date):
    """date format: %Y%m%d"""
    guid_url = "https://ea.ezfly.com/ProdDAIR/Json/GetDataToken/"
    if schedule == "return":
        payload = { "trip":"RT", 
                    "ct_from":dp_ct_name,
                    "ct_from_name":dp_ct_name,
                        "ct_to":ar_ct_name,
                        "ct_to_name":ar_ct_name,
                        "dp_date":dp_date.replace("-", ""),
                        "rt_date":rt_date.replace("-", ""),
                        "adults":1,
                        "childs":0,
                        "olds":0,
                        "islands":0,
                        "islands_C":0,
                        "islands_O":0,
                        "s":"",
                        "o":""}
    elif schedule == "oneWay":
        payload = { "trip":"OW", 
                    "ct_from":dp_ct_name,
                    "ct_from_name":dp_ct_name,
                        "ct_to":ar_ct_name,
                        "ct_to_name":ar_ct_name,
                        "dp_date":dp_date.replace("-", ""),
                        "rt_date":rt_date.replace("-", ""),
                        "adults":1,
                        "childs":0,
                        "olds":0,
                        "islands":0,
                        "islands_C":0,
                        "islands_O":0,
                        "s":"",
                        "o":""}
        
    r = requests.post(url=guid_url, json=payload)
    if r.status_code == 200:
        data = r.json()
        guid = data["Guid"]
        if schedule == "return":
            url = f"https://ea.ezfly.com/ProdDAIR/inquiry/indexSearch/?Guid={guid}&trip=RT&ct_from={dp_ct_name}&ct_to={ar_ct_name}&dp_date={dp_date}&rt_date={rt_date}&adults=1&childs=0&olds=0&islands=0&islands_C=0&islands_O=0&s=&o=&AL=&Q=Q"
        elif schedule == "oneWay":
             url = f"https://ea.ezfly.com/ProdDAIR/inquiry/indexSearch/?Guid={guid}&trip=OW&ct_from={dp_ct_name}&ct_to={ar_ct_name}&dp_date={dp_date}&rt_date={rt_date}&adults=1&childs=0&olds=0&islands=0&islands_C=0&islands_O=0&s=&o=&AL=&Q=Q"
       
    else:
        url = f"https://ea.ezfly.com/ProdDAIR/inquiry/indexSearch/?trip=OW&ct_from={dp_ct_name}&ct_to={ar_ct_name}&dp_date={dp_date}&rt_date={rt_date}&adults=1&childs=0&olds=0&islands=0&islands_C=0&islands_O=0&s=&o=&AL=&Q=Q"
    return url

def get_url_lifeTour(schedule, start_date, return_date, depart_at, return_at):
    formatted_start_date = start_date.replace("-", "")
    formatted_reurn_date = return_date.replace("-", "")

    if schedule == "oneWay":
        schedule_id = 0
        formatted_reurn_date = ""
    elif schedule == "return":
        schedule_id = 1
    
    url = f"https://flights.lifetour.com.tw/search?&trvaltype={schedule_id}&dep={depart_at}&arr={return_at}&godate={formatted_start_date}&backdate={formatted_reurn_date}&adt=1&chd=0&classcode=999&trans=false"
    return url

def get_url_richmond(schedule, start_date, return_date, depart_at, return_at):
    if schedule == "oneWay":
        schedule_id = 1
        return_date = ""
    elif schedule == "return":
        schedule_id = 2
  
    if depart_at == "TSA":
        depart_at = "TPE"
    elif return_at == "TSA":
        return_at = "TPE"

    url = f"https://www.travel4u.com.tw/flight/search/?trip={schedule_id}&dep_location_codes={depart_at}&arr_location_codes={return_at}&dep_location_types=2&arr_location_types=1&dep_dates={start_date}&return_date={return_date}&adult=1&child=0&cabin_class=2&is_direct_flight_only=True&exclude_budget_airline=False&target_page=1&order_by=0_1&transfer_count=&carriers=&search_key="
    return url
