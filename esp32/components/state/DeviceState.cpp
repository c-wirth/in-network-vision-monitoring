#include "DeviceState.h"
#include "PowerManager.h"
// #include "CameraDriver.h"
// #include "NetworkManager.h"
#include "LEDDriver.h"
#include "esp_log.h"


static const char *TAG = "DeviceState";


DeviceStateManager::DeviceStateManager():
	powerState_(PowerState::IDLE),
	cameraState_(CameraState::OFF),
	networkState_(NetworkState::DISCONNECTED)
{
	ESP_LOGI(TAG, "DeviceStateManager initialized with default states");
}


PowerState DeviceStateManager::getPowerState() const { return powerState_; }

CameraState DeviceStateManager::getCameraState() const { return cameraState_; }

NetworkState DeviceStateManager::getNetworkState() const { return networkState_; }


void DeviceStateManager::setPowerMode(PowerState state) {

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
            ESP_LOGE(TAG, "Device in ERROR state!");
            LEDDriver::setIO2(250, 250);
            return;

	default:
            ESP_LOGE(TAG, "Unknown PowerState value! %s");
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
