# etray-commissioner-local
Commissioning tools for the E-tray of the ARRI robot.

---

## 1. Pull the latest version

```bash
git clone https://github.com/botsandus/etray-commissioner-local
cd etray-commissioner-local
git pull
```

---

## 2. Prepare for offline installation

Run this on the development machine to bundle all dependencies:

```bash
./build_usb.sh
cp ~/.ssh/dexory_shared.key ssh/dexory_shared.key
```

Then copy the entire `etray-commissioner-local` folder to a USB stick.

---

## 3. Install on target machine

On the target machine, run once to install system dependencies:

```bash
sudo apt install python3-venv python3-tk libusb-dev
```

Then install the tool from the USB stick:

```bash
cd etray-commissioner-local
./install.sh
```

Open a new terminal and run:

```bash
etray-commissioner
```
