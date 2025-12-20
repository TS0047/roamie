# ...existing code...
import os
import re
import json
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

from langchain.tools import tool

def _call_hf_parse(prompt: str) -> str:
    api_key = os.environ.get("HF_API_KEY")
    if not api_key:
        return ""
    model = os.environ.get("HF_MODEL", "google/flan-t5-small")
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200}}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        if isinstance(data, str):
            return data
        return json.dumps(data)
    except Exception:
        return ""

def _regex_parse(query: str) -> Dict[str, Any]:
    out = {"origin": None, "destination": None, "depart_date": None, "return_date": None, "passengers": 1}
    m = re.search(r'from\s+([A-Za-z ]+?)\s+to\s+([A-Za-z ]+?)(?:\s|$)', query, re.IGNORECASE)
    if m:
        out["origin"] = m.group(1).strip()
        out["destination"] = m.group(2).strip()
    m2 = re.search(r'(\d{4}-\d{2}-\d{2})', query)
    if m2:
        out["depart_date"] = m2.group(1)
    m3 = re.search(r'on\s+([A-Za-z]+)\s+(\d{1,2})', query, re.IGNORECASE)
    if m3 and not out["depart_date"]:
        try:
            month = m3.group(1)
            day = int(m3.group(2))
            dt = datetime.strptime(f"{month} {day} {datetime.now().year}", "%B %d %Y")
            out["depart_date"] = dt.date().isoformat()
        except Exception:
            pass
    m4 = re.search(r'(\d+)\s+passengers?', query, re.IGNORECASE)
    if m4:
        out["passengers"] = int(m4.group(1))
    return out

def parse_query(query: str) -> Dict[str, Any]:
    prompt = (
        "Extract origin, destination, depart_date (YYYY-MM-DD if present), return_date (YYYY-MM-DD or null), "
        "passengers (number) from the following user query and output a JSON object with keys "
        "origin,destination,depart_date,return_date,passengers. Query:\n\n" + query
    )
    hf_text = _call_hf_parse(prompt)
    if hf_text:
        jmatch = re.search(r'(\{.*\})', hf_text, re.S)
        try:
            if jmatch:
                return json.loads(jmatch.group(1))
            return json.loads(hf_text)
        except Exception:
            pass
    return _regex_parse(query)

def _mock_flight_results(parsed: Dict[str, Any], max_results: int = 3) -> List[Dict[str, Any]]:
    origin = parsed.get("origin") or "OriginCity"
    destination = parsed.get("destination") or "DestinationCity"
    depart_date = parsed.get("depart_date") or (datetime.now() + timedelta(days=7)).date().isoformat()
    results = []
    airlines = ["AirFast", "SkyWay", "CloudNine", "JetQuick"]
    for i in range(max_results):
        depart_time = datetime.strptime(depart_date, "%Y-%m-%d") + timedelta(hours=6 + i*3)
        duration_mins = random.choice([90, 120, 150, 180])
        arrive_time = depart_time + timedelta(minutes=duration_mins)
        price = round(random.uniform(80, 650), 2)
        results.append({
            "flight_id": f"FL{random.randint(1000,9999)}",
            "airline": random.choice(airlines),
            "origin": origin,
            "destination": destination,
            "depart": depart_time.isoformat(sep=' '),
            "arrive": arrive_time.isoformat(sep=' '),
            "duration_min": duration_mins,
            "price_usd": price,
            "stops": 0
        })
    return results

def call_tool(tool_obj, *args, **kwargs):
    """Call a langchain-decorated tool (StructuredTool) or a plain function."""
    if callable(tool_obj):
        try:
            return tool_obj(*args, **kwargs)
        except TypeError:
            pass
    if hasattr(tool_obj, "func") and callable(tool_obj.func):
        return tool_obj.func(*args, **kwargs)
    if hasattr(tool_obj, "run") and callable(tool_obj.run):
        try:
            return tool_obj.run(*args, **kwargs)
        except TypeError:
            if args:
                return tool_obj.run(args[0])
            raise
    raise TypeError("Tool object is not callable")

@tool
def search_flights(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Search for flights given a natural language query.
    Uses Hugging Face model (if HF_API_KEY set) to parse query, otherwise a regex fallback.
    Returns a dict with parsed query and a list of flight options.
    """
    parsed = parse_query(query)
    flights = _mock_flight_results(parsed, max_results=max_results)
    return {"parsed": parsed, "flights": flights}

def _pretty_print_results(resp: Dict[str, Any]):
    parsed = resp.get("parsed", {})
    flights = resp.get("flights", [])
    print("\nParsed query:", parsed)
    if not flights:
        print("No flights found.")
        return
    print("\nAvailable flights:")
    for idx, f in enumerate(flights, start=1):
        print(f"[{idx}] {f['airline']} {f['flight_id']} | {f['origin']} -> {f['destination']} | "
              f"Depart: {f['depart']} Arrive: {f['arrive']} | ${f['price_usd']} | {f['duration_min']}m")

def _book_flight(flight: Dict[str, Any], passenger_name: str) -> Dict[str, Any]:
    confirmation = f"BK{int(time.time())}{random.randint(100,999)}"
    return {
        "confirmation_id": confirmation,
        "flight_id": flight["flight_id"],
        "passenger": passenger_name,
        "price_usd": flight["price_usd"],
        "status": "CONFIRMED"
    }

if __name__ == "__main__":
    # For inter-agent communication, just run a sample query and print the result (no CLI loop)
    sample_query = "Find flights from Mumbai to Paris on 2026-01-10 for 2 passengers"
    resp = call_tool(search_flights, sample_query, max_results=4)
    _pretty_print_results(resp)