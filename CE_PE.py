# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 20:42:09 2022
@author: roopaksr
"""

import requests
import json
import math

# Method to get nearest strikes
def round_nearest(x,num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x,100)

# Urls for fetching Data
url_oc      = "https://www.nseindia.com/option-chain"
url_bnf     = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

# Headers
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}

sess = requests.Session()
cookies = dict()
lot_value = 25
num = 7
step = 100
# Local methods
def set_cookie():
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)

def get_data(url):
    set_cookie()
    response = sess.get(url, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==401):
        set_cookie()
    if(response.status_code==200):
        return response.text
    return ""

def set_ds(oi_dict, url):
    response_text = get_data(url)
    data = json.loads(response_text)
    ul = data["records"]["underlyingValue"]
    nearest = nearest_strike_bnf(ul)
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    currExpiryDate = data["records"]["expiryDates"][0]
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                oi_dict[strike] = {'CE' : [], 'PE' : []} 
                strike = strike + step

def print_hr():
    print("------------------------------------------------------------------------")

def print_oi(oi_dict):
    for strike in oi_dict:
        print(str(strike) + " CE [" + str(oi_dict[strike]['CE'][0]) + "] - PE  [" + str(oi_dict[strike]['PE'][0]) + "]")

# Fetching CE and PE data based on Nearest Expiry Date
def update_oi(oi_dict, url):
    global bnf_ul
    global bnf_nearest
    response_text = get_data(url)
    data = json.loads(response_text)
    bnf_ul = data["records"]["underlyingValue"]
    bnf_nearest=nearest_strike_bnf(bnf_ul)
    print("Bank Nifty")
    print("   Expiry: " + data["records"]["expiryDates"][0])
    print("   Last Price: " + str(bnf_ul))
    print("   Nearest Strike: " + str(bnf_nearest))
    currExpiryDate = data["records"]["expiryDates"][0]
    keys = list(oi_dict.keys())
    key_index = 0
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if key_index < len(keys) and item["strikePrice"] == keys[key_index]:
                oi_dict[keys[key_index]]['CE'].append(item["CE"]["openInterest"]*lot_value)
                oi_dict[keys[key_index]]['PE'].append(item["PE"]["openInterest"]*lot_value)
                key_index = key_index + 1;

oi_dict = {}
set_ds(oi_dict, url_bnf)
update_oi(oi_dict, url_bnf)
print_oi(oi_dict)
