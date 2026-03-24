#pragma once

// LEDDriver.h
// Manages onboard LEDs with configurable blink patterns

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include <stdint.h>

class LEDDriver {
public:
    // Initialize LED manager (configure GPIOs, create tasks)
    static void init();

    /**
     * @brief Blink IO2 LED with specified on/off intervals
     * 
     * @param on_interval_ms  Time in milliseconds LED stays ON
     * @param off_interval_ms Time in milliseconds LED stays OFF
     * 
     * The task controlling IO2 will automatically update if called again.
     */
    static void setIO2(uint32_t on_interval_ms, uint32_t off_interval_ms);

    /**
     * @brief Stop blinking IO2 LED and turn it off
     */
    static void stopIO2();

private:
    // FreeRTOS task handle for IO2 blinking
    static TaskHandle_t io2TaskHandle;

    // Current blink intervals
    static volatile uint32_t io2_on_ms;
    static volatile uint32_t io2_off_ms;

    // GPIO pin for IO2
    static const gpio_num_t IO2_GPIO = GPIO_NUM_2;

    // Internal task that toggles IO2
    static void IO2BlinkTask(void* arg);
};
