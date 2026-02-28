#include "esp_log.h"
#include "esp_netif.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "DeviceState.h"

static const char *TAG = "app_main";

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Starting device...");

    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_ERROR_CHECK(esp_event_loop_create_default());

    DeviceStateManager deviceState;
    deviceState.camera_fps = 10;

    // --- camera idle ---
    deviceState.setCameraState(CameraState::IDLE);
    if (deviceState.getCameraState() == CameraState::ERROR) {
        ESP_LOGE(TAG, "Camera init failed — halting");
        return;
    }
    ESP_LOGI(TAG, "CameraState: %s", DeviceStateManager::cameraStateToString(deviceState.getCameraState()));

    // --- network ---
    deviceState.setNetworkState(NetworkState::CONNECTED);
    if (deviceState.getNetworkState() == NetworkState::ERROR) {
        ESP_LOGE(TAG, "Network init failed — halting");
        return;
    }
    ESP_LOGI(TAG, "NetworkState: %s", DeviceStateManager::networkStateToString(deviceState.getNetworkState()));


    ESP_LOGI(TAG, "Waiting for IP...");
    esp_netif_ip_info_t ip_info;
    esp_netif_t* netif = esp_netif_get_handle_from_ifkey("WIFI_STA_DEF");
    int timeout = 0;
    const int MAX_WAIT_MS = 15000; // 15 seconds
 
    do {
        vTaskDelay(pdMS_TO_TICKS(500));
        esp_netif_get_ip_info(netif, &ip_info);
        timeout += 500;
        if (timeout >= MAX_WAIT_MS) {
            ESP_LOGE(TAG, "Timed out waiting for IP — halting");
            return;
        }
    } while (ip_info.ip.addr == 0);
 
    ESP_LOGI(TAG, "Device IP: " IPSTR, IP2STR(&ip_info.ip));


    // --- UDP init and handshake ---
    deviceState.setUDPState(UDPState::CONNECTED_IDLE);
    if (deviceState.getUDPState() == UDPState::ERROR) {
        ESP_LOGE(TAG, "UDP connect failed — halting");
        return;
    }
    ESP_LOGI(TAG, "UDPState: %s", DeviceStateManager::udpStateToString(deviceState.getUDPState()));

    ESP_LOGI(TAG, "Device ready — waiting for server commands");

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
