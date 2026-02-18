idf_component_register(
    SRCS CameraManager.cpp            # source files in this component
    INCLUDE_DIRS "."                  # expose headers in this folder
    REQUIRES driver esp32-camera
)
