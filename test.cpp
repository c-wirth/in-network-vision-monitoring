// UDPManager.cpp

#include "UDPManager.h"
#include "esp_log.h"

#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>

static const char* TAG = "UDPManager";

// --- static member definitions ---
bool UDPManager::initialized_           = false;
bool UDPManager::streaming_             = false;

int  UDPManager::send_sock_             = -1;
int  UDPManager::recv_sock_             = -1;

TaskHandle_t UDPManager::send_task_handle_ = nullptr;
TaskHandle_t UDPManager::recv_task_handle_ = nullptr;

QueueHandle_t UDPManager::frame_queue_  = nullptr;
UDPManager::EventCallback UDPManager::event_callback_ = nullptr;

struct sockaddr_in UDPManager::server_addr_ = {};


// --- packet layout ---
// | frame_id (2) | frag_id (2) | total_frags (2) | flags (2) | payload |
#define UDP_HEADER_SIZE   8
#define UDP_MTU           1400
#define UDP_PAYLOAD_SIZE  (UDP_MTU - UDP_HEADER_SIZE)

// --- flags ---
#define FLAG_HANDSHAKE      0x0001
#define FLAG_HANDSHAKE_ACK  0x0002
#define FLAG_STOP_STREAM    0x0004
#define FLAG_START_STREAM   0x0008
#define FLAG_PACKET_LOSS    0x0010


