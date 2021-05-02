import requests

resp = requests.delete("https://reqres.in/api/users/2")

code = resp.status_code
assert code == 204, "Code doesn't match"
