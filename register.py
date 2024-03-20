import requests
import json

# Define the data to be sent in JSON format
data = {
    "agency_name": "Joe Wakeling News Agency",
    "url": "https://sc21jjfw.pythonanywhere.com",
    "agency_code": "JJW02"
}

# Convert data to JSON string
json_data = json.dumps(data)

# Define the URL to send the POST request to
url = "https://newssites.pythonanywhere.com/api/directory/"

# Send the POST request
response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
print(response.text)

# Check the response status code
if response.status_code == 201:
    print("POST request successful: 201 CREATED")
elif response.status_code == 503:
    print("POST request failed: 503 Service Unavailable")
    print("Reason:", response.text)
else:
    print("POST request failed with status code:", response.status_code)