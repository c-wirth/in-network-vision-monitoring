// LEDDriver.cpp
#include "LEDDriver.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "LEDDriver";

// Initialize static members
TaskHandle_t LEDDriver::io2TaskHandle = nullptr;
volatile uint32_t LEDDriver::io2_on_ms = 500;   // default 500ms on
volatile uint32_t LEDDriver::io2_off_ms = 500;  // default 500ms off

void LEDDriver::init() {
    // Configure IO2 GPIO
    gpio_config_t io_conf = {};
    io_conf.pin_bit_mask = (1ULL << IO2_GPIO);
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.intr_type = GPIO_INTR_DISABLE;

    gpio_config(&io_conf);
    ESP_LOGI(TAG, "IO2 GPIO configured");

}

void LEDDriver::setIO2(uint32_t on_interval_ms, uint32_t off_interval_ms) {
    io2_on_ms = on_interval_ms;
    io2_off_ms = off_interval_ms;

    if (io2TaskHandle == nullptr) {
        // Create the blink task if not already running
        BaseType_t result = xTaskCreate(
            LEDDriver::IO2BlinkTask,
            "IO2BlinkTask",
            2048,               // stack size
            nullptr,            // argument (static intervals)
            5,                  // task priority
            &io2TaskHandle
        );

        if (result == pdPASS) {
            ESP_LOGI(TAG, "IO2 blink task started");
        } else {
            ESP_LOGE(TAG, "Failed to start IO2 blink task");
        }
    } else {
        ESP_LOGI(TAG, "IO2 blink intervals updated: ON=%dms, OFF=%dms", on_interval_ms, off_interval_ms);
    }
}

void LEDDriver::stopIO2() {
    if (io2TaskHandle != nullptr) {
        vTaskDelete(io2TaskHandle);
        io2TaskHandle = nullptr;
        ESP_LOGI(TAG, "IO2 blink task stopped");
    }
    gpio_set_level(IO2_GPIO, 0); // turn LED off
}

// Internal FreeRTOS task
void LEDDriver::IO2BlinkTask(void* arg) {
    while (true) {
        gpio_set_level(IO2_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(io2_on_ms));

        gpio_set_level(IO2_GPIO, 0);
        vTaskDelay(pdMS_TO_TICKS(io2_off_ms));
    }
}
