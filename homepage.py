import tkinter as tk
import os
import sys
import subprocess
def open_login():
    root.destroy()
    script_path = os.path.join(os.path.dirname(__file__), "login.py")
    subprocess.Popen([sys.executable, script_path])
def open_register():
    root.destroy()
    script_path = os.path.join(os.path.dirname(__file__), "registration.py")
    subprocess.Popen([sys.executable, script_path])
def open_about():
    root.destroy()
    script_path = os.path.join(os.path.dirname(__file__), "about_us.py")
    subprocess.Popen([sys.executable, script_path])
def open_contact():
    root.destroy()
    script_path = os.path.join(os.path.dirname(__file__), "contact_us.py")
    subprocess.Popen([sys.executable, script_path])
root = tk.Tk()
root.title("SkyNest Homepage")
root.geometry("600x550")
root.configure(bg="#D0E6F5")
header = tk.Frame(
    root,
    bg="#D0E6F5"
)
header.pack(
    fill="x",
    padx=0,
    pady=(10, 0)
)
logo_path = os.path.join(
    os.path.dirname(__file__),
    "skynest_logo.png"
)
try:
    logo_image = tk.PhotoImage(file=logo_path)
    logo_image = logo_image.subsample(12, 12)
    logo_label = tk.Label(
        header,
        image=logo_image,
        bg="#D0E6F5"
    )
    logo_label.pack(side="left")
except Exception as e:
    print("Could not load SkyNest logo:", e)
tk.Label(
    root,
    text="Welcome to SkyNest",
    font=("Helvetica", 22, "bold"),
    bg="#D0E6F5",
    fg="#0A3D62"
    ).pack(pady=(5, 20))  
btn_frame = tk.Frame(
    root, 
    bg="#D0E6F5"
    )
btn_frame.pack(pady=10)
button_style = {
    "font":("Arial",13,"bold"),
    "bg":"#0D2E91",
    "fg":"white",
    "activebackground":"#09246F",
    "activeforeground":"white",
    "width":20,
    "height":2,
    "bd":0,
    "relief":"flat",
    "cursor":"hand2"
}
tk.Button(
    btn_frame,
    text="Login",
    command=open_login,
    **button_style
).pack(pady=7)
tk.Button(
    btn_frame,
    text="Register",
    command=open_register,
    **button_style
).pack(pady=7)
tk.Button(
    btn_frame,
    text="About Us",
    command=open_about,
    **button_style
).pack(pady=7)
tk.Button(
    btn_frame,
    text="Contact Us",
    command=open_contact,
    **button_style
).pack(pady=7)
root.mainloop()