# Portable QEMU Launcher

A lightweight, portable Python-based GUI launcher for QEMU virtual machines. Designed to run on both Linux and Windows (in portable mode).

![QEMU Launcher](https://github.com/user-attachments/assets/placeholder.png)

## Features

- **Portable**: Run from a USB stick on Windows without installation (if QEMU binaries are provided).
- **Simple GUI**: Check, add, edit, and launch VMs easily with a modern interface (CustomTkinter).
- **Process Management**: Launch and Stop VMs directly from the dashboard.
- **Quick Launch**: Instantly boot an ISO file for testing without creating a full VM config.
- **Multi-OS Support**: Automatically detects QEMU on Linux (system path) or locally on Windows.

## Installation

### Prerequisites

#### Windows
1. **Python 3**: Download and install [Python 3.10 or newer](https://www.python.org/downloads/windows/).
   - **Important**: During installation, check the box **"Add Python to PATH"**.
2. **Dependencies**: You must install the required libraries (see below).

#### Linux
1. **Python 3**: Usually pre-installed. Ensure you have `python3-pip` and `python3-venv` (optional but recommended).
2. **QEMU**: Ensure QEMU system and GUI packages are installed:
   ```bash
   sudo apt update
   sudo apt install qemu-system-x86 qemu-system-gui python3-pip
   ```

### Setting up the Environment

It is recommended to use a virtual environment or install dependencies directly (if preferred).

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/portable-qemu-launcher.git
   cd portable-qemu-launcher
   ```

2. Install Python dependencies (Windows & Linux):
   Open your terminal (CMD/PowerShell on Windows) in the project folder and run:
   ```bash
   pip install -r requirements.txt
   ```
   *Note for Linux users: If you encounter an "externally-managed-environment" error, use `pip install -r requirements.txt --break-system-packages`.*

## Usage

Run the application:
```bash
python main.py
```

### Windows Portable Mode (No Admin Rights)
To carry this app on a USB stick or use it without administrator privileges:

1. Download the [QEMU for Windows installer](https://qemu.weilnetz.de/w64/) (e.g., `qemu-w64-setup-....exe`).
2. **Do not run it**. Instead, right-click the `.exe` and open it with **7-Zip** (or similar).
3. Extract the contents into a folder named `qemu` **inside** this project's directory.
   - You should end up with: `.../portable-qemu-launcher/qemu/qemu-system-x86_64.exe`
4. The launcher will automatically detect it. No admin rights required!

## Configuration

VM configurations and the path to QEMU are stored in `config.json`, which is automatically generated upon first run.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)
