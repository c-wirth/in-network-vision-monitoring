idf_component_register(
    SRCS "main.cpp"
    INCLUDE_DIRS "."
    REQUIRES camera_manager frame_buffer frame_encoder led_driver power_manager network_manager state tests esp32-camera
)
