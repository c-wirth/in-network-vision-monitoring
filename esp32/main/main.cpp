#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "PowerManager.h"
#include "NetworkManager.h"
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


    esp_err_t ret = NetworkManager::init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "NetworkManager init failed: %s", esp_err_to_name(ret));
        return;
    }

    ESP_LOGI(TAG, "PowerManger successfully initializes %s", esp_err_to_name(ret));

    // --- Initialize DeviceStateManager ---
    DeviceStateManager deviceState;


    ESP_LOGI("Network state 1, %s: (expected DISCONNECTED)", deviceState.getNetworkState())
    ESP_LOGI("Power state 1, %s: (expected IDLE)", deviceState.getPowerState())


    deviceState.setNetworkState(NetworkState::CONNECTED);
    deviceState.setPowerMode(PowerState::HIGH_POWER);
    ESP_LOGI("Power state 2, %s: (expected HIGH_POWER)", deviceState.getPowerState())
    ESP_LOGI("Network state 2, %s: (expected CONNECTED)", deviceState.getNetworkState())


    deviceState.setNetworkState(NetworkState::DISCONNECTED);
    deviceState.setPowerMode(PowerState::IDLE);
    ESP_LOGI("Network state 3, %s: (expected DISCONNECTED)", deviceState.getNetworkState())
    ESP_LOGI("Power state 3, %s: (expected IDLE)", deviceState.getPowerState())



    deviceState.setPowerMode(NetworkState::ERROR);
    deviceState.setPowerMode(PowerState::ERROR);
    ESP_LOGI("Power state 3, %s: (expected ERROR)", deviceState.getPowerState())
    ESP_LOGI("Network state 3, %s: (expected ERROR)", deviceState.getNetworkState())



    deviceState.setNetworkState(NetworkState::DISCONNECTED);
    deviceState.setPowerMode(PowerState::IDLE);
    ESP_LOGI("Network state 4, %s: (expected DISCONNECTED)", deviceState.getNetworkState())
    ESP_LOGI("Power state 4, %s: (expected IDLE)", deviceState.getPowerState())



    vTaskDelay(pdMS_TO_TICKS(5000));
    ESP_LOGI(TAG, "DeviceStateManager initialized. Entering main loop...");

    while (true){
        vTaskDelay(pdMS_TO_TICKS(1000));
	}

}
