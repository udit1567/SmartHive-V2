#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// =====================================================
// Wi-Fi
// =====================================================

const char *ssid = "Wifi";
const char *password = "#Udit1588";

// =====================================================
// API
// =====================================================

const String apiToken = "wbQHFeCx";   // device token of the deployed (Render) account

// Deployed Render server (HTTPS). For the local Flask server use
// "http://192.168.246.24:5000/update" - the client is picked
// automatically from the URL scheme.
const String apiUrl = "https://smarthive-v2.onrender.com/update";

// Dashboard's Soil moisture graph reads D3 by default.
const char *MOISTURE_PIN_KEY = "D3";

// =====================================================
// SENSOR PIN
// =====================================================

// Capacitive/resistive soil sensor AO -> GPIO 32.
// Must be an ADC1 pin (GPIO 32-39). ADC2 pins (e.g. 25/26/27)
// can't be read while Wi-Fi is on and return 0 / garbage.
#define SOIL_PIN 32

// =====================================================
// CALIBRATION
// =====================================================

// ESP32 ADC is 12-bit (0-4095), so the ESP8266 values (540 / 845 on a
// 10-bit A0) are scaled x4 here as a starting point. Calibrate for your
// sensor: read "Raw ADC" on Serial with the probe in dry air (SOIL_DRY)
// and in a glass of water (SOIL_WET), then put those numbers here.
#define SOIL_WET 2160   // raw ADC when fully wet  -> 100 %
#define SOIL_DRY 3380   // raw ADC when fully dry  ->   0 %

// =====================================================
// SETTINGS
// =====================================================

unsigned long lastTime = 0;
unsigned long timerDelay = 5000;    // 5 seconds

#define ADC_MAX 4095.0
#define ADC_VOLTAGE 3.3

WiFiClient plainClient;
// Render only accepts HTTPS - a plain WiFiClient gets
// "400 The plain HTTP request was sent to HTTPS port".
WiFiClientSecure secureClient;


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
// RAW ADC -> MOISTURE %
// 0 % = dry, 100 % = wet
// =====================================================

float moisturePercentage(int adc)
{
  float percentage =
    (float)(SOIL_DRY - adc) * 100.0 / (float)(SOIL_DRY - SOIL_WET);

  return constrain(percentage, 0.0, 100.0);
}


// =====================================================
// MOISTURE LEVEL
// =====================================================

String getMoistureLevel(float percentage)
{
  if (percentage < 20)
    return "VERY DRY";

  else if (percentage < 40)
    return "DRY";

  else if (percentage < 70)
    return "OPTIMAL";

  else if (percentage < 90)
    return "MOIST";

  else
    return "WATERLOGGED";
}


// =====================================================
// WIFI CONNECTION
// =====================================================

void connectWiFi()
{
  if (WiFi.status() == WL_CONNECTED)
    return;

  WiFi.mode(WIFI_STA);
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
  Serial.println("     ESP32 SOIL MOISTURE MONITOR");
  Serial.println("========================================");

  // ADC configuration (0 - ~3.3 V range)
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  pinMode(SOIL_PIN, INPUT);

  // Wi-Fi
  WiFi.setAutoReconnect(true);
  connectWiFi();

  // HTTPS without certificate pinning
  secureClient.setInsecure();

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
    // SOIL MOISTURE
    // -------------------------------------------------

    int soilRaw = readAverageADC(SOIL_PIN);

    float soilVoltage = adcToVoltage(soilRaw);

    float soilPercent = moisturePercentage(soilRaw);

    String soilLevel = getMoistureLevel(soilPercent);

    // =================================================
    // SERIAL OUTPUT
    // =================================================

    Serial.println();
    Serial.println("========================================");
    Serial.println("          SOIL MOISTURE");
    Serial.println("========================================");

    Serial.print("Raw ADC     : ");
    Serial.println(soilRaw);

    Serial.print("Voltage     : ");
    Serial.print(soilVoltage, 3);
    Serial.println(" V");

    Serial.print("Moisture    : ");
    Serial.print(soilPercent, 1);
    Serial.println(" %");

    Serial.print("Status      : ");
    Serial.println(soilLevel);

    Serial.println("========================================");


    // =================================================
    // JSON
    // =================================================

    // Backend stores only numeric pins D1..D8 - the text status
    // stays on Serial.
    StaticJsonDocument<128> jsonDoc;

    jsonDoc[MOISTURE_PIN_KEY] = soilPercent;

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

      bool ok;
      if (apiUrl.startsWith("https://"))
        ok = http.begin(secureClient, apiUrl);
      else
        ok = http.begin(plainClient, apiUrl);

      if (!ok)
      {
        Serial.println("HTTP begin failed - check apiUrl.");
        return;
      }

      http.addHeader("Content-Type", "application/json");
      http.addHeader("Authorization", apiToken);   // raw device token, no "Bearer"

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
