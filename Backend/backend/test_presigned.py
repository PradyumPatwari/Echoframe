import requests

API_KEY = "rd_9b4a064f1e7d0fb8_04cb398ae234b3fb31a24865fea91adc"
url = "https://api.prd.realitydefender.xyz/api/files/aws-presigned"

payload = { "fileName": "test.mp4" }
headers = { "X-API-KEY": API_KEY, "Content-Type": "application/json" }

response = requests.post(url, json=payload, headers=headers)
print(response.json())
