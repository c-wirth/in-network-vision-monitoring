// NetworkManager.h
// Handles Wi-Fi connectivity and UDP network communication.
// Fires events to DeviceStateManager on connection/disconnection.

#ifndef NETWORK_MANAGER_H
#define NETWORK_MANAGER_H

class NetworkManager {
public:
    NetworkManager();

    // Initialize Wi-Fi
    void initWiFi(const char* ssid, const char* password);

    // Start / stop network
    void connect();
    void disconnect();

    // Periodically check status
    bool isConnected() const;

private:
    bool connected_;
};

#endif // NETWORK_MANAGER_H
