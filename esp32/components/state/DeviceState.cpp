// DeviceState.cpp


#include "DeviceState.h"
#include "CameraManager.h"
#include "PowerManager.h"
#include "NetworkManager.h"
#include "LEDDriver.h"

#include "esp_log.h"
#include <cstdint>
#include "esp_event.h"
#include "nvs_flash.h"


static const char *TAG = "DeviceState";


DeviceStateManager::DeviceStateManager():
	powerState_(PowerState::IDLE),
	cameraState_(CameraState::OFF),
	networkState_(NetworkState::DISCONNECTED)
{

	ESP_LOGI(TAG, "DeviceStateManager initialized with default states");


        // Register network event callback
        NetworkManager::setEventCallback(
		[this](esp_event_base_t base, int32_t id, void* data) {
			this->onNetworkEvent(base, id, data);
        }
        );
}


PowerState DeviceStateManager::getPowerState() const { return powerState_; }
CameraState DeviceStateManager::getCameraState() const { return cameraState_; }
NetworkState DeviceStateManager::getNetworkState() const { return networkState_; }


void DeviceStateManager::setPowerState(PowerState state) {

    esp_err_t ret = ESP_FAIL;

    switch (state) {
        case PowerState::IDLE:
	    ret = PowerManager::setLowPower();
	    LEDDriver::stopIO2();
            break;

        case PowerState::HIGH_POWER:
            ret = PowerManager::setHighPower();
            LEDDriver::setIO2(1000, 1000);
            break;

        case PowerState::ERROR:
            ESP_LOGE(TAG, "PowerState set to ERROR state!");
            LEDDriver::setIO2(250, 250);
            powerState_ = PowerState::ERROR;
            return;

	default:
            ESP_LOGE(TAG, "Unknown PowerState set: %s.  Switching to PowerState::ERROR", DeviceStateManager::powerStateToString(state));
            LEDDriver::setIO2(250, 250);
            powerState_ = PowerState::ERROR;
            return;
    }

    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set power state: %s", esp_err_to_name(ret));
        powerState_ = PowerState::ERROR;  // set error state safely
        LEDDriver::setIO2(250, 250);
	// TODO: we need to kill all high level processes here 

    } else {
        powerState_ = state;
    }
}


void DeviceStateManager::setNetworkState(NetworkState state) {
    esp_err_t ret = ESP_OK;

    switch(state) {
        case NetworkState::CONNECTED:
            ret = NetworkManager::connect();
            break;
        case NetworkState::DISCONNECTED:
            ret = NetworkManager::disconnect();
            break;
        case NetworkState::ERROR:
            networkState_ = NetworkState::ERROR;
            ESP_LOGE(TAG, "NetworkState is set to ERROR!");
            return;
    }

    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to change NetworkState to: %s, setting to NetworkState::Error", esp_err_to_name(ret));
        networkState_ = NetworkState::ERROR;
    } else {
        networkState_ = state;
    }
}


void DeviceStateManager::onNetworkEvent(esp_event_base_t event_base, int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        networkState_ = NetworkState::DISCONNECTED;
        ESP_LOGW(TAG, "Network disconnected unexpectedly");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        networkState_ = NetworkState::CONNECTED;
        ESP_LOGI(TAG, "Network connected (got IP)");
    }
}


void DeviceStateManager::setCameraState(CameraState state) {
    esp_err_t ret = ESP_OK;

    // Extreme Error check: cannot be streaming if uninitialized
    if (!CameraManager::isInitialized() && CameraManager::isStreaming()) {
        ESP_LOGE(TAG, "Invalid camera state: streaming but not initialized, setting to CameraState::ERROR");
        cameraState_ = CameraState::ERROR;
        return;
    }

    switch (state) {
        case CameraState::OFF:
            ret = CameraManager::deinit();
            break;

        case CameraState::IDLE:
            if (CameraManager::isStreaming()) {
                ret = CameraManager::stopStream();
            } else if (!CameraManager::isInitialized()) {
                ret = CameraManager::init();
            }
            break;

	case CameraState::CAPTURE_STREAM:
	    if (!CameraManager::isInitialized()) {
	        ret = CameraManager::init();
	        if (ret != ESP_OK) {
	            ESP_LOGE(TAG, "Failed to initialize camera before streaming: %s", esp_err_to_name(ret));
	            break;
	        }
	    }
    	    ret = CameraManager::startStream(camera_fps);
	    break;

        case CameraState::ERROR:
            ESP_LOGE(TAG, "CameraState is set to ERROR!");
            cameraState_ = CameraState::ERROR;
            return;
    }

    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to change CameraState to: %s, received: %s, setting to CameraState::ERROR",
            cameraStateToString(state), esp_err_to_name(ret));
        cameraState_ = CameraState::ERROR;
    } else {
        cameraState_ = state;
    }
}


const char* DeviceStateManager::networkStateToString(NetworkState state) {
    switch (state) {
        case NetworkState::DISCONNECTED: return "DISCONNECTED";
        case NetworkState::CONNECTED:    return "CONNECTED";
        case NetworkState::ERROR:        return "ERROR";
        default:                         return "UNKNOWN";
    }
}


const char* DeviceStateManager::powerStateToString(PowerState state) {
    switch (state) {
        case PowerState::IDLE:        return "IDLE";
        case PowerState::HIGH_POWER:  return "HIGH_POWER";
        case PowerState::ERROR:       return "ERROR";
        default:                      return "UNKNOWN";
    }
}


const char* DeviceStateManager::cameraStateToString(CameraState state) {
    switch (state) {
        case CameraState::IDLE:            return "IDLE";
        case CameraState::OFF:             return "OFF";
        case CameraState::CAPTURE_STREAM:  return "CAPTURE_STREAM";
        case CameraState::ERROR:           return "ERROR";
        default:                           return "UNKNOWN";
    }
}
