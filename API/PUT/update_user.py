import requests

"""in PUT: all properties of the object be provided while making request, if record is not exist then create new.
{
    "name" : "russel",
    "phone": 2129994444,
    "address: "32 maple ave"
}

"""

"""in PATCH: specific properties can only update
{
    "phone": 2223334444
}
"""

payload={
    "name": "touhidul islam",
    "job": "SDET"
}

resp = requests.put("https://reqres.in/api/users/2", data=payload)

code = resp.status_code
assert code == 200, "Code doesn't match"
print(resp.json())
assert resp.json()['job'] == 'SDET', 'job does not match'