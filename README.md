# Simple Weather API

A Flask-based REST API that provides current weather information for any city using WeatherAPI.com.

## Features

- Get current weather by city name
- Simple JSON response format
- Error handling for invalid cities
- Health check endpoint

## Setup

1. **Get API Key**
   - Sign up at [WeatherAPI.com](https://www.weatherapi.com/signup.aspx)
   - Get your free API key

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

4. **Run the Server**
   ```bash
   python app.py
   ```

## API Usage

### Get Weather
```bash
curl -X POST http://localhost:5000/weather \
  -H "Content-Type: application/json" \
  -d '{"city": "London"}'
```

**Response:**
```json
{
  "city": "London",
  "country": "United Kingdom",
  "temperature": "15°C",
  "condition": "Partly cloudy",
  "humidity": "72%",
  "wind_speed": "13 km/h",
  "last_updated": "2024-11-09 14:30"
}
```

### Health Check
```bash
curl http://localhost:5000/health
```

## Endpoints

- `GET /` - API information
- `POST /weather` - Get weather by city
- `GET /health` - Health check# onboardingCohortTwo
# onboardingCohortTwo
# onboardingCohortTwo
