from flask import Flask, jsonify
from flask_cors import CORS
import requests, re
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

H = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/"}

def session():
    s = requests.Session()
    s.get("https://www.nseindia.com", headers=H, timeout=10)
    return s

def amount(text):
    for p in [r'(?:INR|Rs\.?|₹)\s*([\d,]+(?:\.\d+)?)\s*[Cc]r', r'([\d,]+(?:\.\d+)?)\s*[Cc]rore']:
        m = re.search(p, text or "")
        if m:
            return float(m.group(1).replace(",",""))
    return 0

@app.route("/orders")
def orders():
    t = datetime.now()
    fd = (t - timedelta(days=3)).strftime("%d-%m-%Y")
    td = t.strftime("%d-%m-%Y")
    try:
        s = session()
        url = f"https://www.nseindia.com/api/corporate-announcements?index=equities&from_date={fd}&to_date={td}&category=Order%20Win"
        data = s.get(url, headers=H, timeout=15).json()
        res = []
        for i, x in enumerate(data[:30]):
            desc = x.get("desc","") or x.get("subject","")
            res.append({"rank":i+1,"symbol":x.get("symbol",""),"company":x.get("company",""),"date":x.get("date",""),"orderCr":amount(desc),"description":desc[:200]})
        res.sort(key=lambda x: x["orderCr"], reverse=True)
        for i,r in enumerate(res): r["rank"]=i+1
        return jsonify({"success":True,"data":res})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)})

@app.route("/")
def home():
    return "NSE Order Tracker Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
