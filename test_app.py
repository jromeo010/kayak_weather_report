from flask import Flask, render_template_string
import folium
from folium.plugins import MarkerCluster
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

locations = [
    {"name": "Rudee Inlet", "latitude": 36.831456, "longitude": -75.972988, "station_id": "8639208"},
    {"name": "64th street boat ramp", "latitude": 36.891655, "longitude": -76.019413, "station_id": "8638863"},
    {"name": "Lynhaven Inlet", "latitude": 36.907000, "longitude": -76.092662, "station_id": "8638911"},
    {"name": "CBBT", "latitude": 36.921020, "longitude": -76.128294, "station_id": "8638863"},
    {"name": "Kiptopeke", "latitude": 37.165768, "longitude": -75.990170, "station_id": "8632200"},
]

def get_next_saturday():
    today = datetime.utcnow()
    days_ahead = 5 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

def get_tide_predictions(station_id, date):
    api_url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": "predictions",
        "application": "web_services",
        "begin_date": date,
        "end_date": date,
        "datum": "MLLW",
        "station": station_id,
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": "hilo",
        "format": "json",
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    return data.get('predictions', [])

def get_water_temperature(station_id, date):
    api_url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": "water_temperature",
        "application": "web_services",
        "begin_date": date,
        "end_date": date,
        "station": station_id,
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": "6",
        "format": "json",
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    temperatures = data.get('data', [])
    if temperatures:
        return sum(float(temp['v']) for temp in temperatures) / len(temperatures)
    return None

def get_wind_forecast(lat, lon, date):
    api_url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(api_url)
    forecast_url = response.json()['properties']['forecast']
    forecast_response = requests.get(forecast_url)
    periods = forecast_response.json()['properties']['periods']
    for period in periods:
        if date in period['startTime']:
            return period['windSpeed']
    return None

@app.route('/')
def index():
    start_coords = (36.9, -76.0)
    m = folium.Map(location=start_coords, zoom_start=10)
    marker_cluster = MarkerCluster().add_to(m)

    date_obj = get_next_saturday()
    date_str = date_obj.strftime('%Y%m%d')
    readable_date = date_obj.strftime('%A, %B %d, %Y')

    for loc in locations:
        tides = get_tide_predictions(loc['station_id'], date_str)
        water_temp = get_water_temperature(loc['station_id'], date_str)
        wind_forecast = get_wind_forecast(loc['latitude'], loc['longitude'], date_obj.strftime('%Y-%m-%d'))

        tide_list = ''.join([f"<li>{t['t']} ({t['type']})</li>" for t in tides]) if tides else "<li>No tide data</li>"
        popup_html = f"""
        <b>{loc['name']}</b><br>
        <b>{readable_date}</b><br>
        <b>Water Temp:</b> {f"{water_temp:.2f} °F" if water_temp else "N/A"}<br>
        <b>Wind:</b> {wind_forecast if wind_forecast else "N/A"}<br>
        <b>Tides:</b><ul>{tide_list}</ul>
        """

        folium.Marker(
            location=[loc['latitude'], loc['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=loc['name']
        ).add_to(marker_cluster)

    return m._repr_html_()


@app.route('/forecast/<location_name>')
def forecast(location_name):
    loc = next((l for l in locations if l['name'] == location_name), None)
    if not loc:
        return "Location not found", 404

    date_obj = get_next_saturday()
    date_str = date_obj.strftime('%Y%m%d')

    tides = get_tide_predictions(loc['station_id'], date_str)
    water_temp = get_water_temperature(loc['station_id'], date_str)
    wind_forecast = get_wind_forecast(loc['latitude'], loc['longitude'], date_obj.strftime('%Y-%m-%d'))

    forecast_html = f"""
    <h2>Forecast for {loc['name']} ({date_obj.strftime('%A, %B %d, %Y')})</h2>
    <p><strong>Water Temperature:</strong> {f"{water_temp:.2f} °F" if water_temp is not None else "Data not available"}</p>
    <p><strong>Wind Forecast:</strong> {wind_forecast if wind_forecast else "Data not available"}</p>
    <h3>Tide Predictions:</h3>
    <ul>
    {''.join([f"<li>{t['t']} ({t['type']})</li>" for t in tides]) if tides else "<li>No tide data available</li>"}
    </ul>
    <a href='/'>Back to Map</a>
    """
    return render_template_string(forecast_html)


if __name__ == '__main__':
    app.run(debug=True)
