idf_component_register(
    SRCS LEDDriver.cpp
    INCLUDE_DIRS "."
    REQUIRES driver freertos esp_driver_gpio #Dependencies (GPIO, FreeRTOS for tasks)
)
