import tkinter as tk
from tkinter import messagebox
import pymysql
import os
import sys
import subprocess
import re
from db_config import DB_CONFIG
def register():
    full_name = full_name_var.get().strip()
    gender = gender_var.get().strip()
    email = email_var.get().strip()
    contact = contact_var.get().strip()
    city = city_var.get().strip()
    username = username_var.get().strip()
    password = password_var.get().strip()
    confirm_password = confirm_password_var.get().strip()
    if not full_name or not email or not contact or not password or not confirm_password:
        messagebox.showerror("Error", "All fields are required.")
        return
    if len(password) < 6:
        messagebox.showerror("Password Error", "Password must be at least 6 characters.")
        return
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Email Error", "Invalid email format")
        return
    if not re.fullmatch(r"\d{10}", contact):
        messagebox.showerror("Phone Error", "Phone number must be exactly 10 digits.")
        return
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_info WHERE username=%s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists.")
            return
        cursor.execute("SELECT * FROM user_info WHERE email_id=%s", (email,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Email already registered.")
            return
        query = "INSERT INTO user_info (name, gender, email_id, contact_no, city, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (full_name, gender, email, contact, city, username, password))
        connection.commit()
        messagebox.showinfo("Success", f"Thank you {full_name} for registering!!")
        root.destroy()
        flight_search()
    except Exception as e:
            print("FULL ERROR:", e)
            messagebox.showerror("Error", str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
def flight_search():
    script_path = os.path.join(os.path.dirname(__file__), "flight_search.py")
    subprocess.Popen([
        sys.executable,
        script_path,
        email_var.get().strip()
    ])
def launch_login_page():
    root.destroy()
    reg_path = os.path.join(os.path.dirname(__file__), "login.py")
    subprocess.Popen([sys.executable, reg_path])
root = tk.Tk()
root.configure(bg="#D0E6F5")
root.title("Skynest Registration")
root.geometry("600x700")
header = tk.Frame(
    root,
    bg="#D0E6F5"
)
header.pack(
    fill="x",
    padx=35,
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
header_font = ("Century Gothic", 24, "bold")
subtitle_font = ("Georgia", 14, "italic")
label_font = ("Roboto", 11)
entry_font = ("Roboto", 10)
entry_style = {
    "font": entry_font,
    "bg": "white",
    "relief": "flat",
    "bd": 1,
    "highlightthickness": 1,
    "highlightbackground": "#BBDEFB",
    "highlightcolor": "#2196F3",
}
button_style = {
    "bg": "#007BFF",
    "fg": "white",
    "activebackground": "#0056b3",
    "activeforeground": "white",
    "font": ("Roboto", 12, "bold"),
    "bd": 0,
    "relief": "flat",
    "cursor": "hand2",
    "pady": 10
}
title_frame = tk.Frame(root, bg="#D0E6F5")
title_frame.pack(pady=(5, 5))
tk.Label(title_frame, text="Create Your SkyNest Account", font=header_font, bg="#D0E6F5", fg="#0A3D62").pack(pady=15)
tk.Label(title_frame, text="Embark on your next adventure with us!", font=subtitle_font, bg="#D0E6F5", fg="#3B3B3B").pack()
main_form_frame = tk.Frame(root, bg="#D0E6F5", padx=20, pady=20)
main_form_frame.pack(pady=(8, 0), padx=50)
full_name_var = tk.StringVar()
gender_var = tk.StringVar(value="Male")
email_var = tk.StringVar()
contact_var = tk.StringVar()
city_var = tk.StringVar()
username_var = tk.StringVar()
password_var = tk.StringVar()
confirm_password_var = tk.StringVar()
tk.Label(main_form_frame, text="Full Name", font=label_font, bg="#D0E6F5").grid(row=0, column=0, padx=10, pady=8, sticky='w')
tk.Entry(main_form_frame, textvariable=full_name_var, **entry_style).grid(row=0, column=1, padx=10, pady=8, sticky='ew')
tk.Label(main_form_frame, text="Gender", font=label_font, bg="#D0E6F5").grid(row=1, column=0, padx=10, pady=8, sticky='w')
gender_frame = tk.Frame(main_form_frame, bg="#D0E6F5")
gender_frame.grid(row=1, column=1, sticky='w')
tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male", font=("Segoe UI", 10), bg="#D0E6F5", selectcolor="#ffffff").pack(side="left", padx=5)
tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female", font=("Segoe UI", 10), bg="#D0E6F5", selectcolor="#ffffff").pack(side="left", padx=5)
tk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other", font=("Segoe UI", 10), bg="#D0E6F5", selectcolor="#ffffff").pack(side="left", padx=5)
tk.Label(main_form_frame, text="Email", font=label_font, bg="#D0E6F5").grid(row=2, column=0, padx=10, pady=8, sticky='w')
tk.Entry(main_form_frame, textvariable=email_var, **entry_style).grid(row=2, column=1, padx=10, pady=8, sticky='ew')
tk.Label(main_form_frame, text="Contact", font=label_font, bg="#D0E6F5").grid(row=3, column=0, padx=10, pady=8, sticky='w')
tk.Entry(main_form_frame, textvariable=contact_var, **entry_style).grid(row=3, column=1, padx=10, pady=8, sticky='ew')
tk.Label(main_form_frame, text="City", font=label_font, bg="#D0E6F5").grid(row=4, column=0, padx=10, pady=8, sticky='w')
tk.Entry(main_form_frame, textvariable=city_var, **entry_style).grid(row=4, column=1, padx=10, pady=8, sticky='ew')
tk.Label(main_form_frame, text="Username", font=label_font, bg="#D0E6F5").grid(row=5, column=0, padx=10, pady=8, sticky='w')
tk.Entry(main_form_frame, textvariable=username_var, **entry_style).grid(row=5, column=1, padx=10, pady=8, sticky='ew')
tk.Label(main_form_frame, text="Password", font=label_font, bg="#D0E6F5").grid(row=6, column=0, padx=10, pady=8, sticky='w')
tk.Entry(main_form_frame, textvariable=password_var, show="*", **entry_style).grid(row=6, column=1, padx=10, pady=8, sticky='ew')
tk.Label(main_form_frame, text="Confirm Password", font=label_font, bg="#D0E6F5").grid(row=7, column=0, padx=10, pady=8, sticky='w')
tk.Entry(main_form_frame, textvariable=confirm_password_var, show="*", **entry_style).grid(row=7, column=1, padx=10, pady=8, sticky='ew')
register_btn = tk.Button(root, text="Register", command=register, **button_style)
register_btn.pack(pady=(15, 5), ipadx=30)
login_frame = tk.Frame(root, bg="#D0E6F5")
login_frame.pack(pady=(0, 20))
tk.Label(login_frame, text="Already have an account?", bg="#D0E6F5", font=("Roboto", 10)).pack(side="left")
login_label = tk.Label(login_frame, text=" Login", fg="blue", bg="#D0E6F5", font=("Roboto", 10, "underline"), cursor="hand2")
login_label.pack(side="left")
login_label.bind("<Button-1>", lambda e: launch_login_page())
root.mainloop()