esp_err_t UDPManager::init(QueueHandle_t frame_queue) {
    if (initialized_) {
        ESP_LOGW(TAG, "UDPManager already initialized");
        return ESP_OK;
    }

    if (frame_queue == nullptr) {
        ESP_LOGE(TAG, "UDPManager::init() failed: frame_queue is null");
        return ESP_ERR_INVALID_ARG;
    }

    frame_queue_ = frame_queue;

    // --- send socket ---
    send_sock_ = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (send_sock_ < 0) {
        ESP_LOGE(TAG, "Failed to create send socket: errno %d", errno);
        return ESP_FAIL;
    }

    memset(&server_addr_, 0, sizeof(server_addr_));
    server_addr_.sin_family      = AF_INET;
    server_addr_.sin_port        = htons(UDP_SERVER_FRAME_PORT);
    inet_aton(UDP_SERVER_IP, &server_addr_.sin_addr);

    // --- receive socket ---
    recv_sock_ = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (recv_sock_ < 0) {
        ESP_LOGE(TAG, "Failed to create receive socket: errno %d", errno);
        close(send_sock_);
        send_sock_ = -1;
        return ESP_FAIL;
    }

    struct sockaddr_in recv_addr = {};
    recv_addr.sin_family         = AF_INET;
    recv_addr.sin_port           = htons(UDP_DEVICE_CONTROL_PORT);
    recv_addr.sin_addr.s_addr    = INADDR_ANY;

    if (bind(recv_sock_, (struct sockaddr*)&recv_addr, sizeof(recv_addr)) < 0) {
        ESP_LOGE(TAG, "Failed to bind receive socket: errno %d", errno);
        close(send_sock_);
        close(recv_sock_);
        send_sock_ = recv_sock_ = -1;
        return ESP_FAIL;
    }

    // 50ms timeout so receive task loop can check initialized_ periodically
    struct timeval timeout = { .tv_sec = 0, .tv_usec = 50000 };
    setsockopt(recv_sock_, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

    initialized_ = true;

    // --- launch receive task ---
    BaseType_t ret = xTaskCreate(
        udpReceiveTask,
        "UDPReceiveTask",
        4096,
        nullptr,
        9,
        &recv_task_handle_
    );

    if (ret != pdPASS) {
        ESP_LOGE(TAG, "Failed to create UDP receive task");
        close(send_sock_);
        close(recv_sock_);
        send_sock_ = recv_sock_ = -1;
        initialized_ = false;
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "UDPManager initialized");
    return ESP_OK;
}


esp_err_t UDPManager::deinit() {
    if (!initialized_) return ESP_OK;

    if (streaming_) stopStream();

    initialized_ = false;

    const TickType_t timeout       = pdMS_TO_TICKS(2000);
    const TickType_t poll_interval = pdMS_TO_TICKS(1);
    TickType_t elapsed = 0;

    // wait for receive task
    while (recv_task_handle_ != nullptr) {
        if (elapsed >= timeout) {
            ESP_LOGE(TAG, "deinit timed out waiting for receive task");
            return ESP_ERR_TIMEOUT;
        }
        vTaskDelay(poll_interval);
        elapsed += poll_interval;
    }

    close(send_sock_);
    close(recv_sock_);
    send_sock_ = recv_sock_ = -1;

    ESP_LOGI(TAG, "UDPManager deinitialized");
    return ESP_OK;
}


esp_err_t UDPManager::sendHandshake() {
    if (!initialized_) {
        ESP_LOGE(TAG, "UDPManager::sendHandshake() called before init");
        return ESP_ERR_INVALID_STATE;
    }

    uint8_t packet[UDP_HEADER_SIZE] = {};
    packet[6] = (FLAG_HANDSHAKE >> 8) & 0xFF;
    packet[7] =  FLAG_HANDSHAKE & 0xFF;

    int sent = sendto(send_sock_, packet, UDP_HEADER_SIZE, 0,
                      (struct sockaddr*)&server_addr_, sizeof(server_addr_));
    if (sent < 0) {
        ESP_LOGE(TAG, "sendHandshake failed: errno %d", errno);
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Handshake sent");
    return ESP_OK;
}


esp_err_t UDPManager::startStream() {
    if (!initialized_) {
        ESP_LOGE(TAG, "UDPManager::startStream() called before init");
        return ESP_ERR_INVALID_STATE;
    }
    if (streaming_) {
        ESP_LOGW(TAG, "UDPManager::startStream() already streaming");
        return ESP_ERR_INVALID_STATE;
    }

    streaming_ = true;

    BaseType_t ret = xTaskCreate(
        udpSendTask,
        "UDPSendTask",
        8192,
        nullptr,
        9,
        &send_task_handle_
    );

    if (ret != pdPASS) {
        ESP_LOGE(TAG, "Failed to create UDP send task");
        streaming_ = false;
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "UDP stream started");
    return ESP_OK;
}


esp_err_t UDPManager::stopStream() {
    if (!streaming_) {
        ESP_LOGW(TAG, "UDPManager::stopStream() called but not streaming");
        return ESP_OK;
    }

    streaming_ = false;

    const TickType_t timeout       = pdMS_TO_TICKS(2000);
    const TickType_t poll_interval = pdMS_TO_TICKS(1);
    TickType_t elapsed = 0;

    while (send_task_handle_ != nullptr) {
        if (elapsed >= timeout) {
            ESP_LOGE(TAG, "stopStream timed out waiting for send task");
            return ESP_ERR_TIMEOUT;
        }
        vTaskDelay(poll_interval);
        elapsed += poll_interval;
    }

    ESP_LOGI(TAG, "UDP stream stopped");
    return ESP_OK;
}


void UDPManager::setEventCallback(EventCallback cb) {
    event_callback_ = cb;
}


// --- send task ---
void UDPManager::udpSendTask(void* param) {
    uint16_t frame_id = 0;

    while (streaming_) {
        camera_fb_t* fb = nullptr;

        if (xQueueReceive(frame_queue_, &fb, pdMS_TO_TICKS(20)) == pdPASS && fb != nullptr) {

            uint16_t total_frags = (fb->len + UDP_PAYLOAD_SIZE - 1) / UDP_PAYLOAD_SIZE;

            for (uint16_t i = 0; i < total_frags; i++) {
                uint8_t  packet[UDP_MTU];
                size_t   offset = i * UDP_PAYLOAD_SIZE;
                size_t   chunk  = (fb->len - offset < UDP_PAYLOAD_SIZE)
                                    ? fb->len - offset
                                    : UDP_PAYLOAD_SIZE;

                packet[0] = (frame_id >> 8) & 0xFF;
                packet[1] =  frame_id & 0xFF;
                packet[2] = (i >> 8) & 0xFF;
                packet[3] =  i & 0xFF;
                packet[4] = (total_frags >> 8) & 0xFF;
                packet[5] =  total_frags & 0xFF;
                packet[6] = 0;
                packet[7] = 0;

                memcpy(packet + UDP_HEADER_SIZE, fb->buf + offset, chunk);

                sendto(send_sock_, packet, UDP_HEADER_SIZE + chunk, 0,
                       (struct sockaddr*)&server_addr_, sizeof(server_addr_));
            }

            frame_id++;
            esp_camera_fb_return(fb);
        }
    }

    ESP_LOGI(TAG, "UDP send task exiting");
    send_task_handle_ = nullptr;
    vTaskDelete(nullptr);
}


// --- receive task ---
void UDPManager::udpReceiveTask(void* param) {
    uint8_t rx_buf[UDP_MTU];

    while (initialized_) {
        struct sockaddr_in src_addr;
        socklen_t src_len = sizeof(src_addr);

        int len = recvfrom(recv_sock_, rx_buf, sizeof(rx_buf), 0,
                           (struct sockaddr*)&src_addr, &src_len);

        if (len < 0) {
            // timeout or error — loop back and check initialized_
            continue;
        }

        if (len < UDP_HEADER_SIZE) {
            ESP_LOGW(TAG, "Malformed packet received (%d bytes) — ignoring", len);
            continue;
        }

        uint16_t flags = (rx_buf[6] << 8) | rx_buf[7];

        if (flags & FLAG_HANDSHAKE_ACK) {
            ESP_LOGI(TAG, "Handshake ACK received");
            if (event_callback_) event_callback_(UDP_EVENT_HANDSHAKE_ACK);
        }
        else if (flags & FLAG_START_STREAM) {
            ESP_LOGI(TAG, "START_STREAM received from server");
            startStream();
        }
        else if (flags & FLAG_STOP_STREAM) {
            ESP_LOGI(TAG, "STOP_STREAM received from server");
            stopStream();
        }
        else if (flags & FLAG_PACKET_LOSS) {
            uint8_t loss_pct = (len > UDP_HEADER_SIZE) ? rx_buf[UDP_HEADER_SIZE] : 0;
            ESP_LOGW(TAG, "Packet loss report: %u%%", loss_pct);
            if (event_callback_) event_callback_(UDP_EVENT_PACKET_LOSS);
        }
    }

    ESP_LOGI(TAG, "UDP receive task exiting");
    recv_task_handle_ = nullptr;
    vTaskDelete(nullptr);
}
