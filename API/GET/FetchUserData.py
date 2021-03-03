import requests
import json
import jsonpath

# API URL
BASE_URL = "https://reqres.in"
PATH_PARAM = "/api/users"
QUERY_PARAM = {'page': 2}


# send GET Request
response = requests.get(BASE_URL+PATH_PARAM, params=QUERY_PARAM)

# Display Response Content
#print(response.content)

# Fetch Response Header value
print(response.headers)
print(response.headers.get("Content-Type"))
print(response.headers.get("Server"))
print(response.headers.get("Content-Encoding"))

# Display Response JSON format
#print(json.dumps(response.json(), indent=2))

# Validate status_code
assert response.status_code == 200

# Fetch Cookies
print(response.cookies)

# Fetch Elapsed time
print(response.elapsed)

##############################
# Parse response to Json Format
json_response = json.loads(response.text)
print(json_response)

# Fetch Response value with specific content Using JSONPATH > It return list
pages = jsonpath.jsonpath(json_response, "total_pages")
print(pages[0])
assert pages[0] == 2

# advanced JSONPATH
first_name = jsonpath.jsonpath(json_response, "data[0].first_name")
print(first_name)

# get all first name in the data
for i in range(0, 3):
    first_name = jsonpath.jsonpath(json_response, "data[" + str(i) + "].first_name")
    print(first_name[0])

first_names = [d['first_name'] for d in json_response["data"]]
print(first_names)

