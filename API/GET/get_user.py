import requests

p = {"page": 2}
resp = requests.get("https://reqres.in/api/users", params=p)

code = resp.status_code
assert code == 200, "Code doesn't match"
#print(resp.text)
#print(resp.content)
#print(resp.json())
#check json data at http://jsonviewer.stack.hu/


#check headers
#print(resp.headers)

#check cookies
#print(resp.cookies)

print(resp.url)
print(resp.encoding)

#respose
json_response =  resp.json()
assert json_response["total"] == 12, "total is not matching"
print(json_response["total"])

email = json_response["data"][0]["email"]
assert email.endswith("@reqres.in"), "email format is not matching"
assert json_response["data"][0]["last_name"] != None
