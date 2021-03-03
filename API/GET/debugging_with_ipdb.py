''''pip install ipdb'''


import requests
import json
import jsonpath

# API URL
BASE_URL = "https://reqres.in"
PATH_PARAM = "/api/users"



def get_response(params):
    resp = requests.get(
        BASE_URL + PATH_PARAM, params=params
    )
    return resp.json()

# send GET Request
params = {'page': 2}

# DEBUG with
import ipdb; ipdb.set_trace()
resp = get_response(params)
print(resp)
