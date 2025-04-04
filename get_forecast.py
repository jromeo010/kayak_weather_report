import json
import requests


# Load locations from locations.json
with open('locations.json', 'r') as file:
    locations = json.load(file)

# Iterate through each location
for location in locations['locations']:
    print(f"Fetching forecast for {location['name']}...")
    lat = location['latitude']
    lon = location['longitude']

    # Call the points endpoint
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    points_response = requests.get(points_url)
    if points_response.status_code != 200:
        print(f"Failed to fetch points for {lat}, {lon}")
        continue

    points_data = points_response.json()
    grid_id = points_data['properties']['gridId']
    grid_x = points_data['properties']['gridX']
    grid_y = points_data['properties']['gridY']

    # Call the gridpoints endpoint
    gridpoints_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}"
    gridpoints_response = requests.get(gridpoints_url)
    if gridpoints_response.status_code != 200:
        print(f"Failed to fetch gridpoints for {grid_id}, {grid_x}, {grid_y}")
        continue

    gridpoints_data = gridpoints_response.json()
    print(f"Forecast for {lat}, {lon}:")
    
    #print(json.dumps(gridpoints_data['properties']['windDirection'], indent=2))
    print(json.dumps(gridpoints_data['properties']['windSpeed'], indent=2))
    break

#id
#@type
#updateTime
#validTimes
#elevation
#forecastOffice
#gridId
#gridX
#gridY
#temperature
#dewpoint
#maxTemperature
#minTemperature
#relativeHumidity
#apparentTemperature
#wetBulbGlobeTemperature
#heatIndex
#windChill
#skyCover
#windDirection
#windSpeed
#windGust
#weather
#hazards
#probabilityOfPrecipitation
#quantitativePrecipitation
#iceAccumulation
#snowfallAmount
#snowLevel
#ceilingHeight
#visibility
#transportWindSpeed
#transportWindDirection
#mixingHeight
#hainesIndex
#lightningActivityLevel
#twentyFootWindSpeed
#twentyFootWindDirection
#waveHeight
#wavePeriod
#waveDirection
#primarySwellHeight
#primarySwellDirection
#secondarySwellHeight
#secondarySwellDirection
#wavePeriod2
#windWaveHeight
#dispersionIndex
#pressure
#probabilityOfTropicalStormWinds
#probabilityOfHurricaneWinds
#potentialOf15mphWinds
#potentialOf25mphWinds
#potentialOf35mphWinds
#potentialOf45mphWinds
#potentialOf20mphWindGusts
#potentialOf30mphWindGusts
#potentialOf40mphWindGusts
#potentialOf50mphWindGusts
#potentialOf60mphWindGusts
#grasslandFireDangerIndex
#probabilityOfThunder
#davisStabilityIndex
#atmosphericDispersionIndex
#lowVisibilityOccurrenceRiskIndex
#stability
#redFlagThreatIndex

