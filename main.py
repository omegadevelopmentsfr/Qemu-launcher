import customtkinter as ctk
from tkinter import filedialog
import vm_manager

print("Don't close this terminal, it is used by the application and QEMU")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class VMEditor(ctk.CTkToplevel):
    def __init__(self, parent, vm_data=None):
        super().__init__(parent)
        self.title("Edit VM" if vm_data else "Add New VM")
        self.geometry("400x620")
        
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
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Create New", width=100, command=self.browse_disk_new).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Select Existing", width=100, command=self.browse_disk_existing).pack(side="left", padx=5)

        # Disk Size
        ctk.CTkLabel(self, text="Disk Size (GB) - for creation:").pack(pady=(5, 0))
        self.disk_size_entry = ctk.CTkEntry(self)
        self.disk_size_entry.pack(pady=(0, 10))
        if self.vm_data.get("disk_size"): 
            self.disk_size_entry.insert(0, self.vm_data["disk_size"])
        else: 
            self.disk_size_entry.insert(0, "20") # Default 20GB

        # --- Install Mode Selector ---
        ctk.CTkLabel(self, text="Installation Media:").pack(pady=(10, 0))
        
        current_mode = self.vm_data.get("install_mode", "iso")
        self.install_mode_var = ctk.StringVar(value="ISO (CD-ROM)" if current_mode == "iso" else "Disquettes (A: / B:)")
        
        self.mode_selector = ctk.CTkSegmentedButton(
            self,
            values=["ISO (CD-ROM)", "Disquettes (A: / B:)"],
            variable=self.install_mode_var,
            command=self.on_mode_change
        )
        self.mode_selector.pack(pady=(5, 10), padx=20, fill="x")

        # --- ISO Frame ---
        self.iso_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        ctk.CTkLabel(self.iso_frame, text="ISO Path (CDROM):").pack(pady=(5, 0))
        self.iso_entry = ctk.CTkEntry(self.iso_frame)
        self.iso_entry.pack(pady=(0, 5), padx=10, fill="x")
        if self.vm_data.get("iso_path"): self.iso_entry.insert(0, self.vm_data["iso_path"])
        ctk.CTkButton(self.iso_frame, text="Browse ISO", command=self.browse_iso).pack(pady=(0, 5))

        # --- Floppy Frame ---
        self.floppy_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        ctk.CTkLabel(self.floppy_frame, text="Floppy A: (.img):").pack(pady=(5, 0))
        self.floppy_a_entry = ctk.CTkEntry(self.floppy_frame)
        self.floppy_a_entry.pack(pady=(0, 5), padx=10, fill="x")
        if self.vm_data.get("floppy_a_path"): self.floppy_a_entry.insert(0, self.vm_data["floppy_a_path"])
        ctk.CTkButton(self.floppy_frame, text="Browse Floppy A:", command=self.browse_floppy_a).pack(pady=(0, 5))
        
        ctk.CTkLabel(self.floppy_frame, text="Floppy B: (.img):").pack(pady=(5, 0))
        self.floppy_b_entry = ctk.CTkEntry(self.floppy_frame)
        self.floppy_b_entry.pack(pady=(0, 5), padx=10, fill="x")
        if self.vm_data.get("floppy_b_path"): self.floppy_b_entry.insert(0, self.vm_data["floppy_b_path"])
        ctk.CTkButton(self.floppy_frame, text="Browse Floppy B:", command=self.browse_floppy_b).pack(pady=(0, 5))

        # Show the correct frame based on current mode
        self.on_mode_change(self.install_mode_var.get())
        
        # Save Button
        ctk.CTkButton(self, text="Save", command=self.save).pack(pady=20)

    def on_mode_change(self, selected):
        if selected == "ISO (CD-ROM)":
            self.floppy_frame.pack_forget()
            self.iso_frame.pack(pady=(0, 5), fill="x")
        else:
            self.iso_frame.pack_forget()
            self.floppy_frame.pack(pady=(0, 5), fill="x")

    def browse_disk_new(self):
        filename = filedialog.asksaveasfilename(
            title="Create New Disk Image",
            defaultextension=".qcow2",
            filetypes=[("QCOW2 Image", "*.qcow2"), ("All files", "*.*")]
        )
        if filename:
            self.disk_entry.delete(0, 'end')
            self.disk_entry.insert(0, filename)
            self.disk_size_entry.configure(state="normal")

    def browse_disk_existing(self):
        filename = filedialog.askopenfilename(
            title="Select Existing Disk Image",
            filetypes=[("QCOW2 Image", "*.qcow2"), ("All files", "*.*")]
        )
        if filename:
            self.disk_entry.delete(0, 'end')
            self.disk_entry.insert(0, filename)
            self.disk_size_entry.delete(0, 'end')
            self.disk_size_entry.configure(placeholder_text="N/A")

    def browse_iso(self):
        filename = filedialog.askopenfilename(title="Select ISO Image", filetypes=[("ISO files", "*.iso"), ("All files", "*.*")])
        if filename:
            self.iso_entry.delete(0, 'end')
            self.iso_entry.insert(0, filename)

    def browse_floppy_a(self):
        filename = filedialog.askopenfilename(title="Select Floppy A: Image", filetypes=[("IMG files", "*.img"), ("All files", "*.*")])
        if filename:
            self.floppy_a_entry.delete(0, 'end')
            self.floppy_a_entry.insert(0, filename)

    def browse_floppy_b(self):
        filename = filedialog.askopenfilename(title="Select Floppy B: Image", filetypes=[("IMG files", "*.img"), ("All files", "*.*")])
        if filename:
            self.floppy_b_entry.delete(0, 'end')
            self.floppy_b_entry.insert(0, filename)

    def save(self):
        install_mode = "iso" if self.install_mode_var.get() == "ISO (CD-ROM)" else "floppy"
        self.result = {
            "name": self.name_entry.get(),
            "ram": self.ram_entry.get(),
            "cpu": self.cpu_entry.get(),
            "disk_path": self.disk_entry.get(),
            "disk_size": self.disk_size_entry.get(),
            "install_mode": install_mode,
            "iso_path": self.iso_entry.get(),
            "floppy_a_path": self.floppy_a_entry.get(),
            "floppy_b_path": self.floppy_b_entry.get()
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
        # Update only button states every 2 seconds to prevent flickering
        self.update_vm_status_buttons()
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
        
        # QEMU System Path
        ctk.CTkLabel(self.sidebar, text="QEMU Path:").pack(padx=20, anchor="w")
        self.qemu_path_entry = ctk.CTkEntry(self.sidebar)
        self.qemu_path_entry.pack(padx=10, pady=5, fill="x")
        self.qemu_path_entry.insert(0, self.vm_manager.qemu_path or "")
        
        # QEMU Img Path
        ctk.CTkLabel(self.sidebar, text="QEMU Img Path:").pack(padx=20, anchor="w")
        self.qemu_img_path_entry = ctk.CTkEntry(self.sidebar)
        self.qemu_img_path_entry.pack(padx=10, pady=5, fill="x")
        self.qemu_img_path_entry.insert(0, self.vm_manager.qemu_img_path or "")
        
        ctk.CTkButton(self.sidebar, text="Save Paths", command=self.save_qemu_path).pack(pady=10)


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
        self.status_buttons = [] # Store references to launch/stop buttons
        
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
            self.status_buttons.append(launch_btn)

    def update_vm_status_buttons(self):
        """Update only the status buttons without recreating the whole list to avoid flickering."""
        if not hasattr(self, "status_buttons"): return
        
        for idx, btn in enumerate(self.status_buttons):
            is_running = self.vm_manager.is_vm_running(idx)
            current_text = btn.cget("text")
            
            if is_running and current_text == "Launch":
                # Changed from stopped to running
                btn.configure(text="Stop", fg_color="red", command=lambda i=idx: self.stop_vm(i))
            elif not is_running and current_text == "Stop":
                # Changed from running to stopped
                btn.configure(text="Launch", fg_color="green", command=lambda i=idx: self.launch_vm(i))

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
            success, error = self.vm_manager.add_vm(dialog.result)
            if success:
                self.refresh_vm_list()
            else:
                 error_window = ctk.CTkToplevel(self)
                 error_window.title("Error Creating VM")
                 ctk.CTkLabel(error_window, text=error or "Unknown error", text_color="red").pack(padx=20, pady=20)

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
        new_img_path = self.qemu_img_path_entry.get()
        self.vm_manager.qemu_path = new_path
        self.vm_manager.qemu_img_path = new_img_path
        self.vm_manager.save_config() # This saves paths too
        
if __name__ == "__main__":
    app = QemuLauncherApp()
    app.mainloop()
