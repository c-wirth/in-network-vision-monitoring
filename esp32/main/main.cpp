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

    DeviceStateManager deviceState;
    deviceState.camera_fps = 5;

    ESP_LOGI(TAG, "CameraState: %s", DeviceStateManager::cameraStateToString(deviceState.getCameraState()));
    deviceState.setCameraState(CameraState::IDLE);
    ESP_LOGI(TAG, "CameraState: %s", DeviceStateManager::cameraStateToString(deviceState.getCameraState()));
    
    deviceState.setCameraState(CameraState::CAPTURE_STREAM);
    ESP_LOGI(TAG, "CameraState: %s", DeviceStateManager::cameraStateToString(deviceState.getCameraState()));

    vTaskDelay(pdMS_TO_TICKS(5000)); // stream for 5 seconds

    deviceState.setCameraState(CameraState::IDLE);
    ESP_LOGI(TAG, "CameraState: %s", DeviceStateManager::cameraStateToString(deviceState.getCameraState()));
    deviceState.setCameraState(CameraState::OFF);
    ESP_LOGI(TAG, "CameraState: %s", DeviceStateManager::cameraStateToString(deviceState.getCameraState()));
}
