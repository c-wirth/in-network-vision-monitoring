#pragma once

// ServerConnectionManager.h
// Handles server-specific connection state (handshake, commands, disconnects).
// Interacts with DeviceStateManager for state updates.

enum class ServerConnectionState { DISCONNECTED, CONNECTING, CONNECTED, ERROR };

class ServerConnectionManager {
public:
    ServerConnectionManager();

    // Start / stop handshake
    void requestHandshake();
    void disconnect();

    // Query state
    ServerConnectionState getServerState() const;

private:
    ServerConnectionState serverState_;

    // Internal helper
    void enterServerState(ServerConnectionState newState);
};
