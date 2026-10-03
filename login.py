import tkinter as tk
from tkinter import messagebox
import pymysql
import os
import sys
import subprocess
import tkinter.font as tkFont
import re
from db_config import DB_CONFIG
def login():
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    if not email or not password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Error", "Invalid email format.")
        return
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM user_info WHERE email_id=%s AND password=%s",
            (email, password)
        )
        result = cursor.fetchone()
        if result:
            root.destroy()
            flight_search(email)  
        else:
            messagebox.showerror("Failed", "Invalid email or password.")
            password_entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Database Error", f"{e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
def flight_search(user_email):
    script_path = os.path.join(os.path.dirname(__file__), "flight_search.py")
    subprocess.Popen([sys.executable, script_path, user_email])  # ✅ PASS EMAIL
def launch_register_page():
    root.destroy()
    reg_path = os.path.join(os.path.dirname(__file__), "registration.py")
    subprocess.Popen([sys.executable, reg_path])
root = tk.Tk()
root.title("SkyNest Login")
root.geometry("500x500")
root.configure(bg="#D0E6F5")
header = tk.Frame(
    root,
    bg="#D0E6F5"
)
header.pack(
    fill="x",
    padx=5,
    pady=(5, 5)
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
title_label = tk.Label(
    root,
    text="Welcome Back!",
    font=("Arial", 22, "bold"),
    bg="#D0E6F5"
)
title_label.pack(pady=(0, 10))
tk.Label(root, text="Email", bg="#D0E6F5").pack()
email_entry = tk.Entry(
    root, 
    width=40,
    font=("Arial",11)
    )
email_entry.pack(
    pady=5,
    ipady=4
    )
tk.Label(
    root, 
    text="Password", 
    bg="#D0E6F5"
    ).pack()
password_entry = tk.Entry(
    root, 
    width=40, 
    show="*",
    font=("Arial",11)
    )
password_entry.pack(
    pady=5,
    ipady=4
    )
login_button = tk.Button(
    root,
    text="Login",
    command=login,
    bg="#0D2E91",
    fg="white",
    activebackground="#09246F",
    activeforeground="white",
    font=("Arial", 13, "bold"),
    width=14,
    height=2,
    cursor="hand2",
    bd=0,
    relief="flat"
)
login_button.pack(pady=(18,22))
register_frame = tk.Frame(root, bg="#D0E6F5")
register_frame.pack()
prompt_label = tk.Label(
    register_frame,
    text="Don't have an account? ",
    bg="#D0E6F5"
)
prompt_label.pack(side="left")
default_font = tkFont.Font(font=prompt_label["font"])
underlined_font = default_font.copy()
underlined_font.configure(underline=True)
register_clickable = tk.Label(
    register_frame,
    text="Register Now",
    fg="blue",
    bg="#D0E6F5",
    cursor="hand2",
    font=underlined_font
)
register_clickable.pack(side="left")
register_clickable.bind("<Button-1>", lambda e: launch_register_page())
root.mainloop()