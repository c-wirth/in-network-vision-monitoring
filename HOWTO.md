# ESP32-S3 Development Workflow

This guide outlines the steps to build, flash, and monitor an ESP32-S3 project using ESP-IDF.

---

## 1. Set Target

Before building, make sure the project target is set to **ESP32-S3**:

```bash
idf.py set-target esp32s3
```

You only need to do this once per project (or after changing targets).

---

## 2. Clean the Build Directory

To remove all previous build artifacts:

```bash
idf.py fullclean
```

> Alternatively, you can manually delete the `build/` directory.

---

## 3. Build the Project

Compile the project with:

```bash
idf.py build
```

This will generate the firmware binaries in the `build/` directory.

---

## 4. Flash the Board and Monitor Output

Connect your ESP32-S3 via a USB-to-Serial adapter and run:

```bash
idf.py -p /dev/cu.wchusbserial5AB90094641 flash monitor
```

* Replace `/dev/cu.wchusbserial5AB90094641` with your serial port if different.
* The command will flash the firmware and start the serial monitor.

---

## 5. Serial Monitor Shortcuts

* Quit monitor: `Ctrl+]`
* Open monitor menu: `Ctrl+T`
* Help in monitor menu: `Ctrl+T` then `Ctrl+H`
