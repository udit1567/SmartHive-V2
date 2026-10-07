#include <WiFi.h>
#include "esp_camera.h"
#include <WebServer.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// ===============================
// WiFi
// ===============================
const char* ssid = "Infinity";
const char* password = "#Udit1588";

// ===============================
// AI Thinker ESP32-CAM pins
// ===============================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

WebServer server(80);

// ===============================
// Stream handler
// ===============================
void handleStream() {

  WiFiClient client = server.client();

  client.print(
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n"
    "Cache-Control: no-cache\r\n"
    "Connection: close\r\n"
    "Access-Control-Allow-Origin: *\r\n"
    "\r\n"
  );

  while (client.connected()) {

    camera_fb_t *fb = esp_camera_fb_get();

    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }

    client.printf(
      "--frame\r\n"
      "Content-Type: image/jpeg\r\n"
      "Content-Length: %u\r\n"
      "\r\n",
      fb->len
    );

    client.write(fb->buf, fb->len);
    client.print("\r\n");

    esp_camera_fb_return(fb);

    delay(30);
  }
}

// ===============================
// Setup
// ===============================
void setup() {

  // Camera power-on draws a current spike that can trip the brownout
  // detector and reboot the board mid-stream; disable it.
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  Serial.println();

  // =============================
  // Connect WiFi
  // =============================
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected!");

  // =============================
  // Camera configuration
  // =============================
  camera_config_t config = {};

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;

  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;

  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

  // fb_count > 1 needs PSRAM to hold the extra frame buffer; without it,
  // this allocation intermittently fails/corrupts memory and crashes the
  // board mid-stream. Fall back to a single smaller buffer if PSRAM isn't
  // available.
  if (psramFound()) {
    // Lower resolution = smoother streaming
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // =============================
  // Initialize camera
  // =============================
  esp_err_t err = esp_camera_init(&config);

  if (err != ESP_OK) {
    Serial.printf(
      "Camera init failed with error 0x%x\n",
      err
    );

    while (true) {
      delay(1000);
    }
  }

  Serial.println("Camera initialized!");

  // =============================
  // Start stream server
  // =============================
  server.on("/stream", HTTP_GET, handleStream);

  server.begin();

  Serial.println("Stream server started!");
  Serial.print("Open this URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");
}

// ===============================
// Loop
// ===============================
void loop() {
  server.handleClient();
}