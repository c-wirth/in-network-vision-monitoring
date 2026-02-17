// DeviceState.h
// Manages the device's functional states (idle, high power, error)

#ifndef DEVICE_STATE_H
#define DEVICE_STATE_H

enum class PowerState { IDLE, HIGH_POWER, ERROR };
enum class CameraState { IDLE, OFF, SINGLE_CAPTURE, CAPTURE_STREAM, ERROR };
enum class NetworkState { DISCONNECTED, CONNECTING, CONNECTED, ERROR };

class DeviceStateManager {
public:
    DeviceStateManager();

    // Query states
    PowerState getPowerState() const;
    CameraState getCameraState() const;
    NetworkState getNetworkState() const;

    // power state events
    void setPowerMode(PowerState state);
 

    // TODO CHANGE THESE TO ONE PARAMETERIZED FUNCTION
    // camera state events
    void requestCameraOn();
    void requestCameraOff();
    void requestSingleCapture();
    void requestCaptureStream();

    // Network state events
    void networkConnected();
    void networkDisconnected();

private:
    PowerState powerState_;
    CameraState cameraState_;
    NetworkState networkState_;
};

#endif // DEVICE_STATE_H
