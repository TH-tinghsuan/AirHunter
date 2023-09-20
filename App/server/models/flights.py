from server import connection, cursor
import json
from datetime import datetime


def get_search_result(arrive_airport_code, depart_airport_code, depart_time):
    sql = """SELECT
        arrive_time,
        depart_time,
        arrive_airport_code, 
        depart_airport_code,
        GROUP_CONCAT(price) AS prices,
        GROUP_CONCAT(airlineName) AS airlineName,
        GROUP_CONCAT(flightCode) AS flightCode,
        GROUP_CONCAT(agentName) AS agentNames
        FROM flights_domestic
        where arrive_airport_code=%s and depart_airport_code=%s and DATE(depart_time) = %s and price is not null
        GROUP BY arrive_time, depart_time, arrive_airport_code, depart_airport_code;"""
    cursor.execute(sql, (arrive_airport_code, depart_airport_code, depart_time))
    catch = cursor.fetchall()
    if catch:
        return search_result_to_dict(catch)
    else:
        return "No data"

def search_result_to_dict(data):
    total = []
    for d in data:
        return_json = {}
        return_json['depart_time'] = d['depart_time'].strftime('%Y-%m-%d %H:%M')
        return_json['depart_airport'] = get_airport_detail(d['depart_airport_code'])
        return_json['arrive_time'] = d['arrive_time'].strftime('%Y-%m-%d %H:%M')
        return_json['arrive_airport'] = get_airport_detail(d['arrive_airport_code'])
        return_json['items'] = []
        prices = d["prices"].split(",")
        agNames =  d["agentNames"].split(",")
        for i in range(len(prices)):
            item = {}
            item["price"] = prices[i]
            item["agentName"] = agNames[i]
            return_json['items'].append(item)
        
        total.append(return_json)
    return total

def get_airline_detail(airlineName):
    sql = "SELECT name, airline_code FROM airlines WHERE name = %s"
    cursor.execute(sql, airlineName)
    catch = cursor.fetchone()
    return catch

def get_airport_detail(airport_code):
    sql = "SELECT city_name, airport_name , IATA_code FROM airports where IATA_code = %s"
    cursor.execute(sql, airport_code)
    catch = cursor.fetchone()
    return catch



