idf_component_register(
    SRCS DeviceState.cpp            	  		# source files in this component
    INCLUDE_DIRS "."                	  		# expose headers in this folder
    REQUIRES esp_pm log power_manager led_driver       # dependencies for locks and logging
)
