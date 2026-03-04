# parts-commissioner
commissioning tools for the parts of the ARRI robot.

## Prerequisites

**Please ensure that you do the following before installing parts-commissioner. You only need to do this once!**

1. Install the Github cli tool:
   ```bash
   sudo apt install gh
   ```

2. Log into the Github cli tool by running the following command and following the instructions:
   ```bash
   gh auth login --web
   ```

3. Configure the Github cli tool:
   ```bash
   gh auth setup-git
   ```

4. Install pipx packaging tool:
   ```bash
   sudo apt install pipx
   ```

5. Install tkinter:
   ```bash
   sudo apt install python3-tk
   ```

6. Install the `libusb-dev` package:
   ```bash
   sudo apt install libusb-dev
   ```

7. Finally, add pipx to your path:
   ```bash
   pipx ensurepath
   ```

## Installation and Usage

1. Run the following command to install the tool:

    ```bash
    pipx install git+https://github.com/botsandus/parts-commissioner.git
    ```

2. Now you can run the tool by calling it from a terminal anywhere:

    ```bash
    parts-commissioner
    ```
