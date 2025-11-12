#!/usr/bin/env python3
"""
gRPC Weather Client
Connects to the gRPC Weather Server and makes weather requests
"""

import grpc
import sys
import argparse
import json
import time

# Import generated protobuf classes
import weather_pb2
import weather_pb2_grpc


class WeatherClient:
    """
    gRPC Weather Client
    """

    def __init__(self, server_address='localhost:50051'):
        """
        Initialize the weather client

        Args:
            server_address (str): Address of the gRPC server
        """
        self.server_address = server_address
        self.channel = None
        self.stub = None

    def connect(self):
        """
        Connect to the gRPC server
        """
        try:
            print(f"🌍 Connecting to gRPC Weather Server at {self.server_address}...")
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = weather_pb2_grpc.WeatherServiceStub(self.channel)

            # Test connection with a timeout
            grpc.channel_ready_future(self.channel).result(timeout=5)
            print("✅ Connected successfully!")
            return True

        except grpc.FutureTimeoutError:
            print(f"❌ Connection timeout - server not responding at {self.server_address}")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def get_weather(self, city_name: str, timeout: float = 10.0):
        """
        Get weather information for a city

        Args:
            city_name (str): Name of the city
            timeout (float): Request timeout in seconds

        Returns:
            WeatherResponse or None: Weather data or None if failed
        """
        if not self.stub:
            print("❌ Not connected to server. Call connect() first.")
            return None

        try:
            # Create protobuf request
            request = weather_pb2.WeatherRequest()
            request.city = city_name

            print(f"🏙️  Requesting weather for: {city_name}")
            start_time = time.time()

            # Make gRPC call with timeout
            response = self.stub.GetWeather(request, timeout=timeout)

            elapsed_time = time.time() - start_time
            print(f"⚡ Response received in {elapsed_time:.2f}s")

            return response

        except grpc.RpcError as e:
            # Handle gRPC specific errors
            status_code = e.code()
            details = e.details()

            error_messages = {
                grpc.StatusCode.NOT_FOUND: "🏙️ City not found",
                grpc.StatusCode.INVALID_ARGUMENT: "❌ Invalid city name",
                grpc.StatusCode.UNAVAILABLE: "🌐 Weather service unavailable",
                grpc.StatusCode.DEADLINE_EXCEEDED: "⏰ Request timeout",
                grpc.StatusCode.INTERNAL: "🔧 Server error"
            }

            error_msg = error_messages.get(status_code, "❌ Unknown error")
            print(f"{error_msg}: {details}")
            return None

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None

    def print_weather(self, response):
        """
        Print weather response in a formatted way

        Args:
            response (WeatherResponse): Weather response from server
        """
        if not response:
            return

        print("\n" + "=" * 50)
        print(f"📍 Location: {response.city}, {response.country}")
        print(f"🌡️  Temperature: {response.temperature}")
        print(f"☁️  Condition: {response.condition}")
        print(f"💧 Humidity: {response.humidity}")
        print(f"💨 Wind Speed: {response.wind_speed}")
        print(f"🕐 Last Updated: {response.last_updated}")
        print("=" * 50)

    def get_weather_json(self, city_name: str):
        """
        Get weather as JSON (for compatibility with REST clients)

        Args:
            city_name (str): Name of the city

        Returns:
            dict: Weather data as dictionary
        """
        response = self.get_weather(city_name)
        if response:
            return {
                'city': response.city,
                'country': response.country,
                'temperature': response.temperature,
                'condition': response.condition,
                'humidity': response.humidity,
                'wind_speed': response.wind_speed,
                'last_updated': response.last_updated
            }
        return None

    def close(self):
        """
        Close the connection to the server
        """
        if self.channel:
            self.channel.close()
            print("🔌 Connection closed")


def interactive_mode(client):
    """
    Interactive mode for testing the client
    """
    print("\n🌤️  Welcome to gRPC Weather Client (Interactive Mode)")
    print("Type city names to get weather, or 'quit' to exit")
    print("-" * 50)

    while True:
        try:
            city = input("\nEnter city name: ").strip()

            if city.lower() in ['quit', 'exit', 'q']:
                break

            if not city:
                print("Please enter a valid city name")
                continue

            response = client.get_weather(city)
            if response:
                client.print_weather(response)

        except KeyboardInterrupt:
            break
        except EOFError:
            break

    print("\n👋 Goodbye!")


def main():
    """
    Main function with command line interface
    """
    parser = argparse.ArgumentParser(description='gRPC Weather Client')
    parser.add_argument('--server', default='localhost:50051',
                        help='gRPC server address (default: localhost:50051)')
    parser.add_argument('--city', help='City name to get weather for')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON format')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode')

    args = parser.parse_args()

    # Create and connect client
    client = WeatherClient(args.server)

    if not client.connect():
        sys.exit(1)

    try:
        if args.interactive or not args.city:
            # Interactive mode
            interactive_mode(client)
        else:
            # Single request mode
            if args.json:
                result = client.get_weather_json(args.city)
                if result:
                    print(json.dumps(result, indent=2))
            else:
                response = client.get_weather(args.city)
                if response:
                    client.print_weather(response)

    finally:
        client.close()


if __name__ == '__main__':
    main()