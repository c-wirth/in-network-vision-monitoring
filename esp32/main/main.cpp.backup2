//main.cpp
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "PowerManager.h"
#include "NetworkManager.h"
#include "DeviceState.h"
#include "CameraManager.h"
#include "LEDDriver.h"

static const char *TAG = "app_main";

extern "C" void app_main(void) {

    ESP_LOGI(TAG, "Starting device...");

    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // --- Initialize DeviceStateManager ---
    DeviceStateManager deviceState;

    ESP_ERROR_CHECK(CameraManager::init());
    ESP_ERROR_CHECK(CameraManager::startStream(10));  // 10 FPS
	
    // Wait 2 seconds
    vTaskDelay(pdMS_TO_TICKS(2000));

    CameraManager::stopStream();

    // Wait for task to fully exit
    while (CameraManager::isStreaming()) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    ESP_LOGI(TAG, "Streaming stopped");
}
