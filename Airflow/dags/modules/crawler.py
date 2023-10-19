from datetime import datetime, timedelta
import requests
import json
import concurrent.futures
from modules.cloud import upload_to_s3
from airflow.models import Variable
import random

def get_all_by_date(date, date_format, crawler_func):
    bundle = {"TSA":["TTT", "MZG", "HUN", "KNH", "MFK", "LZN"],
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
    date = date.strftime(date_format)
    total= {"data":[]}
    for key, value in bundle.items():    
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

def lifetour_scraper(start_date, total_dates):  
    def get_json_file(deapart, arrive, date):
        url ="https://flights.lifetour.com.tw/Ajax/SearchTicket"
        payload = {
            "Type": "OneWay",
            "none_search": "0",
            "AdultCount": "1",
            "ChildCount": "0",
            "IsMobile": False,
            "OnlyDirect": True,
            "FlightInfo[0][Origin]": deapart,
            "FlightInfo[0][Destination]": arrive,
            "FlightInfo[0][DepartDate]": date,
            "FlightInfo[0][ClassLevel]": "999"
        }
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            data = json.loads(r.json())
            return data
        else:
            print("error, ", r.status_code)
    search_date = Variable.get("search_date_key")    
    date_list = [start_date + timedelta(days=i) for i in range(total_dates)]
    for date in date_list:
        total = get_all_by_date(date, "%Y%m%d", get_json_file)
        upload_to_s3(f"{date}_domestic_lifeTour_{search_date}.json", json.dumps(total, ensure_ascii=False))

def richmond_crawler(start_date, total_dates):
    def get_flights_html(depart_from, arrive_at, depart_date):
        url = f"https://www.travel4u.com.tw/flight/search/flights/?trip=1&dep_location_codes={depart_from}&arr_location_codes={arrive_at}&dep_location_types=1&arr_location_types=1&dep_dates={depart_date}&return_date=&adult=1&child=0&cabin_class=2&is_direct_flight_only=True&exclude_budget_airline=False&target_page=1&order_by=0_1&transfer_count=0&carriers=&search_key="
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            if data["code"] == 100:
                return data['flights_html']
        else:
            print("error, ", r.status_code)
    search_date = Variable.get("search_date_key") 
    date_list = [start_date + timedelta(days=i) for i in range(total_dates)]
    for date in date_list:
        total = get_all_by_date(date, "%Y-%m-%d", get_flights_html)
        upload_to_s3(f"{date}_domestic_richmond_{search_date}.json", json.dumps(total, ensure_ascii=False))


def ezTravel_crawler(start_date, total_dates):
    def get_json_data(depart_airport, arrive_airport, depart_date):
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
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            data = r.json()
            if data["data"]:
                return data["data"]
        else:
            message = r.status_code
            print(f"error, {message}")
    search_date = Variable.get("search_date_key")  
    date_list = [start_date + timedelta(days=i) for i in range(total_dates)]
    for date in date_list:
        total = get_all_by_date(date, "%d/%m/%Y", get_json_data)
        upload_to_s3(f"{date}_domestic_ezTravel_{search_date}.json", json.dumps(total, ensure_ascii=False))



def ezFly_crawler(start_date, total_dates):
    def get_Guid(dp_ct_name, ar_ct_name, dp_date):
        root_url = "https://ea.ezfly.com/ProdDAIR/Json/GetDataTokenWithCallback/"
        args = f"""?trip=OW&ct_from={dp_ct_name}&ct_to={ar_ct_name}&dp_date{dp_date}&rt_date=&adults=1&childs=0&olds=0&islands=0&islands_C=0&islands_O=0&s=&o=&AL=&Q=Q"""
        url = root_url + args
        r = requests.get(url=url)
        if r.status_code == 200:
            response = r.text.replace("(", "").replace(")", "")
            data = json.loads(response)
            return data["Guid"]
        else:
            return f"error, {r.status_code}"
    
    def get_html_data(depart_airport, arrive_airport, date):
        guid = get_Guid(depart_airport, arrive_airport, date)
        form_data = {"SegmentTrip": "GO",
                    "DepartureAirport": depart_airport,
                    "ArrivalAirport": arrive_airport,
                    "Sdate": date,
                    "Edate": date,
                    "Guid": guid}
        my_headers = [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
        ]
        headers = {'User-Agent':random.choice(my_headers)}
        response = requests.post(url="https://ea.ezfly.com/ProdDAIR/Home/GetProdLists", data=form_data, headers=headers)
        if response.status_code == 200:
            data = response.text
            if data:
                data_dict = {"depart": depart_airport, "arrive": arrive_airport, "date": date, "info": data}
                return data_dict
        else:
            message = response.status_code
            print(f"error, {message}")
    search_date = Variable.get("search_date_key") 
    date_list = [start_date + timedelta(days=i) for i in range(total_dates)]
    for date in date_list:
        total = get_all_by_date(date, "%Y%m%d", get_html_data)
        upload_to_s3(f"{date}_domestic_ezFly_{search_date}.json", json.dumps(total, ensure_ascii=False))
