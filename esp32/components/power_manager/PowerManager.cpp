#include "PowerManager.h"
#include "esp_err.h"
#include "esp_pm.h"
#include "esp_log.h"

static const char *TAG = "PowerManager";

// static members
esp_pm_lock_handle_t PowerManager::cpu_lock_ = nullptr;
bool PowerManager::initialized_ = false;


/**
 * @brief Initialize the ESP32-S3 power management system.
 *
 * Configures dynamic frequency scaling (DFS) and light sleep according
 * to default settings. Creates CPU lock.
 *
 * After calling this, you can switch between high and low power using
 * setHighPower() and setLowPower().
 *
 * @return ESP_OK on success, or if already initialized (idempotent)
 * @return ESP_ERR_INVALID_ARG or ESP_ERR_NOT_SUPPORTED if esp_pm calls fail
 *
 * @note Must be called once at system startup.
 */
esp_err_t PowerManager::init() {

	if (initialized_){
		ESP_LOGW(TAG, "PowerManager already initialized");
		return ESP_OK;
	}

	esp_pm_config_esp32_t pm_config = {
		.max_freq_mhz = 240, // max CPU freq
		.min_freq_mhz = 80,  // min CPU freq
		.light_sleep_enable = true
	};


        esp_err_t ret = esp_pm_configure(&pm_config);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "esp_pm_configure failed: %s", esp_err_to_name(ret));
            return ret;
        }


        ret = esp_pm_lock_create(ESP_PM_CPU_FREQ_MAX, 0, "cpu_lock", &cpu_lock_);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to create CPU lock: %s", esp_err_to_name(ret));
            return ret;
        }


        initialized_ = true;
        ESP_LOGI(TAG, "PowerManager initialized successfully");
        return ESP_OK;

}


/**
 * @brief Switch the device to high-power mode.
 *
 * Acquires the CPU lock to prevent
 * frequency scaling and light sleep. Needed when performing
 * real-time tasks (e.g., camera capture, UDP streaming).
 *
 * @return ESP_OK on success
 * @return ESP_ERR_INVALID_STATE if PowerManager not initialized
 * @return ESP_ERR_* if esp_pm_lock_acquire fails
 */
esp_err_t PowerManager::setHighPower() {
	
	if (!initialized_) { 
		ESP_LOGE(TAG, "PowerManager not initialized");
		return ESP_ERR_INVALID_STATE;
	}

        esp_err_t ret = esp_pm_lock_acquire(cpu_lock_);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to acquire CPU lock: %s", esp_err_to_name(ret));
            return ret;
        }

        ESP_LOGI(TAG, "High power mode enabled");
        return ESP_OK;
}

esp_err_t PowerManager::setLowPower()
{
    if (!initialized_) {
        ESP_LOGE(TAG, "PowerManager not initialized");
        return ESP_ERR_INVALID_STATE;
    }

    esp_err_t ret;

    ret = esp_pm_lock_release(cpu_lock_);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to release CPU lock: %s", esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "Low power mode enabled (sleep allowed)");
    return ESP_OK;
}
