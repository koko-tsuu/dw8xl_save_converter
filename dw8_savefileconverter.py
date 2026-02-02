import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import main_functions


def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()



# ===================== GUI FUNCTIONS =====================

def browse_input():
    path = filedialog.askopenfilename(title="Select Input File")
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)


def browse_output():
    path = filedialog.asksaveasfilename(title="Select Output Directory")
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)


    

def convert():
    input_path = input_entry.get()
    output_path = output_entry.get()
    in_type = input_type.get()
    out_type = output_type.get()

    if not input_path or not output_path:
        messagebox.showerror("Error", "Please select both input and output files.")
        return
    
    
    if not in_type or not out_type:
        messagebox.showerror("Error", "Please select both input and output types.")
        return
    
    if in_type is out_type:
        messagebox.showerror("Error", "Input and output types are the same.")
        return
    
    
    def task():
        try:
            main_functions.convert(input_path, output_path, in_type, out_type)
            
            messagebox.showinfo("Success", "Operation completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    

    threading.Thread(target=task, daemon=True).start()




# ===================== DRAG & DROP =====================

def drop_input(event):
    path = event.data.strip("{}")
    input_entry.delete(0, tk.END)
    input_entry.insert(0, path)


def drop_output(event):
    path = event.data.strip("{}")
    output_entry.delete(0, tk.END)
    output_entry.insert(0, path)


# ===================== MAIN WINDOW =====================


PADX_LEFT_SIZE = (30, 0)
row = 0
root = TkinterDnD.Tk()
root.title("Dynasty Warriors 8 XL Save File Converter")
root.geometry("600x300")
root.resizable(False, False)
center(root)
root.iconbitmap("favicon.ico")
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)


# ---- Input File ----
tk.Label(root, text="Input:").grid(row=0, column=0, padx=PADX_LEFT_SIZE, pady=(30, 10), sticky="w")

input_entry = tk.Entry(root, width=75)
input_entry.grid(row=0, column=0, pady=(20, 0), padx=(100, 0), sticky="w")
input_entry.drop_target_register(DND_FILES)
input_entry.dnd_bind("<<Drop>>", drop_input)

tk.Button(root, width=18, text="Browse", command=browse_input).grid(row=0, column=1, padx=(5, 30), pady=(30, 10))

# ---- Output File ----
tk.Label(root, text="Output:").grid(row=1, column=0, padx=PADX_LEFT_SIZE, pady=10, sticky="w")

output_entry = tk.Entry(root, width=75)
output_entry.grid(row=1, column=0,  pady=(0, 0), padx=(100, 0), sticky="w")
output_entry.drop_target_register(DND_FILES)
output_entry.dnd_bind("<<Drop>>", drop_output)

tk.Button(root,  width=18, text="Browse", command=browse_output).grid(row=1, column=1, padx=(5, 30))

# ---- Input Type Dropdown ----
tk.Label(root, text="Input Type:").grid(row=2, column=0, padx=(50, 50), pady=(30, 10), sticky="w")

input_type = ttk.Combobox(root, values=["", "PC", "PS3", "PS4", "PSV"], state="readonly")
input_type.current(0)
input_type.grid(row=3, column=0, padx=(90, 0), pady=(2, 10), sticky="w")

# ---- Output Type Dropdown ----
tk.Label(root, text="Output Type:").grid(row=2, column=0, padx=(300, 50), pady=(30, 10), sticky="w")

output_type = ttk.Combobox(root, values=["", "PC", "PS3", "PS4", "PSV"], state="readonly")
output_type.current(0)
output_type.grid(row=3, column=0, padx=(370, 0), pady=(2, 10), sticky="w")

# ---- Buttons ----
tk.Button(root, width= 70, text="Convert", command=convert).grid(row=4, column=0, padx=(90, 0),pady=(40, 20))
root.mainloop()
