#pragma once

// DeviceState.h
// Manages the device's functional states (idle, high power, error)

enum class PowerState { IDLE, HIGH_POWER, ERROR };
enum class NetworkState { DISCONNECTED, CONNECTED, ERROR };
enum class CameraState { IDLE, OFF, SINGLE_CAPTURE, CAPTURE_STREAM, ERROR };

class DeviceStateManager {
public:
    DeviceStateManager();



    // Query states
    PowerState getPowerState() const;
    CameraState getCameraState() const;
    NetworkState getNetworkState() const;

    // power state events
    void setPowerState(PowerState state);
 
    // Network state events
    void setNetworkState(NetworkState new_state);


    // TODO CHANGE THESE TO ONE PARAMETERIZED FUNCTION
    // camera state events
    void requestCameraOn();
    void requestCameraOff();
    void requestSingleCapture();
    void requestCaptureStream();


    static const char* networkStateToString(NetworkState state);
    static const char* powerStateToString(PowerState state);

private:
    PowerState powerState_;
    CameraState cameraState_;
    NetworkState networkState_;
};
