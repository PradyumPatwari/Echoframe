import requests

API_KEY = "rd_9b4a064f1e7d0fb8_04cb398ae234b3fb31a24865fea91adc"
url_to_scan = "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"

api_url = "https://api.prd.realitydefender.xyz/api/scan/url"
headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
payload = {"url": url_to_scan}

resp = requests.post(api_url, headers=headers, json=payload)
print("Status:", resp.status_code)
print("Text:", resp.text)
