#include <FastLED.h>

// Coin acceptor setup (unchanged)
volatile unsigned int pulseCount = 0;
unsigned long lastPulseMs = 0;
const byte COIN_PIN = 2;
const unsigned long QUIET_MS = 150;
const unsigned long DEBOUNCE_MS = 8;

// LED setup
#define LED_PIN 6
#define NUM_LEDS 180
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];

String ledMode = "DIM";
unsigned long lastLedUpdate = 0;
uint8_t gHue = 0;
uint8_t glowBrightness = 20;  // tracks fade-in from DIM level

void onPulse() {
  unsigned long now = millis();
  if (now - lastPulseMs >= DEBOUNCE_MS) {
    pulseCount++;
    lastPulseMs = now;
  }
}

void setup() {
  Serial.begin(115200);
  delay(50);
  Serial.println("READY");
  
  pinMode(COIN_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(COIN_PIN), onPulse, FALLING);
  
  // FastLED setup
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(200);
  FastLED.clear();
  FastLED.show();
  
  Serial.println("LEDs initialized");  // DEBUG
}

void loop() {
  // Coin detection (unchanged)
  if (pulseCount > 0 && (millis() - lastPulseMs) > QUIET_MS) {
    noInterrupts();
    unsigned int n = pulseCount;
    pulseCount = 0;
    interrupts();

    Serial.print("COIN ");
    Serial.println(n);
  }
  
  // Handle serial commands for LEDs
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    Serial.print("Received: ");  // DEBUG
    Serial.println(cmd);          // DEBUG
    
    if (cmd.startsWith("START ")) {
      ledMode = cmd.substring(6);
      if (ledMode == "GLOW") glowBrightness = 20;  // reset for fade-in
      Serial.print("LED mode set to: ");  // DEBUG
      Serial.println(ledMode);             // DEBUG
    } else if (cmd == "STOP") {
      ledMode = "DIM";
      Serial.println("LED mode: DIM");  // DEBUG
    }
  }
  
  // Update LED animations
  if (millis() - lastLedUpdate > 30) {
    lastLedUpdate = millis();
    
    if (ledMode == "DIM") {
      fill_solid(leds, NUM_LEDS, CHSV(192, 200, 20));  // dim purple, ~8% brightness
      FastLED.show();
    }
    else if (ledMode == "GLOW") {
      glowBrightness = qadd8(glowBrightness, 4);  // ramp up ~875ms, saturates at 255
      fill_solid(leds, NUM_LEDS, CHSV(192, 255, glowBrightness));
      FastLED.show();
    }
    else if (ledMode == "PULSE") {
      uint8_t breath = beatsin8(15, 60, 255);           // slow breath, warm amber/gold
      fill_solid(leds, NUM_LEDS, CHSV(40, 255, breath));
      FastLED.show();
    }
    else if (ledMode == "SPARKLE") {
      fadeToBlackBy(leds, NUM_LEDS, 20);
      for (int i = 0; i < 5; i++) {
        int pos = random16(NUM_LEDS);
        leds[pos] = CHSV(random8(180, 220), 255, 255);
      }
      FastLED.show();
    }
  }
  
  EVERY_N_MILLISECONDS(20) { gHue++; }
}