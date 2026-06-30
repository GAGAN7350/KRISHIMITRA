import urllib.request
import json

key = "AQ.Ab8RN6K0LD3-M-KnrkTe1YFHr-_btlPtIAl8Vw-jWqi4vjod8A"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

print("Testing API key...")
try:
    r = urllib.request.urlopen(url, timeout=10)
    data = json.loads(r.read())
    print("KEY WORKS! Available models:")
    for m in data.get("models", [])[:5]:
        print(" -", m["name"])
except Exception as e:
    print("KEY FAILED:", e)

input("\nPress Enter to close...")
