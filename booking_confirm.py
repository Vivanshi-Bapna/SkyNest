import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
if len(sys.argv) < 9:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Error",
        "Booking confirmation details are missing."
    )
    root.destroy()
    sys.exit()
user_email = sys.argv[1]
booking_code = sys.argv[2]
transaction_id = sys.argv[3]
flight_number = sys.argv[4]
source_city = sys.argv[5]
destination_city = sys.argv[6]
num_passengers = sys.argv[7]
total_amount = sys.argv[8]
root = tk.Tk()
root.title(
    "SkyNest - Booking Confirmed"
)
root.geometry(
    "750x750"
)
root.resizable(
    False,
    False
)
root.configure(
    bg="#D0E6F5"
)
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
        "Could not load SkyNest logo:",
        e
    )
tk.Label(
    root,
    text="✓",
    font=("Arial", 50, "bold"),
    fg="#28A745",
    bg="#D0E6F5"
).pack(
    pady=(20, 0)
)
tk.Label(
    root,
    text="Booking Confirmed!",
    font=("Arial", 26, "bold"),
    fg="#0D2E91",
    bg="#D0E6F5"
).pack(
    pady=(0, 5)
)
tk.Label(
    root,
    text="Your flight has been booked successfully.",
    font=("Arial", 13),
    fg="#555555",
    bg="#D0E6F5"
).pack(
    pady=(0, 20)
)
details_frame = tk.Frame(
    root,
    bg="#D0E6F5",
    bd=1,
    relief="solid"
)
details_frame.pack(
    padx=80,
    fill="x"
)
def add_detail(label, value):
    row = tk.Frame(
        details_frame,
        bg="#D0E6F5"
    )
    row.pack(
        fill="x",
        padx=25,
        pady=9
    )
    tk.Label(
        row,
        text=label,
        font=("Arial", 11, "bold"),
        bg="#D0E6F5",
        fg="#555555",
        width=18,
        anchor="w"
    ).pack(
        side="left"
    )
    tk.Label(
        row,
        text=value,
        font=("Arial", 11),
        bg="#D0E6F5",
        fg="#222222",
        anchor="w"
    ).pack(
        side="left"
    )
add_detail(
    "Booking Code",
    booking_code
)
add_detail(
    "Transaction ID",
    transaction_id
)
add_detail(
    "Flight Number",
    flight_number
)
add_detail(
    "Route",
    f"{source_city} → {destination_city}"
)
add_detail(
    "Passengers",
    num_passengers
)
try:
    formatted_amount = (
        f"₹{float(total_amount):,.0f}"
    )
except ValueError:
    formatted_amount = (
        f"₹{total_amount}"
    )
add_detail(
    "Total Amount",
    formatted_amount
)
def open_my_bookings():
    try:
        root.destroy()
        script_path = os.path.join(
            os.path.dirname(__file__),
            "my_booking.py"
        )
        subprocess.Popen([
            sys.executable,
            script_path,
            user_email
        ])
    except Exception as e:
        messagebox.showerror(
            "Navigation Error",
            f"Could not open My Bookings.\n\n{e}"
        )
def back_to_flight_search():
    try:
        root.destroy()
        script_path = os.path.join(
            os.path.dirname(__file__),
            "flight_search.py"
        )
        subprocess.Popen([
            sys.executable,
            script_path,
            user_email
        ])
    except Exception as e:
        messagebox.showerror(
            "Navigation Error",
            f"Could not open Flight Search.\n\n{e}"
        )
button_frame = tk.Frame(
    root,
    bg="#D0E6F5"
)
button_frame.pack(
    pady=25
)
tk.Button(
    button_frame,
    text="View My Bookings",
    command=open_my_bookings,
    font=("Arial", 15, "bold"),
    bg="#0D2E91",
    fg="white",
    activebackground="#09246F",
    activeforeground="white",
    width=20,
    height=2,
    cursor="hand2",
    bd=0,
    relief="flat"
).pack(
    side="left",
    padx=15
)
tk.Button(
    button_frame,
    text="Back to Flight Search",
    command=back_to_flight_search,
    font=("Arial", 15, "bold"),
    bg="#28A745",
    fg="white",
    activebackground="#218838",
    activeforeground="white",
    width=20,
    height=2,
    cursor="hand2",
    bd=0,
    relief="flat"
).pack(
    side="left",
    padx=15
)
tk.Label(
    root,
    text="Thank you for choosing SkyNest ✈",
    font=("Arial", 11, "italic"),
    fg="#777777",
    bg="#D0E6F5"
).pack(
    pady=5
)
root.mainloop()