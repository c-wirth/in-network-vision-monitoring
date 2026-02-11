
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "BLINK";

// Change this to whatever GPIO your LED is connected to
#define LED_GPIO GPIO_NUM_2

extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "Starting blink test...");

    // Configure GPIO as output
    gpio_config_t io_conf = {};
    io_conf.pin_bit_mask = (1ULL << LED_GPIO);
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.intr_type = GPIO_INTR_DISABLE;

    gpio_config(&io_conf);

    while (true)
    {
        gpio_set_level(LED_GPIO, 1);  // LED ON
        vTaskDelay(pdMS_TO_TICKS(2000));

        gpio_set_level(LED_GPIO, 0);  // LED OFF
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
