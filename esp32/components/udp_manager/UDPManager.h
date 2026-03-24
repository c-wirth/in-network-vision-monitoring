#pragma once
// UDPManager.h
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_err.h"
#include "esp_camera.h"
#include "lwip/sockets.h"

#include <functional>

#define UDP_SERVER_IP                  CONFIG_SERVER_IP
#define UDP_SERVER_FRAME_PORT          CONFIG_SERVER_FRAME_PORT
#define UDP_DEVICE_CONTROL_PORT        CONFIG_DEVICE_CONTROL_PORT
#define UDP_HANDSHAKE_MAX_RETRIES      CONFIG_UDP_HANDSHAKE_MAX_RETRIES
#define UDP_HANDSHAKE_PING_INTERVAL_MS CONFIG_UDP_HANDSHAKE_PING_INTERVAL_MS
#define UDP_ALIVE_TIMEOUT_MS           CONFIG_UDP_ALIVE_TIMEOUT_MS

#define TASK_STOP_TIMEOUT_MS         pdMS_TO_TICKS(2000)
#define TASK_STOP_POLL_MS            pdMS_TO_TICKS(1)
#define UDP_QUEUE_RECEIVE_TIMEOUT_MS pdMS_TO_TICKS(100)


enum class UDPEvent {
    HANDSHAKE_ACK,
    START_STREAM,
    STOP_STREAM,
    PACKET_LOSS,
    CONNECTION_LOSS
};

class UDPManager {
public:
    using EventCallback = std::function<void(UDPEvent)>;

    static esp_err_t init(QueueHandle_t frame_queue);
    static esp_err_t connect();
    static esp_err_t deinit();
    static esp_err_t sendHandshake();
    static esp_err_t startStream();
    static esp_err_t stopStream();
    static void setEventCallback(EventCallback cb);
    static bool isStreaming();
    static bool isInitialized();


private:
    static bool initialized_;
    static bool streaming_;

    static int send_sock_;
    static int recv_sock_;

    static TaskHandle_t send_task_handle_;
    static TaskHandle_t recv_task_handle_;

    static QueueHandle_t frame_queue_;
    static EventCallback event_callback_;

    static struct sockaddr_in server_addr_;

    static volatile bool connected_;
    static volatile TickType_t last_alive_tick_;

    static void udpSendTask(void* param);
    static void udpReceiveTask(void* param);
};
