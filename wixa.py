import tkinter as tk
from tkinter import ttk
# Just simply import the azure.tcl file



# Zaimportuj plik azure.tcl
root.tk_call("Azure-ttk-theme-main/azure.tcl", "azure.tcl")

# Ustaw motyw na jasny (light) lub ciemny (dark)
root.tk_call("set_theme", "light")

def open_popup():
    popup = tk.Toplevel(root)
    popup.title("Popup Window")
    label = tk.Label(popup, text="This is a popup window!")
    label.pack(pady=20)
    close_button = ttk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack()

def change_font_size():
    current_size = style.lookup('TButton', 'font')[1]
    new_size = current_size + 2
    style.configure('TButton', font=('Arial', new_size))

def custom_command():
    result_label.config(text="Custom Command Executed")

root = tk.Tk()
root.title("Tkinter App")
root.geometry("400x300")

style = ttk.Style()

# Style configuration
style.configure('TButton', background='#3498db', foreground='white', padding=(10, 5), borderwidth=4, relief="raised", font=('Arial', 12))
style.map('TButton', background=[('active', '#1f618d')])  # Change color on hover

frame = ttk.Frame(root)
frame.pack(pady=20, side=tk.BOTTOM)

button1 = ttk.Button(frame, text="Regular Button")
button1.pack(side=tk.LEFT, padx=10)

button2 = ttk.Button(frame, text="Popup Button", command=open_popup)
button2.pack(side=tk.LEFT, padx=10)

button3 = ttk.Button(frame, text="Font Size +", command=change_font_size)
button3.pack(side=tk.LEFT, padx=10)

button4 = ttk.Button(frame, text="Disabled Button", state="disabled")
button4.pack(side=tk.LEFT, padx=10)

button5 = ttk.Button(frame, text="Custom Color", style='TButton.TButton')
style.configure('TButton.TButton', background='#27ae60')
button5.pack(side=tk.LEFT, padx=10)

button6 = ttk.Button(frame, text="Custom Command", command=custom_command)
button6.pack(side=tk.LEFT, padx=10)

result_label = tk.Label(root, text="")
result_label.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
