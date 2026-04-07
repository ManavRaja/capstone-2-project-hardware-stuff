#include <NimBLEDevice.h>
#include "esp_sleep.h"

// --- Configuration ---
#define DEEP_SLEEP_TIME_SEC  180ULL  // 3 minutes
#define ADV_DURATION_MS      1500    // 1.5s of advertising
#define HALO_COMPANY_ID      0xFFFF  // Company ID for manufacturer data
#define HALO_TAG_ID          1

// Set to true for development (waits 3 min), false for production (deep sleep)
#define IS_DEV               true

// Advertising instance ID for extended advertising
#define ADV_INSTANCE_ID      0

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

    // 2. Setup Extended Advertising (for Coded PHY / Long Range)
    NimBLEExtAdvertising *pAdvertising = NimBLEDevice::getAdvertising();

    // 3. Create Extended Advertisement with Coded PHY
    NimBLEExtAdvertisement advData(BLE_HCI_LE_PHY_CODED);
    advData.setPrimaryPhy(BLE_HCI_LE_PHY_CODED);
    advData.setSecondaryPhy(BLE_HCI_LE_PHY_CODED);

    // 4. Create Payload
    halo_adv_data payload;
    payload.company_id = HALO_COMPANY_ID;
    payload.tag_id = HALO_TAG_ID;
    payload.battery = 100;

    // 5. Set Manufacturer Data
    advData.setManufacturerData((uint8_t*)&payload, sizeof(payload));

    // 6. Set advertisement data for instance 0 and start
    pAdvertising->setInstanceData(ADV_INSTANCE_ID, advData);
    pAdvertising->start(ADV_INSTANCE_ID);
    Serial.println("Halo Tag Broadcasting on Coded PHY (Long Range)...");

    // 7. Wait for Anchor to catch signal
    delay(ADV_DURATION_MS);

    // 8. Stop and Sleep
    pAdvertising->stop(ADV_INSTANCE_ID);

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