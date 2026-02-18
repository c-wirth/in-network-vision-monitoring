//main.cpp
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


    // Default event loop
    ESP_ERROR_CHECK(esp_event_loop_create_default());


    LEDDriver::init();

    esp_err_t ret = PowerManager::init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "PowerManager init failed: %s", esp_err_to_name(ret));
        return;
    }


    ret = NetworkManager::init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "NetworkManager init failed: %s", esp_err_to_name(ret));
        return;
    }

    ESP_LOGI(TAG, "PowerManger successfully initializes %s", esp_err_to_name(ret));

    // --- Initialize DeviceStateManager ---
    DeviceStateManager deviceState;

    ESP_LOGI(TAG, "Network state 1: %s (expected DISCONNECTED)",
             DeviceStateManager::networkStateToString(deviceState.getNetworkState()));
    ESP_LOGI(TAG, "Power state 1: %s (expected IDLE)",
             DeviceStateManager::powerStateToString(deviceState.getPowerState()));
 
    deviceState.setNetworkState(NetworkState::CONNECTED);
    deviceState.setPowerState(PowerState::HIGH_POWER);
    ESP_LOGI(TAG, "Power state 2: %s (expected HIGH_POWER)",
             DeviceStateManager::powerStateToString(deviceState.getPowerState()));
    ESP_LOGI(TAG, "Network state 2: %s (expected CONNECTED)",
             DeviceStateManager::networkStateToString(deviceState.getNetworkState()));

    deviceState.setNetworkState(NetworkState::DISCONNECTED);
    deviceState.setPowerState(PowerState::IDLE);
    ESP_LOGI(TAG, "Network state 3: %s (expected DISCONNECTED)",
             DeviceStateManager::networkStateToString(deviceState.getNetworkState()));
    ESP_LOGI(TAG, "Power state 3: %s (expected IDLE)",
             DeviceStateManager::powerStateToString(deviceState.getPowerState()));

    deviceState.setNetworkState(NetworkState::ERROR);
    deviceState.setPowerState(PowerState::ERROR);
    ESP_LOGI(TAG, "Power state 4: %s (expected ERROR)",
             DeviceStateManager::powerStateToString(deviceState.getPowerState()));
    ESP_LOGI(TAG, "Network state 4: %s (expected ERROR)",
             DeviceStateManager::networkStateToString(deviceState.getNetworkState()));

    deviceState.setNetworkState(NetworkState::DISCONNECTED);
    deviceState.setPowerState(PowerState::IDLE);
    ESP_LOGI(TAG, "Network state 5: %s (expected DISCONNECTED)",
             DeviceStateManager::networkStateToString(deviceState.getNetworkState()));
    ESP_LOGI(TAG, "Power state 5: %s (expected IDLE)",
             DeviceStateManager::powerStateToString(deviceState.getPowerState()));



    vTaskDelay(pdMS_TO_TICKS(5000));
    ESP_LOGI(TAG, "DeviceStateManager initialized. Entering main loop...");

    while (true){
        vTaskDelay(pdMS_TO_TICKS(1000));
	}

}
