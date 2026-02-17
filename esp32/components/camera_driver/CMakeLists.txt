idf_component_register(
    SRCS CameraDriver.cpp             # source files in this component
    INCLUDE_DIRS "."                  # expose headers in this folder
    REQUIRES driver                   # ESP32 driver library (if using camera APIs)
)
