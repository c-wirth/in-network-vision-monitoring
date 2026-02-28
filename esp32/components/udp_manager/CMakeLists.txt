idf_component_register(
    SRCS "UDPManager.cpp"
    INCLUDE_DIRS "."
    REQUIRES
        esp_wifi
        lwip
        freertos
	esp32-camera
)
