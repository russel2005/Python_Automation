import requests


payload = {
    "name": "russel",
    "job": "SDET"
}

resp = requests.post("https://reqres.in/api/users", data=payload)

code = resp.status_code
assert code == 201, "Code doesn't match"

assert resp.json()['job'] == 'SDET', 'job does not match'
