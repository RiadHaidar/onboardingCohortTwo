#!/usr/bin/env python3
"""
gRPC Weather Server
Implements the WeatherService defined in weather.proto
"""

import grpc
from concurrent import futures
import requests
import os
from dotenv import load_dotenv
import logging
import time

# Import generated protobuf classes
import weather_pb2
import weather_pb2_grpc

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# WeatherAPI.com configuration (same as Flask app)
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_BASE_URL = 'http://api.weatherapi.com/v1/current.json'


class WeatherServiceServicer(weather_pb2_grpc.WeatherServiceServicer):
    """
    Implementation of the WeatherService
    Inherits from the generated base class
    """

    def GetWeather(self, request, context):
        """
        Implement the GetWeather RPC method

        Args:
            request (WeatherRequest): Contains city name
            context: gRPC context for setting status codes and details

        Returns:
            WeatherResponse: Weather data for the requested city
        """
        start_time = time.time()
        logger.info(f"Received GetWeather request for city: {request.city}")

        try:
            # Validate input
            if not request.city.strip():
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('City name cannot be empty')
                return weather_pb2.WeatherResponse()

            city = request.city.strip()

            # Make API call to WeatherAPI.com (same logic as Flask app)
            params = {
                'key': WEATHER_API_KEY,
                'q': city,
                'aqi': 'no'  # We don't need air quality data
            }

            logger.info(f"Calling WeatherAPI.com for city: {city}")
            response = requests.get(WEATHER_API_BASE_URL, params=params, timeout=10)

            if response.status_code == 200:
                weather_data = response.json()

                # Create protobuf response (instead of JSON)
                result = weather_pb2.WeatherResponse()
                result.city = weather_data['location']['name']
                result.country = weather_data['location']['country']
                result.temperature = f"{weather_data['current']['temp_c']}°C"
                result.condition = weather_data['current']['condition']['text']
                result.humidity = f"{weather_data['current']['humidity']}%"
                result.wind_speed = f"{weather_data['current']['wind_kph']} km/h"
                result.last_updated = weather_data['current']['last_updated']

                elapsed_time = time.time() - start_time
                logger.info(f"Successfully processed request for {result.city} in {elapsed_time:.2f}s")
                return result

            elif response.status_code == 400:
                # City not found
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'City "{city}" not found')
                return weather_pb2.WeatherResponse()

            else:
                # WeatherAPI service error
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details('Weather service temporarily unavailable')
                return weather_pb2.WeatherResponse()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling WeatherAPI for city: {request.city}")
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details('Weather service request timed out')
            return weather_pb2.WeatherResponse()

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error calling WeatherAPI for city: {request.city}")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Weather service temporarily unavailable')
            return weather_pb2.WeatherResponse()

        except KeyError as e:
            logger.error(f"Invalid response format from WeatherAPI: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid response from weather service')
            return weather_pb2.WeatherResponse()

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return weather_pb2.WeatherResponse()


def serve():
    """
    Start the gRPC server
    """
    # Check if API key is configured
    if not WEATHER_API_KEY:
        logger.error("WEATHER_API_KEY not found in environment variables")
        logger.error("Please create a .env file with your WeatherAPI.com API key")
        return

    # Create gRPC server with thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add our weather service to the server
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherServiceServicer(), server)

    # Configure server address
    listen_addr = '[::]:50051'  # Listen on all interfaces, port 50051
    server.add_insecure_port(listen_addr)

    # Start the server
    logger.info(f"Starting gRPC Weather Server on {listen_addr}")
    logger.info("API Key configured: ✅")
    logger.info("Server ready to accept connections...")

    server.start()

    try:
        # Keep the server running
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(5)  # Graceful shutdown with 5-second timeout


if __name__ == '__main__':
    serve()