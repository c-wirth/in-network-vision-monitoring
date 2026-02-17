idf_component_register(
    SRCS DeviceState.cpp              # source files in this component
    INCLUDE_DIRS "."                  # expose headers in this folder
    REQUIRES esp_pm log               # dependencies for locks and logging
)
