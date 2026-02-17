#pragma once

#include "esp_err.h"
#include "esp_pm.h"
#include "esp_log.h"

/**
 * @brief Manages CPU power for the ESP32-S3.
 * 
 * Allows switching between high-power mode (CPU locked at max frequency)
 * and low-power mode (automatic frequency scaling and light sleep enabled).
 */
class PowerManager {
public:
    static esp_err_t init();         // initialze cpu_lock_ and configre power manager
    static esp_err_t setHighPower(); // sets full processing power on CPU (240Hz)
    static esp_err_t setLowPower();  // removes cpu lock set on by setHighPower, enabling automatic low power

private:
    static esp_pm_lock_handle_t cpu_lock_;
    static bool initialized_;
};
