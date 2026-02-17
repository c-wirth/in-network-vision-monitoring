#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "PowerManager.h"
#include "DeviceState.h"
#include "LEDDriver.h"

static const char *TAG = "MAP_INIT";

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Starting device...");


    // --- Initialize DeviceStateManager ---
    DeviceStateManager deviceState;


    deviceState.requestLowPower();


    ESP_LOGI(TAG, "DeviceStateManager initialized. Entering main loop...");


    while (true){
        vTaskDelay(pdMS_TO_TICKS(1000));
	}

}
