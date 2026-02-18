idf_component_register(
    SRCS NetworkManager.cpp
    INCLUDE_DIRS "."
    REQUIRES esp_wifi esp_netif esp_event log nvs_flash 
)
