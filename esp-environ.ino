#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// =====================================================
// Wi-Fi
// =====================================================

const char *ssid = "Excitel_ 2.4";
const char *password = "@Udit1588";

// =====================================================
// API
// =====================================================

const String apiToken = "wbQHFeCx";
const String apiUrl = "https://smarthive-v2.onrender.com/update";

// =====================================================
// SENSOR PINS
// =====================================================

// MQ sensors must be on ADC1 pins (GPIO 32-39). ADC2 pins (e.g. 25/26/27)
// can't be read while Wi-Fi is on and return 0 / garbage.
#define MQ135_PIN 34
#define MQ2_PIN   35
#define DHT_PIN   25
#define DHT_TYPE  DHT11

DHT dht(DHT_PIN, DHT_TYPE);

// =====================================================
// SETTINGS
// =====================================================

unsigned long lastTime = 0;
unsigned long timerDelay = 10000;   // 10 seconds

#define ADC_MAX 4095.0
#define ADC_VOLTAGE 3.3

// Render only accepts HTTPS - a plain WiFiClient gets
// "400 The plain HTTP request was sent to HTTPS port".
WiFiClientSecure wifiClient;


// =====================================================
// READ AVERAGE ADC
// =====================================================

int readAverageADC(int pin)
{
  long total = 0;

  // Take 20 readings to reduce noise
  for (int i = 0; i < 20; i++)
  {
    total += analogRead(pin);
    delay(5);
  }

  return total / 20;
}


// =====================================================
// ADC TO VOLTAGE
// =====================================================

float adcToVoltage(int adc)
{
  return (adc / ADC_MAX) * ADC_VOLTAGE;
}


// =====================================================
// NORMALIZED SENSOR LEVEL
// 0 - 100 %
// =====================================================

float sensorPercentage(int adc)
{
  float percentage = (adc / ADC_MAX) * 100.0;

  if (percentage < 0)
    percentage = 0;

  if (percentage > 100)
    percentage = 100;

  return percentage;
}


// =====================================================
// MQ-135 AIR QUALITY LEVEL
// =====================================================

String getMQ135Level(float percentage)
{
  if (percentage < 20)
    return "GOOD";

  else if (percentage < 40)
    return "MODERATE";

  else if (percentage < 60)
    return "POOR";

  else if (percentage < 80)
    return "VERY POOR";

  else
    return "HAZARDOUS";
}


// =====================================================
// MQ-2 GAS / SMOKE LEVEL
// =====================================================

String getMQ2Level(float percentage)
{
  if (percentage < 20)
    return "LOW";

  else if (percentage < 40)
    return "MODERATE";

  else if (percentage < 60)
    return "HIGH";

  else if (percentage < 80)
    return "VERY HIGH";

  else
    return "CRITICAL";
}


// =====================================================
// WIFI CONNECTION
// =====================================================

void connectWiFi()
{
  if (WiFi.status() == WL_CONNECTED)
    return;

  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 30)
  {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println();
    Serial.println("Wi-Fi Connected!");

    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
  }
  else
  {
    Serial.println();
    Serial.println("Wi-Fi connection failed.");
  }
}


// =====================================================
// SETUP
// =====================================================

