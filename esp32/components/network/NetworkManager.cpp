#include "NetworkManager.h"

#include "esp_err.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "sdkconfig.h"


#include "string.h"

static const char* TAG = "NetworkManager";

// static member
bool Network::initialized_ = false;

esp_err_t NetworkManager::init(){

	if (initialized_){
		ESP_LOGW(TAG, "NetworkManager was already initialized.");
		return ESP_OK;
	}

	esp_err_t ret = esp_wifi_init(WIFI_INIT_CONFIG_DEFAULT);

        if (ret == ESP_ERR_NO_MEM) {
            ESP_LOGE(TAG, "esp_wifi_init failed due to OOM: %s", esp_err_to_name(ret));
            return ret;
        }
	else if (ret != ESP_OK) {
            ESP_LOGE(TAG, "esp_wifi_init failed: %s", esp_err_to_name(ret));
            return ret;
        }

        initialized_ = true;
        ESP_LOGI(TAG, "NetworkManager initialized successfully");
        return ESP_OK;

}


esp_err_t NetworkManager::deinit(){

        if (initialized_)
            ESP_LOGW(TAG, "NetworkManager was not initialized.");
            return ESP_OK;
        }
	
	esp_err_t ret = esp_wifi_deinit()
	
	if (ret != ESP_OK) {
        	ESP_LOGE(TAG, "esp_wifi_deinit failed: %s", esp_err_to_name(ret));
		return ret;
	}

        initialized_ = false;
       ESP_LOGI(TAG, "NetworkManager deinitialized successfully");
       return ESP_OK;
}


esp_err_t NetworkManager::connect(){

	if (!initialized_){
		ESP_LOGW(TAG, "Cannot connect to WiFi: NetworkManager was not initialized.");
		return ESP_ERR_WIFI_NOT_INIT;
	}

        wifi_config_t wifi_cfg = get_wifi_config_();

	esp_err_t ret;

	ret = esp_wifi_set_mode(WIFI_MODE_STA);
	if (ret != ESP_OK){
        	ESP_LOGE(TAG, "esp_wifi_set_mode failed: %s", esp_err_to_name(ret));
		return ret;
	}

	ret = esp_wifi_set_config(WIFI_IF_STA, &wifi_cfg);

	if (ret != ESP_OK){
        	ESP_LOGE(TAG, "esp_wifi_set_config failed: %s", esp_err_to_name(ret));
		return ret;
	}

        ret = esp_wifi_start();
          if (ret != ESP_OK) {
              ESP_LOGE(TAG, "esp_wifi_start failed: %s", esp_err_to_name(ret));
              return ret;
          }
	
          ret = esp_wifi_connect();
          if (ret != ESP_OK) {
              ESP_LOGE(TAG, "esp_wifi_connect failed: %s", esp_err_to_name(ret));
              return ret;
          }
          ESP_LOGI(TAG, "WiFi connection established");
          return ESP_OK;
}


static wifi_config_t get_wifi_config_(){
    wifi_config_t cfg = {};
    strncpy((char*)cfg.sta.ssid, CONFIG_WIFI_SSID, sizeof(cfg.sta.ssid) - 1);
    strncpy((char*)cfg.sta.password, CONFIG_WIFI_PASSWORD, sizeof(cfg.sta.password) - 1);

    cfg.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    cfg.sta.pmf_cfg.capable = true;
    cfg.sta.pmf_cfg.required = false;
    return cfg;
}
