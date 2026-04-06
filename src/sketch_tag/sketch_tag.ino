#include <NimBLEDevice.h>
#include "esp_sleep.h"

// --- Configuration ---
#define DEEP_SLEEP_TIME_SEC  180ULL  // 3 minutes
#define ADV_DURATION_MS      1500    // 1.5s of advertising
#define HALO_COMPANY_ID      0xFFFF  // Company ID for manufacturer data
#define HALO_TAG_ID          1

// Set to true for development (waits 3 min), false for production (deep sleep)
#define IS_DEV               true

// Manufacturer Data Structure
struct halo_adv_data {
    uint16_t company_id;
    uint16_t tag_id;
    uint8_t  battery;
} __attribute__((packed));

void setup() {
    Serial.begin(115200);

    // 1. Initialize BLE
    NimBLEDevice::init("Halo-Tag");

    // 2. Setup Advertising
    NimBLEAdvertising *pAdvertising = NimBLEDevice::getAdvertising();

    // 3. Create Payload
    halo_adv_data payload;
    payload.company_id = HALO_COMPANY_ID;
    payload.tag_id = HALO_TAG_ID;
    payload.battery = 100;

    // 4. Set Data
    NimBLEAdvertisementData advData;
    // Pass manufacturer data (company_id through battery) as bytes
    advData.setManufacturerData((uint8_t*)&payload.company_id, sizeof(payload) - offsetof(halo_adv_data, company_id));
    pAdvertising->setAdvertisementData(advData);

    // 5. Start Advertising
    pAdvertising->start();
    Serial.println("Halo Tag Broadcasting (v3.x Core)...");

    // 6. Wait for Anchor to catch signal
    delay(ADV_DURATION_MS);

    // 7. Stop and Sleep
    pAdvertising->stop();

    #if IS_DEV
        Serial.println("DEV MODE: Waiting 3 minutes (no deep sleep)...");
        delay(DEEP_SLEEP_TIME_SEC * 1000ULL);
        Serial.println("DEV MODE: 3 minutes elapsed. Restarting advertising cycle...");
        ESP.restart();
    #else
        Serial.println("Entering Deep Sleep...");
        esp_sleep_enable_timer_wakeup(DEEP_SLEEP_TIME_SEC * 1000000ULL);
        esp_deep_sleep_start();
    #endif
}

void loop() {
    // Never reached
}