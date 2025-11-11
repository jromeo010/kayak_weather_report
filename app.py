import json
import folium
from folium import plugins
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import math

app = Flask(__name__)

# Load the kayak forecast data
with open('kayak_forecast.json', 'r', encoding='utf-8') as f:
    forecast_data = json.load(f)

def get_color_class(color):
    """Map color rating to CSS color"""
    color_map = {
        'green': '#2ecc71',
        'yellow': '#f39c12',
        'red': '#e74c3c'
    }
    return color_map.get(color, '#95a5a6')

def parse_wind_speed(wind_speed_str):
    """Extract wind speed as a number from strings like '10-12 mph'"""
    try:
        # Extract the first number from the wind speed string
        import re
        match = re.search(r'(\d+)', wind_speed_str)
        if match:
            return int(match.group(1))
        return 0
    except:
        return 0

def wind_direction_to_bearing(direction):
    """Convert wind direction (N, NW, etc.) to bearing in degrees"""
    directions = {
        'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
        'S': 180, 'SW': 225, 'W': 270, 'NW': 315
    }
    return directions.get(direction, 0)

def get_locations_by_day(day):
    """Filter locations by day"""
    return [loc for loc in forecast_data['locations'] if loc['day'] == day]

def create_map(day):
    """Create a Folium map with locations for the given day"""
    # Get locations for this day
    locations = get_locations_by_day(day)
    
    # Calculate center of map
    if locations:
        lats = [loc['coordinates'][0] for loc in locations]
        lons = [loc['coordinates'][1] for loc in locations]
        center_lat = (max(lats) + min(lats)) / 2
        center_lon = (max(lons) + min(lons)) / 2
    else:
        center_lat, center_lon = 36.9, -76.2
    
    # Create map
    map_obj = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles='OpenStreetMap'
    )
    
    # Add wind arrows for each location
    for loc in locations:
        lat, lon = loc['coordinates']
        wind_direction = loc['hover_facts']['wind_direction']
        wind_speed = parse_wind_speed(loc['hover_facts']['wind_speed'])
        bearing = wind_direction_to_bearing(wind_direction)
        
        # Create wind arrow - scale the arrow size based on wind speed
        arrow_length = min(wind_speed / 5, 0.08)  # Scale arrow by wind speed
        
        # Calculate end point of arrow based on bearing
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        # Rough conversion for lat/lon delta
        end_lat = lat + arrow_length * math.cos(bearing_rad) * 0.85
        end_lon = lon + arrow_length * math.sin(bearing_rad)
        
        # Color arrow by wind speed intensity
        if wind_speed > 14:
            arrow_color = '#e74c3c'  # Red for strong winds
        elif wind_speed > 11:
            arrow_color = '#f39c12'  # Orange for moderate winds
        else:
            arrow_color = '#3498db'  # Blue for light winds
        
        # Add arrow as a line with arrowhead
        folium.PolyLine(
            locations=[[lat, lon], [end_lat, end_lon]],
            color=arrow_color,
            weight=3,
            opacity=0.7,
            popup=f"Wind: {loc['hover_facts']['wind_speed']} {wind_direction}"
        ).add_to(map_obj)
        
        # Add arrowhead (small triangle at end point)
        folium.CircleMarker(
            location=[end_lat, end_lon],
            radius=4,
            color=arrow_color,
            fill=True,
            fillColor=arrow_color,
            fillOpacity=0.8,
            weight=0
        ).add_to(map_obj)
    
    # Add markers for each location
    for loc in locations:
        lat, lon = loc['coordinates']
        color = get_color_class(loc['color'])
        
        # Create popup HTML with detailed information
        popup_html = f"""
        <div style="font-family: Arial; width: 280px;">
            <h4 style="margin: 0 0 8px 0; color: #2c3e50;">{loc['name']}</h4>
            <p style="margin: 0 0 8px 0; font-weight: bold; color: #34495e;">
                Rating: <span style="color: {color};">●</span> {loc['rating'].upper()}
            </p>
            <hr style="margin: 8px 0;">
            <p style="margin: 0 0 8px 0; font-size: 12px; line-height: 1.5;">
                <strong>Summary:</strong><br>{loc['summary']}
            </p>
            <hr style="margin: 8px 0;">
            <table style="width: 100%; font-size: 11px;">
                <tr><td><strong>High Tide:</strong></td><td>{loc['hover_facts']['high_tide']}</td></tr>
                <tr><td><strong>Low Tide:</strong></td><td>{loc['hover_facts']['low_tide']}</td></tr>
                <tr><td><strong>Wind:</strong></td><td>{loc['hover_facts']['wind_speed']} {loc['hover_facts']['wind_direction']}</td></tr>
                <tr><td><strong>Water Temp:</strong></td><td>{loc['hover_facts']['water_temp']}</td></tr>
                <tr><td><strong>Current:</strong></td><td>{loc['hover_facts']['current_speed']}</td></tr>
            </table>
            <hr style="margin: 8px 0;">
            <p style="margin: 0; font-size: 11px;">
                <strong>Notes:</strong><br>
                {' • '.join(loc['hover_facts']['extra_notes'])}
            </p>
        </div>
        """
        
        # Add circle marker with color based on rating
        folium.CircleMarker(
            location=[lat, lon],
            radius=15,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=2,
            tooltip=f"{loc['name']} - {loc['rating'].upper()}"
        ).add_to(map_obj)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 10px; width: 240px; height: 200px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 10px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.2); overflow-y: auto;">
        <p style="margin: 0 0 10px 0; font-weight: bold; border-bottom: 2px solid #ecf0f1; padding-bottom: 8px;">Forecast Rating</p>
        <p style="margin: 5px 0;"><span style="color: #2ecc71; font-size: 16px;">●</span> Good</p>
        <p style="margin: 5px 0;"><span style="color: #f39c12; font-size: 16px;">●</span> Okay</p>
        <p style="margin: 5px 0;"><span style="color: #e74c3c; font-size: 16px;">●</span> Bad</p>
        <p style="margin: 12px 0 8px 0; font-weight: bold; border-top: 2px solid #ecf0f1; border-bottom: 2px solid #ecf0f1; padding: 8px 0;">Wind Speed</p>
        <p style="margin: 5px 0;"><span style="color: #3498db; font-size: 14px;">━→</span> Light (≤11 mph)</p>
        <p style="margin: 5px 0;"><span style="color: #f39c12; font-size: 14px;">━→</span> Moderate (12-14 mph)</p>
        <p style="margin: 5px 0;"><span style="color: #e74c3c; font-size: 14px;">━→</span> Strong (≥15 mph)</p>
    </div>
    '''
    map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    return map_obj

@app.route('/')
def index():
    """Render the main page"""
    report_generated = forecast_data.get('report_generated_for', 'Unknown')
    return render_template('index.html', report_generated=report_generated)

@app.route('/map/<day>')
def get_map(day):
    """Get map for a specific day"""
    if day not in ['Saturday', 'Sunday']:
        return jsonify({'error': 'Invalid day'}), 400
    
    map_obj = create_map(day)
    map_html = map_obj._repr_html_()
    return jsonify({'map_html': map_html})

@app.route('/api/locations/<day>')
def get_locations(day):
    """Get all locations for a specific day"""
    if day not in ['Saturday', 'Sunday']:
        return jsonify({'error': 'Invalid day'}), 400
    
    locations = get_locations_by_day(day)
    return jsonify({
        'day': day,
        'count': len(locations),
        'locations': locations
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
