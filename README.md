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

- Python 3.10 or higher.
- **Linux**: Ensure QEMU system and GUI packages are installed:
  ```bash
  sudo apt update
  sudo apt install qemu-system-x86 qemu-system-gui
  ```

### Setting up the Environment

It is recommended to use a virtual environment or install dependencies directly (if preferred).

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/portable-qemu-launcher.git
   cd portable-qemu-launcher
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note for Linux users: If you encounter an "externally-managed-environment" error, use `pip install -r requirements.txt --break-system-packages` or set up a venv.*

## Usage

Run the application:
```bash
python main.py
```

### Windows Portable Mode (No Admin Rights)
To carry this app on a USB stick or use it without administrator privileges:

1. Download the [QEMU for Windows installer](https://qemu.weilnetz.de/w64/).
2. Run the installer. When asked for the installation path, browse and select a folder named `qemu` **inside** this project's directory.
   - Example: `X:\portable-qemu-launcher\qemu\`
3. **Crucial**: Ensure you install to this local folder, NOT "Program Files". This avoids needing admin permissions.
4. The launcher will automatically detect `qemu-system-x86_64.exe` in that folder.

## Configuration

VM configurations and the path to QEMU are stored in `config.json`, which is automatically generated upon first run.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)
