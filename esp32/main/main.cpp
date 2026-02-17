#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "PowerManager.h"
#include "DeviceState.h"
#include "LEDDriver.h"

static const char *TAG = "MAP_INIT";

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Starting device...");

    LEDDriver::init();

    esp_err_t ret = PowerManager::init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "PowerManager init failed: %s", esp_err_to_name(ret));
        return;
    }

    ESP_LOGI(TAG, "PowerManger successfully initializes %s", esp_err_to_name(ret));

    // --- Initialize DeviceStateManager ---
    DeviceStateManager deviceState;


    deviceState.setPowerMode(PowerState::IDLE);
    deviceState.setPowerMode(PowerState::HIGH_POWER);


    vTaskDelay(pdMS_TO_TICKS(5000));
    deviceState.setPowerMode(PowerState::IDLE);


    ESP_LOGI(TAG, "DeviceStateManager initialized. Entering main loop...");


    while (true){
        vTaskDelay(pdMS_TO_TICKS(1000));
	}

}
