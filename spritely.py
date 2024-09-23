import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import json
import math

def create_sprite_sheet(folder_path, output_name, frame_size, frame_step):
    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    png_files.sort()
    
    # Apply frame step (skip frames)
    png_files = png_files[::frame_step]

    if not png_files:
        print(f"No PNG files found in {folder_path}")
        return None, None

    num_images = len(png_files)
    grid_size = math.ceil(math.sqrt(num_images))
    
    sheet_size = frame_size * grid_size

    sprite_sheet = Image.new('RGBA', (sheet_size, sheet_size))
    json_data = {"frames": []}

    for i, file in enumerate(png_files):
        with Image.open(os.path.join(folder_path, file)) as img:
            # Resize the image if necessary
            if img.size != (frame_size, frame_size):
                img = img.resize((frame_size, frame_size), Image.LANCZOS)
            
            row = i // grid_size
            col = i % grid_size
            x = col * frame_size
            y = row * frame_size
            sprite_sheet.paste(img, (x, y))
            json_data["frames"].append({
                "position": {"x": x, "y": y, "w": frame_size, "h": frame_size}
            })

    return sprite_sheet, json_data

class SpriteSheetCreatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sprite Sheet Creator")
        master.geometry("600x450")  # Slightly increased height for new button

        self.input_folders = []
        self.output_folder = tk.StringVar()
        self.frame_size = tk.IntVar(value=64)
        self.frame_step = tk.IntVar(value=1)
        self.custom_name = tk.StringVar()

        # Input folders list
        tk.Label(master, text="Input Folders:").grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.folder_listbox = tk.Listbox(master, width=70, height=5)
        self.folder_listbox.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        scrollbar = tk.Scrollbar(master, orient="vertical")
        scrollbar.config(command=self.folder_listbox.yview)
        scrollbar.grid(row=0, column=3, sticky="ns")
        self.folder_listbox.config(yscrollcommand=scrollbar.set)
        
        tk.Button(master, text="Add Folder", command=self.add_input_folder).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        tk.Button(master, text="Remove Folder", command=self.remove_input_folder).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        tk.Button(master, text="Select Parent Folder", command=self.select_parent_folder).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Output folder selection
        tk.Label(master, text="Output Folder:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.output_folder, width=70).grid(row=3, column=1, padx=5, pady=5, columnspan=2)
        tk.Button(master, text="Browse", command=self.browse_output).grid(row=3, column=3, padx=5, pady=5)

        # Frame size
        tk.Label(master, text="Frame Size:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.frame_size, width=10).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Frame step (skip frames)
        tk.Label(master, text="Frame Step:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.frame_step, width=10).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Custom name for output files
        tk.Label(master, text="Custom Name:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(master, textvariable=self.custom_name, width=70).grid(row=6, column=1, padx=5, pady=5, columnspan=2)

        # Process button
        tk.Button(master, text="Create Sprite Sheets", command=self.process).grid(row=7, column=1, pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(master, length=500, mode='determinate')
        self.progress.grid(row=8, column=0, columnspan=4, padx=5, pady=5)

    def add_input_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.input_folders:
            self.input_folders.append(folder)
            self.folder_listbox.insert(tk.END, folder)

    def remove_input_folder(self):
        selection = self.folder_listbox.curselection()
        if selection:
            index = selection[0]
            self.folder_listbox.delete(index)
            del self.input_folders[index]

    def select_parent_folder(self):
        parent_folder = filedialog.askdirectory()
        if parent_folder:
            subfolders = [f.path for f in os.scandir(parent_folder) if f.is_dir()]
            for folder in subfolders:
                if folder not in self.input_folders:
                    self.input_folders.append(folder)
                    self.folder_listbox.insert(tk.END, folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def process(self):
        if not self.input_folders:
            messagebox.showerror("Error", "Please add at least one input folder.")
            return

        output_folder = self.output_folder.get()
        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        frame_size = self.frame_size.get()
        frame_step = self.frame_step.get()
        custom_name = self.custom_name.get()

        if frame_size < 1:
            messagebox.showerror("Error", "Frame size must be at least 1 pixel.")
            return

        if frame_step < 1:
            messagebox.showerror("Error", "Frame step must be 1 or greater.")
            return

        self.progress['value'] = 0
        self.master.update_idletasks()

        os.makedirs(output_folder, exist_ok=True)

        total_folders = len(self.input_folders)
        for i, folder in enumerate(self.input_folders):
            folder_name = os.path.basename(folder)
            output_name = custom_name if custom_name else folder_name
            
            if custom_name and total_folders > 1:
                output_name = f"{custom_name}_{i+1}"

            sprite_sheet, json_data = create_sprite_sheet(folder, output_name, frame_size, frame_step)
            if sprite_sheet and json_data:
                sprite_sheet.save(os.path.join(output_folder, f"{output_name}_sprite_sheet.png"))
                with open(os.path.join(output_folder, f"{output_name}_sprite_sheet.json"), 'w') as json_file:
                    json.dump(json_data, json_file, indent=2)
                print(f"Sprite sheet and JSON saved as {output_name}")
            
            self.progress['value'] = (i + 1) / total_folders * 100
            self.master.update_idletasks()

        messagebox.showinfo("Complete", "Sprite sheets and JSON files have been created.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = SpriteSheetCreatorGUI(root)
    root.mainloop()