# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 20:42:09 2022
@author: roopaksr
"""

import requests
import json
import math
import time

''' Method to get nearest strikes
'''
def round_nearest(x,num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x,100)

# Urls for fetching Data
url_oc      = "https://www.nseindia.com/option-chain"
url_bnf     = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

# Headers
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}

''' Global configs
'''
sess = requests.Session()
cookies = dict()
lot_value = 25
num = 4
step = 100
refresh_interval = 180
# Local methods
def set_cookie():
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)

''' Get the data from Url
'''
def get_data(url):
    set_cookie()
    response = sess.get(url, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==401):
        set_cookie()
    if(response.status_code==200):
        return response.text
    return ""

''' Printing horizontal line for better redaibility
'''
def print_hr():
    print("------------------------------------------------------------------------")

''' Fetching CE and PE data based on Nearest Expiry Date and add it
    oi_dict, the keys of oi_dict which are strike prices will be used
    to update the values later. We want to only update some particular
    strike price which is initilized here
'''
def initilize_strike_prices(oi_dict, url):
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

''' Printing last entry in oi_dict which contains all CE PE OI for gicen expiry
    It is time series data capturing the values at regular interval
'''
def print_oi(oi_dict):
    for strike in oi_dict:
        print(str(strike) + " CE [" + str(oi_dict[strike]['CE'][-1]) + "] - PE  [" + str(oi_dict[strike]['PE'][-1]) + "]")

''' Fetching CE and PE data based on Nearest Expiry Date and append it to
    oi_dict data structures for plotting/printing
'''
def update_oi(oi_dict, url):
    bnf_ul = 0.0
    bnf_nearest = 0.0
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

''' The main function is called in loop to append values to oi_dict
    oi_dict will be like
    {strike} : {'CE'} : [oi_t, oi_t+1], {'PE'} : [oi_t, oi_t+1]
'''
def main():
    oi_dict = {}
    initilize_strike_prices(oi_dict, url_bnf)
    while True:
        update_oi(oi_dict, url_bnf)
        print_oi(oi_dict)
        time.sleep(refresh_interval)
        
if __name__== "__main__" :
    main()

