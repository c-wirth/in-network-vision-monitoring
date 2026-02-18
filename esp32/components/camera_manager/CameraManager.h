// CameraManager.h
#pragma once

#include "esp_err.h"
#include "esp_camera.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

class CameraManager {
public:
    static esp_err_t init();
    static esp_err_t deinit();

    static camera_fb_t* captureFrame();
    static void returnFrame(camera_fb_t* fb);

    // Streaming interface
    static esp_err_t startStream(uint32_t fps = 30); // default 30 fps
    static esp_err_t stopStream();
    static bool isStreaming();
    static bool isInitialized();

private:
    static bool initialized_;
    static bool streaming_;
    static TaskHandle_t stream_task_handle_; // pointer to the video stream capture task
    static TickType_t stream_interval_;

    static void streamTask(void* param);

    static inline TickType_t fpsToTicks(uint32_t fps) {
        return pdMS_TO_TICKS(1000 / fps);
    }

};
