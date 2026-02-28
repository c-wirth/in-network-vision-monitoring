#pragma once

//DeviceState.h

#include <cstdint>
#include "esp_event.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_camera.h"
#include "UDPManager.h"

enum class PowerState   { IDLE, HIGH_POWER, ERROR };
enum class NetworkState { DISCONNECTED, CONNECTED, ERROR };
enum class CameraState  { IDLE, OFF, CAPTURE_STREAM, ERROR };
enum class UDPState     { OFF,CONNECTED_IDLE, STREAMING, ERROR };

class DeviceStateManager {
public:
    DeviceStateManager();

    uint32_t camera_fps = 30;

    PowerState   getPowerState()   const;
    NetworkState getNetworkState() const;
    CameraState  getCameraState()  const;
    UDPState     getUDPState()     const;

    void setPowerState(PowerState state);
    void setNetworkState(NetworkState state);
    void setCameraState(CameraState state);
    void setUDPState(UDPState state);

    void onNetworkEvent(esp_event_base_t event_base, int32_t event_id, void* event_data);
    void onUDPReceiveEvent(UDPEvent event);

    static const char* powerStateToString(PowerState state);
    static const char* networkStateToString(NetworkState state);
    static const char* cameraStateToString(CameraState state);
    static const char* udpStateToString(UDPState state);

private:
    PowerState   powerState_;
    CameraState  cameraState_;
    NetworkState networkState_;
    UDPState     udpState_;

    QueueHandle_t frame_queue_;
};
