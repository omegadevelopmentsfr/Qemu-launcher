import customtkinter as ctk
from tkinter import filedialog
import vm_manager

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class VMEditor(ctk.CTkToplevel):
    def __init__(self, parent, vm_data=None):
        super().__init__(parent)
        self.title("Edit VM" if vm_data else "Add New VM")
        self.geometry("400x500")
        
        self.vm_data = vm_data or {}
        self.result = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Name
        ctk.CTkLabel(self, text="VM Name:").pack(pady=(10, 0))
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(pady=(0, 10))
        if self.vm_data.get("name"): self.name_entry.insert(0, self.vm_data["name"])

        # RAM
        ctk.CTkLabel(self, text="RAM (MB):").pack(pady=(5, 0))
        self.ram_entry = ctk.CTkEntry(self)
        self.ram_entry.pack(pady=(0, 10))
        if self.vm_data.get("ram"): self.ram_entry.insert(0, self.vm_data["ram"])
        else: self.ram_entry.insert(0, "2048")

        # CPU
        ctk.CTkLabel(self, text="CPU Cores:").pack(pady=(5, 0))
        self.cpu_entry = ctk.CTkEntry(self)
        self.cpu_entry.pack(pady=(0, 10))
        if self.vm_data.get("cpu"): self.cpu_entry.insert(0, self.vm_data["cpu"])
        else: self.cpu_entry.insert(0, "2")
        
        # Disk Path
        ctk.CTkLabel(self, text="Disk Image Path (HDA):").pack(pady=(5, 0))
        self.disk_entry = ctk.CTkEntry(self)
        self.disk_entry.pack(pady=(0, 5))
        if self.vm_data.get("disk_path"): self.disk_entry.insert(0, self.vm_data["disk_path"])
        ctk.CTkButton(self, text="Browse Disk", command=self.browse_disk).pack(pady=(0, 10))

        # Disk Size
        ctk.CTkLabel(self, text="Disk Size (GB):").pack(pady=(5, 0))
        self.disk_size_entry = ctk.CTkEntry(self)
        self.disk_size_entry.pack(pady=(0, 10))
        if self.vm_data.get("disk_size"): self.disk_size_entry.insert(0, self.vm_data["disk_size"])
        else: self.disk_size_entry.insert(0, "20") # Default 20GB

        # ISO Path
        ctk.CTkLabel(self, text="ISO Path (CDROM):").pack(pady=(5, 0))
        self.iso_entry = ctk.CTkEntry(self)
        self.iso_entry.pack(pady=(0, 5))
        if self.vm_data.get("iso_path"): self.iso_entry.insert(0, self.vm_data["iso_path"])
        ctk.CTkButton(self, text="Browse ISO", command=self.browse_iso).pack(pady=(0, 10))
        
        # Save Button
        ctk.CTkButton(self, text="Save", command=self.save).pack(pady=20)

    def browse_disk(self):
        filename = filedialog.askopenfilename(title="Select Disk Image")
        if filename:
            self.disk_entry.delete(0, 'end')
            self.disk_entry.insert(0, filename)

    def browse_iso(self):
        filename = filedialog.askopenfilename(title="Select ISO Image", filetypes=[("ISO files", "*.iso"), ("All files", "*.*")])
        if filename:
            self.iso_entry.delete(0, 'end')
            self.iso_entry.insert(0, filename)

    def save(self):
        self.result = {
            "name": self.name_entry.get(),
            "ram": self.ram_entry.get(),
            "cpu": self.cpu_entry.get(),
            "disk_path": self.disk_entry.get(),
            "disk_size": self.disk_size_entry.get(),
            "iso_path": self.iso_entry.get()
        }
        self.destroy()


class QemuLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QEMU Portable Launcher")
        self.geometry("800x600")

        self.vm_manager = vm_manager.VMManager()

        self.create_layout()
        self.refresh_vm_list()
        self.check_vm_status()

    def check_vm_status(self):
        # Refresh list every second to update button states (e.g. if VM closed externally)
        # Note: A full refresh is expensive, maybe just update buttons?
        # For simplicity in this mvp, we full refresh or we could iterate buttons.
        # Let's just iterate buttons to be efficient.
        # However, we recreate buttons on refresh.
        
        # Actually, let's just trigger a lightweight update or just rely on manual clicks?
        # User requested "buttons", so they should update.
        self.refresh_vm_list()
        self.after(2000, self.check_vm_status)

    def create_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="QEMU Launcher", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        ctk.CTkButton(self.sidebar, text="Add new VM", command=self.add_vm).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Edit Selected", command=self.edit_vm).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Delete Selected", command=self.delete_vm, fg_color="red").pack(pady=10, padx=20)
        
        # Settings area in sidebar
        ctk.CTkLabel(self.sidebar, text="Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(40, 10))
        ctk.CTkLabel(self.sidebar, text="QEMU Path:").pack(padx=20, anchor="w")
        self.qemu_path_entry = ctk.CTkEntry(self.sidebar)
        self.qemu_path_entry.pack(padx=10, pady=5, fill="x")
        self.qemu_path_entry.insert(0, self.vm_manager.qemu_path or "")
        ctk.CTkButton(self.sidebar, text="Save Path", command=self.save_qemu_path).pack(pady=10)


        # Main Area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.main_frame, text="Your Virtual Machines", font=ctk.CTkFont(size=18)).pack(pady=10, anchor="w")
        
        # Scrollable Frame for VM List
        self.vm_list_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.vm_list_frame.pack(fill="both", expand=True)
        
        self.vm_buttons = []
        self.selected_vm_index = -1

    def refresh_vm_list(self):
        # Clear existing
        for widget in self.vm_list_frame.winfo_children():
            widget.destroy()
        
        self.vm_buttons = []
        
        for idx, vm in enumerate(self.vm_manager.vms):
            frame = ctk.CTkFrame(self.vm_list_frame)
            frame.pack(fill="x", pady=5)
            
            # Select button (invisible radio behavior, or just a button that sets selection)
            # Simplification: The whole row is a button
            btn = ctk.CTkButton(frame, text=f"{vm.get('name', 'Unnamed')} (RAM: {vm.get('ram')}MB)", 
                                command=lambda i=idx: self.select_vm(i),
                                anchor="w", fg_color="transparent", border_width=1)
            btn.pack(side="left", fill="x", expand=True, padx=5, pady=5)
            
            if self.vm_manager.is_vm_running(idx):
                 launch_btn = ctk.CTkButton(frame, text="Stop", width=80, fg_color="red", 
                                        command=lambda i=idx: self.stop_vm(i))
            else:
                 launch_btn = ctk.CTkButton(frame, text="Launch", width=80, fg_color="green", 
                                        command=lambda i=idx: self.launch_vm(i))
                                        
            launch_btn.pack(side="right", padx=10)
            
            self.vm_buttons.append(btn)

    def select_vm(self, index):
        self.selected_vm_index = index
        # Visual feedback
        for i, btn in enumerate(self.vm_buttons):
            if i == index:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    def add_vm(self):
        dialog = VMEditor(self)
        self.wait_window(dialog)
        if dialog.result:
            self.vm_manager.add_vm(dialog.result)
            self.refresh_vm_list()

    def edit_vm(self):
        if self.selected_vm_index == -1: return
        vm_data = self.vm_manager.vms[self.selected_vm_index]
        dialog = VMEditor(self, vm_data)
        self.wait_window(dialog)
        if dialog.result:
            self.vm_manager.update_vm(self.selected_vm_index, dialog.result)
            self.refresh_vm_list()

    def delete_vm(self):
        if self.selected_vm_index == -1: return
        self.vm_manager.delete_vm(self.selected_vm_index)
        self.selected_vm_index = -1
        self.refresh_vm_list()

    def launch_vm(self, index):
        error = self.vm_manager.launch_vm(index)
        if error:
            # If "VM is already running", maybe we just refresh
            if error == "VM is already running":
                self.refresh_vm_list()
                return

            error_window = ctk.CTkToplevel(self)
            error_window.title("Error")
            ctk.CTkLabel(error_window, text=error, text_color="red").pack(padx=20, pady=20)
        else:
            print(f"Launched VM at index {index}")
            self.refresh_vm_list()

    def stop_vm(self, index):
        if self.vm_manager.stop_vm(index):
            print(f"Stopped VM at index {index}")
            self.refresh_vm_list()
        else:
             print("Failed to stop or already stopped")
            
    def save_qemu_path(self):
        new_path = self.qemu_path_entry.get()
        self.vm_manager.qemu_path = new_path
        self.vm_manager.save_config() # This saves path too
        
if __name__ == "__main__":
    app = QemuLauncherApp()
    app.mainloop()
