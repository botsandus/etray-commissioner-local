# etray-commissioner-local
Commissioning tools for the E-tray of the ARRI robot. Fully offline — no internet or GitHub account required.

## Prerequisites

**Run once on the target machine before installing:**

1. Install python3-venv:
   ```bash
   sudo apt install python3-venv
   ```

2. Install tkinter:
   ```bash
   sudo apt install python3-tk
   ```

3. Install the `libusb-dev` package:
   ```bash
   sudo apt install libusb-dev
   ```

## Installation

1. Copy the `etray-commissioner-local` folder from the USB stick to the target machine.

2. Run the install script:
   ```bash
   cd etray-commissioner-local
   ./install.sh
   ```

## Usage

```bash
./run.sh
```

## Updating the USB Package

Run this on the development machine after making changes:

```bash
./build_usb.sh
```

Before copying to the USB stick, place the shared SSH key in the `ssh/` folder:

```bash
cp ~/.ssh/dexory_shared.key ssh/dexory_shared.key
```

Then copy the updated folder to the USB stick.
