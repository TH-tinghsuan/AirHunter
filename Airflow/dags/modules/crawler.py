import json
import time
import logging
import requests
from datetime import datetime, timedelta
from fake_useragent import UserAgent

from airflow.models import Variable

from modules.cloud import upload_to_s3

logging.basicConfig(level=logging.INFO)
AIRLINE_BUNDLE = {"TSA":["TTT", "MZG", "HUN", "KNH", "MFK", "LZN"],
          "KHH":["MZG", "HUN", "KNH"],
          "HUN":["RMQ", "TSA", "KHH"],
          "TTT":["TSA"],
          "TNN":["MZG", "KNH"],
          "RMQ":["MZG", "HUN", "KNH", "LZN"],
          "CYI":["MZG", "KNH"],
          "MZG":["RMQ", "TSA", "TNN", "CYI", "KNH", "KHH"],
          "KNH":["RMQ", "TSA", "TNN", "CYI", "MZG", "KHH"],
          "MFK":["TSA"],
          "LZN":["RMQ", "TSA"]
          }

def get_all_by_date(date: datetime, date_format: str, crawler_func: callable) -> dict:
    date = date.strftime(date_format)
    total= {"data":[]}
    for key, value in AIRLINE_BUNDLE.items():    
        depart_airport = key
        for item in value:
            arrive_airport = item
            crawler_data = crawler_func(depart_airport, arrive_airport, date)
            if crawler_data:
                total["data"].append(crawler_data)
                print(f"Done. from: {depart_airport} to: {arrive_airport}")
            else:
                print(f"No data from: {depart_airport} to: {arrive_airport}")
    return total

def get_lifeTour_raw_data(depart: str, arrive: str, date: str) -> json:
    url ="https://flights.lifetour.com.tw/Ajax/SearchTicket"
    payload = {
        "Type": "OneWay",
        "none_search": "0",
        "AdultCount": "1",
        "ChildCount": "0",
        "IsMobile": False,
        "OnlyDirect": True,
        "FlightInfo[0][Origin]": depart,
        "FlightInfo[0][Destination]": arrive,
        "FlightInfo[0][DepartDate]": date,
        "FlightInfo[0][ClassLevel]": "999"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            data = json.loads(r.json())
            return data
        else:
            error_message = f"error in get_lifeTour_raw_data, status_code: {r.status_code}, request payload: {payload}, content: {r.text}"
            raise Exception(error_message)
    except Exception as e:
        logging.error(f"error in get_lifeTour_raw_data: {e}")

def get_richmond_raw_data(depart_from: str, arrive_at: str, depart_date: str) -> str:
    url = f"https://www.travel4u.com.tw/flight/search/flights/?trip=1&dep_location_codes={depart_from}&arr_location_codes={arrive_at}&dep_location_types=1&arr_location_types=1&dep_dates={depart_date}&return_date=&adult=1&child=0&cabin_class=2&is_direct_flight_only=True&exclude_budget_airline=False&target_page=1&order_by=0_1&transfer_count=0&carriers=&search_key="
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            if data["code"] == 100:
                return data['flights_html']
        else:
            error_message = f"status_code: {r.status_code}, request url: {url}, content: {r.text}"
            raise Exception(error_message)
    except Exception as e:
        logging.error(f"error in get_richmond_raw_data: {e}")

def get_ezTravel_raw_data(depart_airport: str, arrive_airport: str, depart_date: str) -> dict:
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
                    "OutBoundDate":depart_date,
                    "FromCityCode":depart_airport,
                    "ToCityCode":arrive_airport,
                    "FromAirportCode":"",
                    "ToAirportCode":"",
                    "ResourceType":"eztravel"}}
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            data = r.json()
            if data["data"]:
                return data["data"]
        else:
            error_message = f"status_code: {r.status_code}, request payload: {payload}, content: {r.text}"
            raise Exception(error_message)
    except Exception as e:
        logging.error(f"error in get_ezTravel_raw_data: {e}")

def get_ezFly_Guid(dp_ct_name: str, ar_ct_name: str, dp_date: str) -> str:
    root_url = "https://ea.ezfly.com/ProdDAIR/Json/GetDataTokenWithCallback/"
    args = f"""?trip=OW&ct_from={dp_ct_name}&ct_to={ar_ct_name}&dp_date{dp_date}&rt_date=&adults=1&childs=0&olds=0&islands=0&islands_C=0&islands_O=0&s=&o=&AL=&Q=Q"""
    url = root_url + args
    try:
        r = requests.get(url=url)
        if r.status_code == 200:
            response = r.text.replace("(", "").replace(")", "")
            data = json.loads(response)
            return data["Guid"]
        else:
            error_message = f"status_code: {r.status_code}, url: {url}"
            raise Exception(error_message)
    except Exception as e:
        logging.error(f"error in get_ezFly_Guid: {e}")

def get_ezFly_raw_data(depart_airport: str, arrive_airport: str, date: str) -> dict:
    guid = get_ezFly_Guid(depart_airport, arrive_airport, date)
    if not guid:
        for _ in range(3): # try up to 3 times to get Guid
            guid = get_ezFly_Guid(depart_airport, arrive_airport, date)
            if guid:
                break
            time.sleep(10)

    if guid:
        form_data = {"SegmentTrip": "GO",
                    "DepartureAirport": depart_airport,
                    "ArrivalAirport": arrive_airport,
                    "Sdate": date,
                    "Edate": date,
                    "Guid": guid}
        user_agent = UserAgent()
        headers = {'User-Agent': user_agent.random}
        try:
            r = requests.post(url="https://ea.ezfly.com/ProdDAIR/Home/GetProdLists", data=form_data, headers=headers)
            if r.status_code == 200:
                data = r.text
                if data:
                    data_dict = {"depart": depart_airport, "arrive": arrive_airport, "date": date, "info": data}
                    return data_dict
            else:
                error_message = f"error in get_ezFly_raw_data, status_code: {r.status_code}, request form data: {form_data}, content: {r.text}"
                raise Exception(error_message)
        except Exception as e:
            logging.error(f"error occur: {e}")
    return None

def scrape_and_upload_s3(start_date: datetime, total_dates: str, fun_name: callable, agent_name: str):
    search_date = Variable.get("search_date_key")    
    date_format = {"ezTravel": "%d/%m/%Y", "ezFly": "%Y%m%d", "lifeTour": "%Y%m%d", "richmond": "%Y-%m-%d"}
    date_list = [start_date + timedelta(days=i) for i in range(total_dates)]
    for date in date_list:
        total = get_all_by_date(date, date_format[agent_name], fun_name)
        upload_to_s3(f"{date}_domestic_{agent_name}_{search_date}.json", json.dumps(total, ensure_ascii=False))
