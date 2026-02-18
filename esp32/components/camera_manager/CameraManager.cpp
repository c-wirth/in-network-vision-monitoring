// CameraManager.cpp

#include "CameraManager.h"
#include "esp_log.h"
#include "esp_camera.h"


static const char* TAG = "CameraManager";

// Freenove ESP32-S3 Camera pin mapping
#define CAM_PIN_D0      11
#define CAM_PIN_D1      9
#define CAM_PIN_D2      8
#define CAM_PIN_D3      10
#define CAM_PIN_D4      12
#define CAM_PIN_D5      18
#define CAM_PIN_D6      17
#define CAM_PIN_D7      16

#define CAM_PIN_XCLK    15
#define CAM_PIN_PCLK    13
#define CAM_PIN_VSYNC   6
#define CAM_PIN_HREF    7

#define CAM_PIN_SIOD    4
#define CAM_PIN_SIOC    5

#define CAM_PIN_PWDN   -1
#define CAM_PIN_RESET  -1

bool CameraManager::initialized_ = false;
bool CameraManager::streaming_ = false;
TaskHandle_t CameraManager::stream_task_handle_ = nullptr;
TickType_t CameraManager::stream_interval_ = 0;

esp_err_t CameraManager::init() {
    if (initialized_) {
        ESP_LOGW(TAG, "CameraManager already initialized");
        return ESP_OK;
    }

    camera_config_t config = {};
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;

    // Pin mapping
    config.pin_d0 = CAM_PIN_D0;
    config.pin_d1 = CAM_PIN_D1;
    config.pin_d2 = CAM_PIN_D2;
    config.pin_d3 = CAM_PIN_D3;
    config.pin_d4 = CAM_PIN_D4;
    config.pin_d5 = CAM_PIN_D5;
    config.pin_d6 = CAM_PIN_D6;
    config.pin_d7 = CAM_PIN_D7;

    config.pin_xclk = CAM_PIN_XCLK;
    config.pin_pclk = CAM_PIN_PCLK;
    config.pin_vsync = CAM_PIN_VSYNC;
    config.pin_href = CAM_PIN_HREF;

    config.pin_sccb_sda = CAM_PIN_SIOD;
    config.pin_sccb_scl = CAM_PIN_SIOC;

    config.pin_pwdn  = CAM_PIN_PWDN;
    config.pin_reset = CAM_PIN_RESET;

    config.xclk_freq_hz = 10000000; // 10 MHz for Freenove
    config.pixel_format = PIXFORMAT_JPEG;

    config.frame_size   = FRAMESIZE_VGA; 
    config.jpeg_quality = 12;
    config.fb_count     = 2;
    config.grab_mode    = CAMERA_GRAB_LATEST;
    config.fb_location  = CAMERA_FB_IN_PSRAM; // use PSRAM

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Camera init failed: 0x%x", err);
        return err;
    }

    initialized_ = true;
    ESP_LOGI(TAG, "Camera initialized successfully");
    return ESP_OK;
}


esp_err_t CameraManager::deinit() {
    if (!initialized_) return ESP_OK;

    if (streaming_) {
        ESP_LOGW(TAG, "CameraManager::deinit() called while streaming, stopping stream first");
        esp_err_t ret = CameraManager::stopStream();
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "CameraManager::deinit() failed to stop stream: %s", esp_err_to_name(ret));
            return ret;
        }
    }

    esp_err_t ret = esp_camera_deinit();
    if (ret == ESP_OK) initialized_ = false;
    return ret;
}


camera_fb_t* CameraManager::captureFrame() {
    if (!initialized_) {
        ESP_LOGE(TAG, "CameraManager not initialized");
        return nullptr;
    }
    return esp_camera_fb_get();
}


void CameraManager::returnFrame(camera_fb_t* fb) {
    if (fb) {
        esp_camera_fb_return(fb);
    }
    else {
	ESP_LOGW(TAG, "CameraManager::returnFrame was called without a frame buffer (fb)");
    }
}



esp_err_t CameraManager::startStream(uint32_t fps) {

	if (!initialized_) {
		ESP_LOGE(TAG, "CameraManager::startStream() failed: camera not initialized");
		return ESP_ERR_INVALID_STATE;
	}

	if (streaming_) {
		ESP_LOGW(TAG, "CameraManager::startStream() called but stream already running");
		return ESP_ERR_INVALID_STATE;
    }

	if (fps == 0) {
		ESP_LOGE(TAG, "CameraManager::startStream() failed: fps cannot be 0");
		return ESP_ERR_INVALID_ARG;
	}

	streaming_ = true;

	// convert fps to ticks for RTOS xTaskCreate 
	stream_interval_ = fpsToTicks(fps);


	ESP_LOGI(TAG, "Executing CameraManager::startStream() at %u FPS", fps);

	BaseType_t ret = xTaskCreate(
		streamTask,
		"CameraStreamTask",
		8192, // stack size
		nullptr,
		10, // task priority
		&stream_task_handle_
	);
	if (ret != pdPASS) {
		ESP_LOGE(TAG, "Failed to start camera streaming task");
		streaming_ = false;
		return ESP_FAIL;
	}

return ESP_OK;
}


esp_err_t CameraManager::stopStream() {
    if (!streaming_) {
        ESP_LOGW(TAG, "CameraManager::stopStream called but stream was not running");
        return ESP_OK;
    }

    streaming_ = false;

    const TickType_t timeout = pdMS_TO_TICKS(2000); // 2 second timeout
    const TickType_t poll_interval = pdMS_TO_TICKS(1);
    TickType_t elapsed = 0;

    while (stream_task_handle_ != nullptr) {
        if (elapsed >= timeout) {
            ESP_LOGE(TAG, "CameraManager::stopStream timed out waiting for stream task to exit");
            return ESP_ERR_TIMEOUT;
        }
        vTaskDelay(poll_interval);
        elapsed += poll_interval;
    }

    ESP_LOGI(TAG, "Camera stream stopped successfully");
    return ESP_OK;
}


bool CameraManager::isStreaming() {
    return streaming_;
}


bool CameraManager::isInitialized() {
    return initialized_;
}


// --- streaming task ---
void CameraManager::streamTask(void* param) {

    TickType_t interval = stream_interval_;

    while (streaming_) {
        camera_fb_t* fb = CameraManager::captureFrame();
        if (fb) {

        ESP_LOGI(TAG,
                 "Frame: %ux%u | %u bytes | ts: %ld.%06ld",
                 fb->width,
                 fb->height,
                 fb->len,
                 fb->timestamp.tv_sec,
                 fb->timestamp.tv_usec);


	CameraManager::returnFrame(fb);
        } else {
            ESP_LOGE(TAG, "Failed to capture frame during streaming");
        }
        vTaskDelay(interval);
    }

    ESP_LOGI(TAG, "Camera streaming task stopped");
    stream_task_handle_ = nullptr;
    vTaskDelete(nullptr);
}

