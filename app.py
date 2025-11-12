from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# WeatherAPI.com configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_BASE_URL = 'http://api.weatherapi.com/v1/current.json'

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Simple Weather API",
        "usage": "POST /weather with {\"city\": \"city_name\"}"
    })

@app.route('/weather', methods=['POST'])
def get_weather():
    try:
        # Get city from request
        data = request.get_json()
        if not data or 'city' not in data:
            return jsonify({'error': 'City name is required'}), 400

        city = data['city']

        # Make API call to weatherapi.com
        params = {
            'key': WEATHER_API_KEY,
            'q': city,
            'aqi': 'no'  # We don't need air quality data
        }

        response = requests.get(WEATHER_API_BASE_URL, params=params)

        if response.status_code == 200:
            weather_data = response.json()

            # Extract relevant information
            result = {
                'city': weather_data['location']['name'],
                'country': weather_data['location']['country'],
                'temperature': f"{weather_data['current']['temp_c']}°C",
                'condition': weather_data['current']['condition']['text'],
                'humidity': f"{weather_data['current']['humidity']}%",
                'wind_speed': f"{weather_data['current']['wind_kph']} km/h",
                'last_updated': weather_data['current']['last_updated']
            }

            return jsonify(result)

        elif response.status_code == 400:
            return jsonify({'error': 'City not found'}), 404
        else:
            return jsonify({'error': 'Weather service unavailable'}), 503

    except requests.exceptions.RequestException:
        return jsonify({'error': 'Failed to fetch weather data'}), 503
    except KeyError as e:
        return jsonify({'error': f'Invalid response format: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'weather-api'})

if __name__ == '__main__':
    if not WEATHER_API_KEY:
        print("Warning: WEATHER_API_KEY not found in environment variables")
        print("Please create a .env file with your API key")

    app.run(debug=True, port=8000, host='0.0.0.0')