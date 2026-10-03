import tkinter as tk
import os
import sys
import subprocess
root = tk.Tk()
root.title("Contact Us - SkyNest")
root.geometry("850x650")
root.configure(bg="#D0E6F5")
header = tk.Frame(
    root,
    bg="#D0E6F5"
)
header.pack(
    fill="x",
    padx=25,
    pady=(10, 0)
)
logo_path = os.path.join(
    os.path.dirname(__file__),
    "skynest_logo.png"
)
try:
    logo_image = tk.PhotoImage(
        file=logo_path
    )
    logo_image = logo_image.subsample(
        15,
        15
    )
    logo_label = tk.Label(
        header,
        image=logo_image,
        bg="#D0E6F5"
    )
    logo_label.pack(
        side="left"
    )
except Exception as e:
    print(
        "Could not load SkyNest logo:",e
    )
content_frame = tk.Frame(
    root,
    bg="#D0E6F5"
)
content_frame.pack(
    fill="both",
    expand=True,
    padx=60,
    pady=(10,20)
)
tk.Label(
    content_frame,
    text="Contact Us",
    font=("Georgia", 30, "bold", "italic"),
    bg="#D0E6F5",
    fg="#2F4F4F",
    anchor="w"
).pack(
    fill="x",
    padx=30,
    pady=(20, 10)
)
intro_text = (
    "Have questions, feedback, or need help with your booking? "
    "Our SkyNest support team is here to help you."
)
tk.Message(
    content_frame,
    text=intro_text,
    font=("Arial", 13),
    bg="#D0E6F5",
    fg="#444444",
    justify="left",
    width=600
).pack(
    padx=30,
    pady=15,
    anchor="w"
)
tk.Label(
    content_frame,
    text="Get in Touch",
    font=("Arial", 17, "bold"),
    bg="#D0E6F5",
    fg="#0D2E91",
    anchor="w"
).pack(
    fill="x",
    padx=30,
    pady=(15, 10)
)
contact_text = (
    "Email: support@skynest.com\n\n"
    "Phone: +91 98765 43210\n\n"
    "Address: Mumbai, Maharashtra, India\n\n"
    "Working Hours: Monday - Saturday, 9:00 AM - 6:00 PM"
)
tk.Message(
    content_frame,
    text=contact_text,
    font=("Arial", 13),
    bg="#D0E6F5",
    fg="#444444",
    justify="left",
    width=600
).pack(
    fill="x",
    padx=30,
    pady=10
)
def go_back():
    root.destroy()
    path = os.path.join(
        os.path.dirname(__file__),
        "homepage.py"
    )
    subprocess.Popen([
        sys.executable,
        path
    ])
tk.Button(
    content_frame,
    text="Back to Homepage",
    font=("Arial", 13, "bold"),
    bg="#0D2E91",
    fg="white",
    activebackground="#09246F",
    activeforeground="white",
    padx=20,
    pady=10,
    bd=0,
    relief="flat",
    cursor="hand2",
    command=go_back
).pack(
    pady=25
)
root.mainloop()