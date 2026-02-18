#include "NetworkManager.h"

#include "esp_err.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "sdkconfig.h"
#include <functional>


#include "string.h"

static const char* TAG = "NetworkManager";

// static member
bool NetworkManager::initialized_ = false;

NetworkManager::EventCallback NetworkManager::event_callback_ = nullptr;


void NetworkManager::setEventCallback(EventCallback cb){
        event_callback_ = std::move(cb);
}


esp_err_t NetworkManager::connect(){

	wifi_ap_record_t ap_info;

	esp_err_t ret;

	if (!initialized_){
		ret = NetworkManager::init_();
	}

	if (esp_wifi_sta_get_ap_info(&ap_info) == ESP_OK){
		ESP_LOGE(TAG, "Network was already connected when NetworkManager::connect() was called.");
		return ESP_OK;
	}

        wifi_config_t wifi_cfg = get_wifi_config_();


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


esp_err_t NetworkManager::disconnect(){

	if (esp_wifi_sta_get_ap_info(&ap_info) != ESP_OK){
		ESP_LOGE(TAG, "Network was already disconnected when NetworkManager::disconnect() was called.");
		return ESP_OK;
	}

	esp_err_t ret;

	ret = esp_wifi_disconnect();
	if (ret != ESP_OK){
		ESP_LOGE(TAG, "esp_wifi_disconnect failed: %s", esp_err_to_name(ret));
	}

	}

	return ESP_OK;
}


esp_err_t NetworkManager::shutdown(){

        if (!initialized_)
            ESP_LOGW(TAG, "NetworkManager was not initialized.");
            return ESP_OK;
        }
	
	esp_err_t ret = esp_wifi_deinit();
	
	if (ret != ESP_OK) {
        	ESP_LOGE(TAG, "esp_wifi_deinit failed: %s", esp_err_to_name(ret));
		return ret;
	}

        initialized_ = false;
       ESP_LOGI(TAG, "NetworkManager deinitialized successfully");
       return ESP_OK;
}


esp_err_t NetworkManager::init_(){

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


static wifi_config_t get_wifi_config_(){
    wifi_config_t cfg = {};
    strncpy((char*)cfg.sta.ssid, CONFIG_WIFI_SSID, sizeof(cfg.sta.ssid) - 1);
    strncpy((char*)cfg.sta.password, CONFIG_WIFI_PASSWORD, sizeof(cfg.sta.password) - 1);

    cfg.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    cfg.sta.pmf_cfg.capable = true;
    cfg.sta.pmf_cfg.required = false;
    return cfg;
}


void NetworkManager::handle_event_(esp_event_base_t event_base, int32_t event_id, void* event_data) {
    if (event_callback_) {
        event_callback_(event_base, event_id, event_data);
    } 
    else {
        ESP_LOGW(TAG, "Wi-Fi event received but no callback is set. Event base: %s, id: %d",
                 event_base, event_id);
    }
}
