# weather_exporter.py
from prometheus_client import start_http_server, Gauge
import requests
import time
import urllib.parse

API_KEY = "11380c68f474f3dc58c75f1037de5a95"
CITIES = ["Astana", "Almaty", "London","Kabul"]

# Labeled gauges
temperature = Gauge('weather_temperature_celsius', 'Current temperature in Celsius', ['city'])
humidity    = Gauge('weather_humidity_percent',   'Current humidity in percent',     ['city'])
pressure    = Gauge('weather_pressure_hpa',       'Atmospheric pressure in hPa',     ['city'])
wind_speed  = Gauge('weather_wind_speed_mps',     'Wind speed in m/s',               ['city'])
clouds      = Gauge('weather_clouds_percent',     'Cloudiness percent',              ['city'])
visibility  = Gauge('weather_visibility_m',       'Visibility in meters',            ['city'])
feels_like  = Gauge('weather_feels_like_celsius', 'Feels like temperature',          ['city'])
sunrise     = Gauge('weather_sunrise_unix',       'Sunrise time (UNIX)',             ['city'])
sunset      = Gauge('weather_sunset_unix',        'Sunset time (UNIX)',              ['city'])
temp_diff   = Gauge('weather_temp_difference',    'Difference between temp and feels_like', ['city'])

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "weather-exporter/1.0"})

def fetch_weather(city: str):
    city_q = urllib.parse.quote(city)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_q}&appid={API_KEY}&units=metric"
    try:
        r = SESSION.get(url, timeout=8)
        if r.status_code != 200:
            print(f"[WARN] {city}: HTTP {r.status_code} {r.text[:160]}")
            return
        data = r.json()

        main = data.get('main', {})
        wind = data.get('wind', {})
        clouds_obj = data.get('clouds', {})
        sys_obj = data.get('sys', {})

        if 'temp' not in main:
            print(f"[WARN] {city}: missing 'temp' in payload: {data}")
            return

        t  = float(main.get('temp', 0))
        fh = float(main.get('feels_like', t))
        h  = float(main.get('humidity', 0))
        p  = float(main.get('pressure', 0))
        w  = float(wind.get('speed', 0))
        c  = float(clouds_obj.get('all', 0))
        v  = float(data.get('visibility', 0))
        sr = float(sys_obj.get('sunrise', 0))
        ss = float(sys_obj.get('sunset', 0))

        temperature.labels(city=city).set(t)
        feels_like.labels(city=city).set(fh)
        humidity.labels(city=city).set(h)
        pressure.labels(city=city).set(p)
        wind_speed.labels(city=city).set(w)
        clouds.labels(city=city).set(c)
        visibility.labels(city=city).set(v)
        sunrise.labels(city=city).set(sr)
        sunset.labels(city=city).set(ss)
        temp_diff.labels(city=city).set(t - fh)

        print(f"[OK] {city}: temp {t}°C, feels {fh}°C, wind {w} m/s")

    except requests.RequestException as e:
        print(f"[ERR] {city}: network error: {e}")
    except Exception as e:
        print(f"[ERR] {city}: unexpected error: {e}")

if __name__ == "__main__":
    port = 8010
    print(f"Starting exporter on :{port}/metrics ...")
    start_http_server(port)
    while True:
        for c in CITIES:
            fetch_weather(c)
        print("Cycle complete. Sleeping 20s...\n")
        time.sleep(20)
