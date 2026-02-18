// PowerStateTests.cpp
#include "unity.h"
#include "DeviceState.h"
#include "PowerManager.h"
#include "LEDDriver.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char* TAG = "PowerStateTests";

static DeviceStateManager deviceState;

// --- Helpers ---
static void wait_for_hardware(int ms) {
    // Give time for LEDs or power changes to take effect
    vTaskDelay(pdMS_TO_TICKS(ms));
}

// --- setUp / tearDown ---
void setUp(void) {
    ESP_LOGI(TAG, "Test setup: starting from IDLE state");
    deviceState.setPowerState(PowerState::IDLE);
    wait_for_hardware(500);
}

void tearDown(void) {
    ESP_LOGI(TAG, "Test teardown: reset to IDLE");
    deviceState.setPowerState(PowerState::IDLE);
    wait_for_hardware(500);
}

// --- TEST CASES ---

void test_HighPowerMode(void) {
    ESP_LOGI(TAG, "Setting HIGH_POWER");
    deviceState.setPowerState(PowerState::HIGH_POWER);
    wait_for_hardware(500);

    TEST_ASSERT_EQUAL_INT(PowerState::HIGH_POWER, deviceState.getPowerState());
}

void test_IdleMode(void) {
    ESP_LOGI(TAG, "Setting IDLE");
    deviceState.setPowerState(PowerState::IDLE);
    wait_for_hardware(500);

    TEST_ASSERT_EQUAL_INT(PowerState::IDLE, deviceState.getPowerState());
}

void test_ErrorMode(void) {
    ESP_LOGI(TAG, "Forcing ERROR state via invalid value");
    deviceState.setPowerState((PowerState)999); // invalid triggers ERROR
    wait_for_hardware(500);

    TEST_ASSERT_EQUAL_INT(PowerState::ERROR, deviceState.getPowerState());
}

void test_CycleAllStates(void) {
    ESP_LOGI(TAG, "Cycle: IDLE -> HIGH_POWER -> IDLE -> ERROR -> IDLE");

    deviceState.setPowerState(PowerState::IDLE);
    wait_for_hardware(200);
    TEST_ASSERT_EQUAL_INT(PowerState::IDLE, deviceState.getPowerState());

    deviceState.setPowerState(PowerState::HIGH_POWER);
    wait_for_hardware(200);
    TEST_ASSERT_EQUAL_INT(PowerState::HIGH_POWER, deviceState.getPowerState());

    deviceState.setPowerState(PowerState::IDLE);
    wait_for_hardware(200);
    TEST_ASSERT_EQUAL_INT(PowerState::IDLE, deviceState.getPowerState());

    deviceState.setPowerState((PowerState)999); // force ERROR
    wait_for_hardware(200);
    TEST_ASSERT_EQUAL_INT(PowerState::ERROR, deviceState.getPowerState());

    deviceState.setPowerState(PowerState::IDLE);
    wait_for_hardware(200);
    TEST_ASSERT_EQUAL_INT(PowerState::IDLE, deviceState.getPowerState());
}

void test_HighPowerToggleStress(void) {
    for (int i = 0; i < 5; ++i) {
        ESP_LOGI(TAG, "Toggle HIGH_POWER #%d", i + 1);
        deviceState.setPowerState(PowerState::HIGH_POWER);
        wait_for_hardware(100);

        deviceState.setPowerState(PowerState::IDLE);
        wait_for_hardware(100);

        TEST_ASSERT_EQUAL_INT(PowerState::IDLE, deviceState.getPowerState());
    }
}

// --- MAIN ---
extern "C" void app_main(void) {
    UNITY_BEGIN();

    RUN_TEST(test_HighPowerMode);
    RUN_TEST(test_IdleMode);
    RUN_TEST(test_ErrorMode);
    RUN_TEST(test_CycleAllStates);
    RUN_TEST(test_HighPowerToggleStress);

    UNITY_END();
}
}
