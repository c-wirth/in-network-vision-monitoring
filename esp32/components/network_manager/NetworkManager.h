#pragma once

// NetworkManager.h
// Handles Wi-Fi connectivity and UDP network communication.
// Fires events to DeviceStateManager on connection/disconnection.

#include "esp_wifi.h"
#include "sdkconfig.h"
#include "esp_err.h"
#include <functional>

#include "esp_event.h"

class NetworkManager {
public:
    NetworkManager();


    // Set the callback for network events
    using EventCallback = std::function<void(esp_event_base_t base, int32_t event_id, void* event_data)>;


     /** 
     * @brief Register a callback to receive Wi-Fi / IP events.
     * @param cb Function or lambda matching EventCallback signature.
     */
    static void setEventCallback(EventCallback cb);


    /**
    * @brief method for connect initializes wifi manager by enabling the esp wifi driver
    *
    * This does not faciliate the connection to any network, it simple allocates space for WiFi in memory
    *
     * @return ESP_OK on success, or if already initialized (idempotent)
     * @return ESP_ERR_INVALID_ARG or ESP_ERR_NOT_SUPPORTED if esp_pm calls fail
    */
    static esp_err_t init();

    // Start connection to configured WiFi -automatically boots up wifi driver
    static esp_err_t connect();


    // stop connection to configured WiFi
    static esp_err_t disconnect();


    // turn off wifi driver
    static esp_err_t shutdown();




private:

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


    /**
     * @brief Callback handler for Wi-Fi events from the ESP-IDF event loop.
     *
     * This static method is registered with the ESP-IDF event system to handle
     * Wi-Fi-related events for the station interface (STA). It interprets the
     * event base and ID, and optionally uses the event data to trigger higher-level
     * actions, such as notifying the device state manager of connection or
     * disconnection events.
     *
     * @param base The event base. For Wi-Fi events, this will always be WIFI_EVENT.
     *             It identifies the subsystem that generated the event.
     *
     * @param event_id The specific event within the Wi-Fi subsystem. Common values
     *                 include:
     *                 - WIFI_EVENT_STA_START:   Station interface has started
     *                 - WIFI_EVENT_STA_CONNECTED: Station successfully connected to an AP
     *                 - WIFI_EVENT_STA_DISCONNECTED: Station disconnected from an AP
     *
     * @param event_data Pointer to event-specific data. For Wi-Fi station events,
     *                   this typically points to a structure such as:
     *                   - wifi_event_sta_disconnected_t* for disconnect events
     *                   - wifi_event_sta_connected_t* for connect events
     *                   Cast this pointer to the correct type depending on event_id.
     *
     * @note This method should not be called directly by application code. Instead,
     *       it is automatically invoked by the ESP-IDF event loop when a Wi-Fi
     *       event occurs.
     *
     * @note This handler currently only processes Wi-Fi STA events and ignores
     *       other event bases.
     */
    static void handle_event_(esp_event_base_t base, int32_t event_id, void* event_data);

    static EventCallback event_callback_;

    static bool initialized_;
    static esp_ip4_addr_t ipAddr_;


};

