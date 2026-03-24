idf_component_register(
    SRCS "main.cpp"
    INCLUDE_DIRS "."
    REQUIRES camera_manager led_driver network_manager state tests esp32-camera esp_wifi
)
