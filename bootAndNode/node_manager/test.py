import requests

url = 'http://localhost:8889/'  # Adjust the URL as needed
data = {'port': 2828}  # Example JSON data

response = requests.post(url, json=data)
print(response.json())  # Print the response from the server
