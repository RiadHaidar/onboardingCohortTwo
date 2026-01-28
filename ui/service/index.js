import React, { useState } from "react";
import StyledButton from "@integratedComponents/StyledButton";
import OutlinedTextArea from "@commonComponents/OutlinedTextArea";
// Import the generated proto files
import weather_pb from "./weather_pb.js";
import { WeatherService } from "./weather_pb_service.js";
import "./style.css";

/**
 * Main UI component for the Weather Service
 *
 * @param {Object} props Component props
 * @param {Object} props.serviceClient The gRPC service client provided by the platform
 * @param {boolean} props.isComplete Whether the service is complete
 */
const ServiceUI = ({ serviceClient, isComplete }) => {
  const [output, setOutput] = useState();

  /**
   * Input component for city input
   */
  const ServiceInput = () => {
    const [city, setCity] = useState("");

    // Check if the input is valid for submission
    const isAllowedToRun = () => {
      return !!city?.trim();
    };

    // Handle response from the service
    const onActionEnd = (response) => {
      const { message, status, statusMessage } = response;

      // Debug logging to see the exact structure of the response
      console.log('gRPC Response:', response);
      console.log('Response message:', message);
      console.log('Response status:', status);

      if (status !== 0) {
        setOutput(`Error: ${statusMessage}`);
        return;
      }

      // In gRPC-Web, the actual response object is in the message property
      setOutput(response);
    };

    // Submit the city to the gRPC service
    const submitAction = () => {
      try {
        // Get the method descriptor for GetWeather
        const methodDescriptor = WeatherService.GetWeather;

        // Create a new request object
        const request = new weather_pb.WeatherRequest();

        // Set the city name
        request.setCity(city.trim());

        console.log('Sending request:', request.toObject());

        // Define the request properties
        const props = {
          request,
          preventCloseServiceOnEnd: false,
          onEnd: onActionEnd,
        };

        // Make the RPC call using the platform's serviceClient
        serviceClient.unary(methodDescriptor, props);

        // Clear the input field
        setCity("");
      } catch (err) {
        console.error('Error in submitAction:', err);
        setOutput(`Client error: ${err.message}`);
      }
    };

    const handleInputChange = (event) => {
      setCity(event.target.value);
    };

    const handleKeyPress = (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        if (isAllowedToRun()) {
          submitAction();
        }
      }
    };

    return (
      <div className={"content-box"}>
        <h4>{"Input"}</h4>
        <div className={"content-box"}>
          <div className="input-group">
            <OutlinedTextArea
              label="City Name"
              value={city}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Enter city name (e.g., London, New York, Tokyo)"
              rows={1}
            />
          </div>
        </div>
        <div className={"content-box"}>
          <StyledButton
            btnText={"Get Weather"}
            variant={"contained"}
            onClick={submitAction}
            disabled={!isAllowedToRun()}
          />
        </div>
      </div>
    );
  };

  /**
   * Output component for displaying weather response
   */
  const ServiceOutput = () => {
    if (!output) {
      return (
        <div className={"content-box"}>
          <h4>
            {"Waiting for response..."}
          </h4>
        </div>
      );
    }

    // Handle string output (likely an error message)
    if (typeof output === 'string') {
      return (
        <div className={"content-box"}>
          <h4>
            {"Output"}
          </h4>
          <div className={"content-box"}>
            <div className="weather-response">
              <OutlinedTextArea
                label="Response"
                value={output}
                disabled={true}
                multiline={true}
                rows={6}
              />
            </div>
          </div>
        </div>
      );
    }

    // For gRPC responses, output is the response message from onActionEnd
    console.log('ServiceOutput received output:', output);

    // The response structure from gRPC-Web
    // The actual WeatherResponse object is in the message property
    const responseObj = output.message;

    // Check if we have a valid response object
    if (!responseObj) {
      return (
        <div className={"content-box"}>
          <h4>{"Output"}</h4>
          <div className={"content-box"}>
            <div className="weather-response">
              <OutlinedTextArea
                label="Response"
                value="No valid response received from the server."
                disabled={true}
                multiline={true}
                rows={6}
              />
            </div>
          </div>
        </div>
      );
    }

    // Extract weather data using the protobuf getters
    const city = responseObj.getCity ? responseObj.getCity() : "Unknown";
    const country = responseObj.getCountry ? responseObj.getCountry() : "";
    const temperature = responseObj.getTemperature ? responseObj.getTemperature() : "";
    const condition = responseObj.getCondition ? responseObj.getCondition() : "";
    const humidity = responseObj.getHumidity ? responseObj.getHumidity() : "";
    const windSpeed = responseObj.getWindSpeed ? responseObj.getWindSpeed() : "";
    const lastUpdated = responseObj.getLastUpdated ? responseObj.getLastUpdated() : "";

    // Format the weather information display
    const weatherInfo = `Location: ${city}, ${country}
Temperature: ${temperature}
Condition: ${condition}
Humidity: ${humidity}
Wind Speed: ${windSpeed}
Last Updated: ${lastUpdated}`;

    return (
      <div className={"content-box"}>
        <h4>
          {"Weather Information"}
        </h4>
        <div className={"content-box"}>
          <div className="weather-card">
            <div className="weather-header">
              <h3>{city}, {country}</h3>
            </div>
            <div className="weather-details">
              <div className="weather-main">
                <div className="temperature">{temperature}</div>
                <div className="condition">{condition}</div>
              </div>
              <div className="weather-info">
                <div className="info-item">
                  <span className="info-label">Humidity:</span>
                  <span className="info-value">{humidity}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Wind Speed:</span>
                  <span className="info-value">{windSpeed}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Last Updated:</span>
                  <span className="info-value">{lastUpdated}</span>
                </div>
              </div>
            </div>
          </div>
          <OutlinedTextArea
            label="Raw Response"
            value={weatherInfo}
            disabled={true}
            multiline={true}
            rows={8}
          />
        </div>
      </div>
    );
  };

  return (
    <div className={"service-container"}>
      <div className={"service-header"}>
        <h2>{"Weather Information Service"}</h2>
        <p>{"Get current weather information for any city around the world."}</p>
      </div>

      {!isComplete ? <ServiceInput /> : <ServiceOutput />}
    </div>
  );
};

export default ServiceUI;