void setup()
{
  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("========================================");
  Serial.println("     ESP32 ENVIRONMENT MONITOR");
  Serial.println("========================================");

  // ADC configuration
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  // Sensor pins
  pinMode(MQ135_PIN, INPUT);
  pinMode(MQ2_PIN, INPUT);

  // DHT
  dht.begin();

  // Wi-Fi
  connectWiFi();

  // HTTPS without certificate pinning
  wifiClient.setInsecure();

  Serial.println("Sensor Node Ready!");
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
  if (millis() - lastTime >= timerDelay)
  {
    lastTime = millis();

    // -------------------------------------------------
    // Wi-Fi
    // -------------------------------------------------

    if (WiFi.status() != WL_CONNECTED)
    {
      Serial.println("Wi-Fi disconnected!");
      connectWiFi();
    }

    // -------------------------------------------------
    // DHT11
    // -------------------------------------------------

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity))
    {
      Serial.println("DHT11 reading failed!");
      return;
    }

    // -------------------------------------------------
    // MQ-135
    // -------------------------------------------------

    int mq135Raw = readAverageADC(MQ135_PIN);

    float mq135Voltage = adcToVoltage(mq135Raw);

    float mq135Percent = sensorPercentage(mq135Raw);

    String mq135Level = getMQ135Level(mq135Percent);

    // -------------------------------------------------
    // MQ-2
    // -------------------------------------------------

    int mq2Raw = readAverageADC(MQ2_PIN);

    float mq2Voltage = adcToVoltage(mq2Raw);

    float mq2Percent = sensorPercentage(mq2Raw);

    String mq2Level = getMQ2Level(mq2Percent);

    // =================================================
    // SERIAL OUTPUT
    // =================================================

    Serial.println();
    Serial.println("========================================");
    Serial.println("          SENSOR READINGS");
    Serial.println("========================================");

    // DHT11
    Serial.println("\n[DHT11]");

    Serial.print("Temperature : ");
    Serial.print(temperature, 2);
    Serial.println(" °C");

    Serial.print("Humidity    : ");
    Serial.print(humidity, 2);
    Serial.println(" %");

    // MQ135
    Serial.println("\n[MQ-135]");

    Serial.print("Raw ADC     : ");
    Serial.println(mq135Raw);

    Serial.print("Voltage     : ");
    Serial.print(mq135Voltage, 3);
    Serial.println(" V");

    Serial.print("Level       : ");
    Serial.print(mq135Percent, 1);
    Serial.println(" %");

    Serial.print("Air Quality : ");
    Serial.println(mq135Level);

    Serial.println("Sensitive to:");
    Serial.println("CO2 / CO / NH3 / NOx / Alcohol / Benzene");

    // MQ2
    Serial.println("\n[MQ-2]");

    Serial.print("Raw ADC     : ");
    Serial.println(mq2Raw);

    Serial.print("Voltage     : ");
    Serial.print(mq2Voltage, 3);
    Serial.println(" V");

    Serial.print("Level       : ");
    Serial.print(mq2Percent, 1);
    Serial.println(" %");

    Serial.print("Gas Level   : ");
    Serial.println(mq2Level);

    Serial.println("Sensitive to:");
    Serial.println("LPG / Propane / Methane / Hydrogen / Smoke");

    Serial.println("========================================");


    // =================================================
    // JSON
    // =================================================

    // Backend stores only numeric pins D1..D8 - the text levels
    // (GOOD / HIGH ...) stay on Serial; derive them from D4 / D7.
    StaticJsonDocument<512> jsonDoc;

    // DHT11
    jsonDoc["D1"] = temperature;
    jsonDoc["D2"] = humidity;

    // MQ-135
    jsonDoc["D3"] = mq135Raw;
    jsonDoc["D4"] = mq135Percent;
    jsonDoc["D5"] = mq135Voltage;

    // MQ-2
    jsonDoc["D6"] = mq2Raw;
    jsonDoc["D7"] = mq2Percent;
    jsonDoc["D8"] = mq2Voltage;

    String jsonPayload;

    serializeJson(jsonDoc, jsonPayload);

    Serial.println("\nJSON:");
    Serial.println(jsonPayload);


    // =================================================
    // HTTP POST
    // =================================================

    if (WiFi.status() == WL_CONNECTED)
    {
      HTTPClient http;

      http.setTimeout(15000);   // TLS handshake + Render can be slow
      http.begin(wifiClient, apiUrl);

      http.addHeader("Content-Type", "application/json");
      http.addHeader("Authorization", apiToken);

      int httpResponseCode = http.POST(jsonPayload);

      if (httpResponseCode > 0)
      {
        Serial.print("HTTP Response: ");
        Serial.println(httpResponseCode);

        String response = http.getString();

        Serial.print("Server Response: ");
        Serial.println(response);
      }
      else
      {
        Serial.print("HTTP Error: ");
        Serial.println(
          http.errorToString(httpResponseCode).c_str()
        );
      }

      http.end();
    }
    else
    {
      Serial.println("Cannot send data - Wi-Fi disconnected.");
    }
  }
}