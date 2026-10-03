import tkinter as tk
import os
import sys
import subprocess
def go_back():
    root.destroy()
    script_path = os.path.join(
        os.path.dirname(__file__),
        "homepage.py"
    )
    subprocess.Popen([
        sys.executable,
        script_path
    ])
root = tk.Tk()
root.title("SkyNest - About Us")
root.geometry("900x650")
root.configure(bg="#D0E6F5")
root.resizable(False, False)
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
tk.Label(
    root,
    text="About Us",
    font=("Georgia", 30, "bold", "italic"),
    bg="#D0E6F5",
    fg="#2F4F4F"
).pack(
    pady=(5, 20)
)
content_frame = tk.Frame(
    root,
    bg="#D0E6F5",
    padx=25,
    pady=30
)
content_frame.pack(
    padx=60,
    fill="both",
    expand=True
)
tk.Label(
    content_frame,
    text="Welcome to SkyNest",
    font=("Arial", 20, "bold"),
    bg="#D0E6F5",
    fg="#0D2E91",
    anchor="w"
).pack(
    fill="x",
    padx=20,
    pady=(0, 20)
)
about_text = (
    "SkyNest is a flight booking application designed to make "
    "planning and managing air travel simple and convenient.\n\n"

    "With SkyNest, users can search for available flights, "
    "select their preferred flight, enter passenger details, "
    "complete their payment, and manage their bookings from "
    "one place.\n\n"

    "Our goal is to provide a straightforward and user-friendly "
    "booking experience while keeping important booking "
    "information organized and accessible.\n\n"

    "From searching for a flight to managing an existing "
    "reservation, SkyNest brings the essential parts of the "
    "flight booking process together in one application."
)
tk.Message(
    content_frame,
    text=about_text,
    font=("Arial", 13,"bold"),
    bg="#D0E6F5",
    fg="#000000",
    justify="left",
    width=650
).pack(
    padx=30,
    pady=10,
    anchor="w"
)
tk.Button(
    root,
    text="Back to Homepage",
    command=go_back,
    font=("Arial", 13, "bold"),
    bg="#0D2E91",
    fg="white",
    activebackground="#09246F",
    activeforeground="white",
    width=20,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2"
).pack(
    pady=25
)
root.mainloop()