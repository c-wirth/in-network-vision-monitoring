#pragma once

// NetworkManager.h
// Handles Wi-Fi connectivity and UDP network communication.
// Fires events to DeviceStateManager on connection/disconnection.

#include "esp_wifi.h"
#include "sdkconfig.h"
#include "esp_err.h"

#include "esp_event.h"

class NetworkManager {
public:
    NetworkManager();

    /**
    * @brief initializes wifi manager by enabling the esp wifi driver
    *
    * This does not faciliate the connection to any network, it simple allocates space for WiFi in memory
    *
     * @return ESP_OK on success, or if already initialized (idempotent)
     * @return ESP_ERR_INVALID_ARG or ESP_ERR_NOT_SUPPORTED if esp_pm calls fail
    */
    static esp_err_t init()

    /**
    * @brief Frees all resoureces allocated for the wifi task allocated by init
    *
    * @return ESP_OK on success, or if not initialized (idempotent)
    * @return ESP_ERR_INVALID_ARG or ESP_ERR_NOT_SUPPORTED if esp_pm calls fail
    */
    static esp_err_t deinit()

    // Start connection to configured WiFi
    static esp_err_t connect();

    // stop connection to configured WiFi
    static esp_err_t disconnect();

    // get the current IP as a string
    static const char* getIPAddress();

private:
    // Internal event handler
    static void eventHandler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data);

    // Internal state update
    static void handleEvent(esp_event_base_t base, int32_t id, void* data);

    static bool initialized_;
    static esp_ip4_addr_t ipAddr_;


    /**
     * @brief Build a WiFi configuration struct for STA connection.
     *
     * Constructs a local `wifi_config_t` struct with SSID and password
     * retrieved from Kconfig macros (CONFIG_WIFI_SSID, CONFIG_WIFI_PASSWORD).
     * This struct is stack-allocated and returned by value; no internal
     * state is stored in the NetworkManager.
     *
     * @return wifi_config_t A fully populated WiFi configuration struct ready
     *         to be passed to `esp_wifi_set_config()` for connecting to the AP.
     *         Its members are:
     *           - `sta.ssid` set to CONFIG_WIFI_SSID
     *           - `sta.password` set to CONFIG_WIFI_PASSWORD
     *           - `sta.threshold.authmode` set to WIFI_AUTH_WPA2_PSK
     *           - `sta.pmf_cfg.capable` set to true (enables protected management frames)
     *
     * @note This is a private, internal helper. The FSM or external modules
     *       should not call this directly. Used internally by `connect()`.
     */
    static wifi_config_t get_wifi_config_();
};

