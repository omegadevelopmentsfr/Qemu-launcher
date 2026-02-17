import json
import os
import subprocess
import platform
import shutil

CONFIG_FILE = "config.json"

class VMManager:
    def __init__(self):
        self.vms = []
        self.qemu_path = None
        self.qemu_img_path = None
        self.load_config()
        
        if not self.qemu_path:
            self.qemu_path = self.get_initial_qemu_path()
            
        if not self.qemu_img_path:
            self.qemu_img_path = self.get_qemu_img_path()
            
        self.running_processes = {} # Dictionary to map VM index (or ID) to Popen object

    def get_initial_qemu_path(self):
        """
        Detects QEMU path.
        Priority:
        1. config.json 'qemu_path' setting (already loaded if sensitive, otherwise detect)
        2. Local 'qemu' folder (portable mode)
        3. System PATH
        """
        system = platform.system()
        
        # Portable check (Windows mostly, but Linux too if folder exists)
        local_qemu = os.path.join(os.getcwd(), "qemu")
        if os.path.exists(local_qemu):
            if system == "Windows":
                 exe = os.path.join(local_qemu, "qemu-system-x86_64w.exe")
                 if os.path.exists(exe): return exe
            else:
                 exe = os.path.join(local_qemu, "qemu-system-x86_64")
                 if os.path.exists(exe): return exe

        # System check
        if system == "Windows":
             path = shutil.which("qemu-system-x86_64w.exe")
        else:
             path = shutil.which("qemu-system-x86_64")
             
        return path if path else ""

    def get_qemu_img_path(self):
        system = platform.system()
        local_qemu = os.path.join(os.getcwd(), "qemu")
        
        if os.path.exists(local_qemu):
             if system == "Windows":
                 exe = os.path.join(local_qemu, "qemu-img.exe")
                 if os.path.exists(exe): return exe
             else:
                 exe = os.path.join(local_qemu, "qemu-img")
                 if os.path.exists(exe): return exe
        
        if system == "Windows":
            path = shutil.which("qemu-img.exe")
        else:
            path = shutil.which("qemu-img")
            
        return path if path else ""

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.vms = data.get("vms", [])
                    self.qemu_path = data.get("qemu_path", "")
                    self.qemu_img_path = data.get("qemu_img_path", "")
            except Exception as e:
                print(f"Error loading config: {e}")
                self.vms = []
        else:
            self.vms = []

    def save_config(self):
        data = {
            "vms": self.vms,
            "qemu_path": self.qemu_path,
            "qemu_img_path": self.qemu_img_path
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def create_disk(self, disk_path, size_gb):
        if not self.qemu_img_path:
            print("qemu-img not found, cannot create disk.")
            return False
            
        if os.path.exists(disk_path):
            print(f"Disk {disk_path} already exists.")
            return True # Already exists

        try:
            cmd = [self.qemu_img_path, "create", "-f", "qcow2", disk_path, f"{size_gb}G"]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating disk: {e}")
            return False

    def resize_disk(self, disk_path, size_gb):
        if not self.qemu_img_path:
            print("qemu-img not found, cannot resize disk.")
            return False
            
        if not os.path.exists(disk_path):
             print(f"Disk {disk_path} does not exist.")
             return False

        try:
            # Resize command
            cmd = [self.qemu_img_path, "resize", disk_path, f"{size_gb}G"]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error resizing disk: {e}")
            return False

    def add_vm(self, vm_data):
        # Create disk if path and size defined
        if vm_data.get("disk_path") and vm_data.get("disk_size"):
             if not self.create_disk(vm_data["disk_path"], vm_data["disk_size"]):
                 return False, "Failed to create disk image. Check console/logs and qemu-img path."
        
        self.vms.append(vm_data)
        self.save_config()
        return True, None

    def update_vm(self, index, vm_data):
        if 0 <= index < len(self.vms):
            old_vm = self.vms[index]
            
            # Check for disk resize
            if vm_data.get("disk_path") == old_vm.get("disk_path"):
                if vm_data.get("disk_size") and vm_data["disk_size"] != old_vm.get("disk_size"):
                     self.resize_disk(vm_data["disk_path"], vm_data["disk_size"])
            elif vm_data.get("disk_path") and vm_data.get("disk_size"):
                 # New path, try creating if doesn't exist?
                 # If user changed path, we assume they might want a new disk or pointing to existing
                 if not os.path.exists(vm_data["disk_path"]):
                      self.create_disk(vm_data["disk_path"], vm_data["disk_size"])

            self.vms[index] = vm_data
            self.save_config()

    def delete_vm(self, index):
        if 0 <= index < len(self.vms):
            del self.vms[index]
            self.save_config()

    def get_launch_command(self, vm_data):
        if not self.qemu_path:
            return None, "QEMU path not configured or found."

        cmd = [self.qemu_path]
        
        # Basic constraints
        if vm_data.get("ram"):
            cmd.extend(["-m", vm_data["ram"]])
        
        if vm_data.get("cpu"):
            cmd.extend(["-smp", vm_data["cpu"]])
            
        # Disk image (HDA)
        if vm_data.get("disk_path"):
            cmd.extend(["-hda", vm_data["disk_path"]])
            
        # ISO image (CDROM) or Floppy disks based on install_mode
        install_mode = vm_data.get("install_mode", "iso")
        
        if install_mode == "floppy":
            # Floppy disk mode
            if vm_data.get("floppy_a_path"):
                cmd.extend(["-fda", vm_data["floppy_a_path"]])
            if vm_data.get("floppy_b_path"):
                cmd.extend(["-fdb", vm_data["floppy_b_path"]])
        else:
            # ISO mode (default, backward compatible)
            if vm_data.get("iso_path"):
                cmd.extend(["-cdrom", vm_data["iso_path"]])
            
        # Boot order
        if vm_data.get("boot_order"):
             cmd.extend(["-boot", vm_data["boot_order"]]) # e.g., 'd' for cdrom
        
        # Acceleration (KVM on Linux, HAX/WHPrat on Windows if available, but let's stick to basic or user defined)
        if vm_data.get("accel"):
            cmd.extend(["-accel", vm_data["accel"]])
        elif platform.system() == "Linux":
            cmd.extend(["-enable-kvm"]) # Default to KVM on Linux if possible

        # Display (Standard VGA is usually safe)
        cmd.extend(["-vga", "std"])
        if platform.system() == "Linux":
            # Force GTK on Linux to avoid VNC default fallback if GUI packet is missing (better to error out than hang)
            cmd.extend(["-display", "gtk"])
        else:
            # On Windows, default usually picks the available GUI (SDL/GTK) correctly
            cmd.extend(["-display", "default"])
        
        return cmd, None

    def launch_vm_from_data(self, vm_data):
        cmd, error = self.get_launch_command(vm_data)
        
        if error:
            return error, None

        try:
            # Popen allows running in background
            process = subprocess.Popen(cmd)
            return None, process # Success, return process handle
        except Exception as e:
            return f"Failed to launch QEMU: {e}", None

    def launch_vm(self, index):
        if not (0 <= index < len(self.vms)):
            return "Invalid VM index"

        if index in self.running_processes:
            if self.running_processes[index].poll() is None:
                return "VM is already running"
            else:
                del self.running_processes[index] # Cleanup finished process

        vm_data = self.vms[index]
        error, process = self.launch_vm_from_data(vm_data)
        
        if not error and process:
            self.running_processes[index] = process
            return None
        return error

    def stop_vm(self, index):
        if index in self.running_processes:
            proc = self.running_processes[index]
            if proc.poll() is None:
                proc.terminate() # Try graceful termination
                # You might want to wait or force kill if it doesn't stop, but terminate is usually enough for QEMU window close
                return True
            else:
                del self.running_processes[index]
        return False

    def is_vm_running(self, index):
        if index in self.running_processes:
            if self.running_processes[index].poll() is None:
                return True
            else:
                del self.running_processes[index] # Cleanup dead
        return False
