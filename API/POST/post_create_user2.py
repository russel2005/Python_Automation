import json

import requests

payload = open("createUser.json", "r").read()

resp = requests.post("https://reqres.in/api/users", data=json.loads(payload))

code = resp.status_code
assert code == 201, "Code doesn't match"

assert resp.json()['job'] == 'python dev', 'job does not match'


