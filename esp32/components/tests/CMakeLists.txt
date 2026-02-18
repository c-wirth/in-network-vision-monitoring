idf_component_register(
    SRCS PowerStateTests.cpp
    INCLUDE_DIRS "."
    REQUIRES esp_pm log led_driver network_manager power_manager unity
)
