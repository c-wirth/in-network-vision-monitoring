#pragma once

#include <cstdint>
#include "esp_event.h"
#include "nvs_flash.h"

// DeviceState.h
// Manages the device's functional states (idle, high power, error)

enum class PowerState { IDLE, HIGH_POWER, ERROR };
enum class NetworkState { DISCONNECTED, CONNECTED, ERROR };
enum class CameraState { IDLE, OFF, CAPTURE_STREAM, ERROR };

class DeviceStateManager {
public:
    DeviceStateManager();


    // PowerState events
    PowerState getPowerState() const;
    void setPowerState(PowerState state);

 
    // NetworkState events
    NetworkState getNetworkState() const;
    void setNetworkState(NetworkState state);
    void onNetworkEvent(esp_event_base_t event_base, int32_t event_id, void* event_data);



    // CameraState events
    CameraState getCameraState() const;
    void setCameraState(CameraState state);

private:
    PowerState powerState_;
    CameraState cameraState_;
    NetworkState networkState_;



    static const char* powerStateToString(PowerState state);
    static const char* networkStateToString(NetworkState state);
    static const char* cameraStateToString(CameraState state);
};
