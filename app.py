import json, os
from flask import Flask, render_template
from redis import Redis
import requests

app = Flask(__name__)
redis = Redis(host="redis", port=6379, decode_responses=True)

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
LAT       = os.getenv("LAT", "-22.2758")
LON       = os.getenv("LON", "166.4579")
TIMEZONE  = os.getenv("TIMEZONE", "Pacific/Noumea")
CACHE_TTL = int(os.getenv("CACHE_TTL", "30"))

@app.route("/")
def index():
    visits = redis.incr("hits")

    weather = redis.get("weather")
    if weather is None:
        params = {
            "latitude": LAT,
            "longitude": LON,
            "current_weather": "true",  # récupère température, vent
            "hourly": "precipitation",  # pour la pluie
            "timezone": TIMEZONE
        }
        r = requests.get(WEATHER_URL, params=params, timeout=10)
        r.raise_for_status()
        print("Data fetched from API.......")
        redis.set("weather", json.dumps(r.json()), ex=CACHE_TTL)
        data = r.json()
    else:
        data = json.loads(weather)

    current = data["current_weather"]
    # récupération de la pluie si disponible dans hourly
    rain = None
    if "hourly" in data and "precipitation" in data["hourly"]:
        # on prend la première valeur actuelle
        rain = data["hourly"]["precipitation"][0]

    return render_template(
        "index.html",
        visits=visits,
        temperature=current["temperature"],
        wind_speed=current["windspeed"],
        wind_direction=current["winddirection"],
        rain=rain
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
