import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime
import pymysql
import sys
import os
import subprocess
import json
import tempfile
import uuid
from db_config import DB_CONFIG
def save_passenger_state():
    passengers = []
    for passenger in passenger_entries:
        passengers.append({
            "name": passenger["name"].get().strip(),
            "gender": passenger["gender"].get().strip(),
            "dob": passenger["dob"].get().strip(),
            "nationality": passenger["nationality"].get().strip(),
            "govt_id_type": passenger["govt_id_type"].get().strip(),
            "govt_id_number": passenger["govt_id_number"].get().strip(),
            "phone": passenger["phone"].get().strip(),
            "email": passenger["email"].get().strip(),
            "meal": passenger["meal"].get().strip(),
            "wheelchair": bool(passenger["wheelchair"].get())
        })
    state = {
        "passenger_type": "domestic",
        "user_email": user_email,
        "flight_id": flight_id,
        "flight_price": flight_price,
        "num_passengers": num_passengers,
        "passengers": passengers
    }
    with open(state_file, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)
def submit_all():
    submit_btn.config(state="disabled")
    try:
        for i, passenger in enumerate(passenger_entries):
            name = passenger["name"].get().strip()
            gender = passenger["gender"].get().strip()
            dob = passenger["dob"].get().strip()
            nationality = passenger["nationality"].get().strip()
            gov_id_type = passenger["govt_id_type"].get().strip()
            gov_id_number = passenger["govt_id_number"].get().strip()
            phone = passenger["phone"].get().strip()
            email = passenger["email"].get().strip()
            if gender == "Select Gender":
                gender = ""
            if gov_id_type == "Select ID Type":
                gov_id_type = ""
            if not all([
                name,
                gender,
                dob,
                nationality,
                gov_id_type,
                gov_id_number,
                phone,
                email
            ]):
                messagebox.showwarning(
                    "Missing Fields",
                    f"Please complete all required fields for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            if not re.fullmatch(
                r"[^@]+@[^@]+\.[^@]+",
                email
            ):
                messagebox.showerror(
                    "Email Error",
                    f"Invalid email for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            if not re.fullmatch(
                r"\d{10}",
                phone
            ):
                messagebox.showerror(
                    "Phone Error",
                    f"Phone number must be 10 digits for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            try:
                datetime.strptime(
                    dob,
                    "%d/%m/%Y"
                )
            except ValueError:
                messagebox.showerror(
                    "Date Format Error",
                    f"Use DD/MM/YYYY format for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
        save_passenger_state()
        script_path = os.path.join(
            os.path.dirname(__file__),
            "payment.py"
        )
        root.destroy()
        subprocess.Popen([
            sys.executable,
            script_path,
            user_email,
            str(flight_id),
            str(flight_price),
            str(num_passengers),
            state_file
        ])
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not continue to payment.\n\n{e}"
        )
        submit_btn.config(state="normal")
def create_passenger_form(container, index):
    frame = tk.LabelFrame(
        container,
        text=f"Passenger {index + 1}",
        font=("Arial", 11, "bold"),
        bg="#D0E6F5",
        fg="#0A3D62",
        bd=1,
        relief="solid",
        padx=15,
        pady=10
    )
    frame.pack(
        padx=10,
        pady=10,
        fill="x"
    )
    def add_field(label, row):
        tk.Label(
            frame,
            text=label,
            bg="#D0E6F5",
            fg="#333333"
        ).grid(
            row=row,
            column=0,
            sticky="w"
        )
        entry = tk.Entry(
            frame,
            width=40
        )
        entry.grid(
            row=row,
            column=1,
            pady=2
        )
        return entry
    entry_name = add_field(
        "Full Name*",
        0
    )
    gender_var = tk.StringVar()
    tk.Label(
        frame,
        text="Gender*",
        bg="#D0E6F5",
        fg="#333333"
    ).grid(
        row=1,
        column=0,
        sticky="w"
    )
    gender_box = ttk.Combobox(
        frame,
        textvariable=gender_var,
        values=[
            "Male",
            "Female",
            "Other"
        ],
        width=37,
        state="readonly"
    )
    gender_box.set("Select Gender")
    gender_box.grid(
        row=1,
        column=1
    )
    entry_dob = add_field(
        "Date of Birth (DD/MM/YYYY)*",
        2
    )
    entry_nat = add_field(
        "Nationality*",
        3
    )
    gov_id_type_var = tk.StringVar()
    tk.Label(
        frame,
        text="Govt ID Type*",
        bg="#D0E6F5",
        fg="#333333"
    ).grid(
        row=4,
        column=0,
        sticky="w"
    )
    gov_id_box = ttk.Combobox(
        frame,
        textvariable=gov_id_type_var,
        values=[
            "Aadhar",
            "PAN",
            "Driving License"
        ],
        width=37,
        state="readonly"
    )
    gov_id_box.set("Select ID Type")
    gov_id_box.grid(
        row=4,
        column=1
    )
    entry_pass = add_field(
        "Govt ID Number*",
        5
    )
    entry_phone = add_field(
        "Phone Number*",
        6
    )
    entry_email = add_field(
        "Email Address*",
        7
    )
    tk.Label(
        frame,
        text="Meal Preference",
        bg="#D0E6F5",
        fg="#333333"
    ).grid(
        row=8,
        column=0,
        sticky="w"
    )
    meal_var = tk.StringVar()
    meal_box = ttk.Combobox(
        frame,
        textvariable=meal_var,
        values=[
            "Non Vegetarian",
            "Vegetarian",
            "Vegan",
            "Jain",
            "Gluten-Free"
        ],
        width=37,
        state="readonly"
    )
    meal_box.set("Select Meal")
    meal_box.grid(
        row=8,
        column=1
    )
    wheelchair_var = tk.BooleanVar()
    tk.Checkbutton(
        frame,
        text="Wheelchair Assistance",
        variable=wheelchair_var,
        bg="#D0E6F5",
        activebackground="#D0E6F5"
    ).grid(
        row=9,
        column=1,
        sticky="w"
    )
    return {
        "name": entry_name,
        "gender": gender_var,
        "dob": entry_dob,
        "nationality": entry_nat,
        "govt_id_type": gov_id_type_var,
        "govt_id_number": entry_pass,
        "phone": entry_phone,
        "email": entry_email,
        "meal": meal_var,
        "wheelchair": wheelchair_var
    }
root = tk.Tk()
root.title(
    "Passenger Details"
)
root.geometry(
    "700x800"
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
        "Could not load SkyNest logo:",e
    )
tk.Label(
    root,
    text="Passenger Details",
    font=("Helvetica", 26, "bold"),
    bg="#D0E6F5",
    fg="#0A3D62"
).pack(
    pady=(5, 15)
)
content_frame = tk.Frame(
    root,
    bg="#D0E6F5"
)
content_frame.pack(
    fill="both",
    expand=True,
    padx=20
)
scroll_canvas = tk.Canvas(
    content_frame,
    bg="#D0E6F5",
    highlightthickness=0
)
scrollbar = ttk.Scrollbar(
    content_frame,
    orient="vertical",
    command=scroll_canvas.yview
)
scroll_canvas.configure(
    yscrollcommand=scrollbar.set
)
scrollbar.pack(
    side="right",
    fill="y"
)
scroll_canvas.pack(
    side="left",
    fill="both",
    expand=True
)
scroll_frame = tk.Frame(
    scroll_canvas,
    bg="#D0E6F5"
)
frame_window = scroll_canvas.create_window(
    (0, 0),
    window=scroll_frame,
    anchor="nw"
)
def on_configure(event):
    scroll_canvas.configure(
        scrollregion=scroll_canvas.bbox("all")
    )
scroll_frame.bind(
    "<Configure>",
    on_configure
)
def resize_frame(event):
    scroll_canvas.itemconfig(
        frame_window,
        width=event.width
    )
scroll_canvas.bind(
    "<Configure>",
    resize_frame
)
try:
    num_passengers = int(
        sys.argv[1]
    )
    user_email = sys.argv[2]
    flight_id = int(
        sys.argv[3]
    )
    flight_price = float(
        sys.argv[4]
    )
    if len(sys.argv) >= 6:
        state_file = sys.argv[5]
    else:
        state_file = os.path.join(
            tempfile.gettempdir(),
            f"skynest_passengers_{uuid.uuid4().hex}.json"
        )
except (IndexError, ValueError):
    messagebox.showerror(
        "Error",
        "Passenger count, user email, or flight information was not passed."
    )
    root.destroy()
    sys.exit()
passenger_entries = []
for i in range(num_passengers):
    form = create_passenger_form(
        scroll_frame,i
    )
    passenger_entries.append(
        form
    )
if os.path.exists(state_file):
    try:
        with open(
            state_file,
            "r",
            encoding="utf-8"
        ) as file:
            saved_state = json.load(file)
        saved_passengers = saved_state.get(
            "passengers",
            []
        )
        for i, data in enumerate(saved_passengers):
            if i >= len(passenger_entries):
                break
            passenger = passenger_entries[i]
            passenger["name"].insert(
                0,
                data.get("name", "")
            )
            passenger["gender"].set(
                data.get(
                    "gender",
                    "Select Gender"
                )
            )
            passenger["dob"].insert(
                0,
                data.get("dob", "")
            )
            passenger["nationality"].insert(
                0,
                data.get("nationality", "")
            )
            passenger["govt_id_type"].set(
                data.get(
                    "govt_id_type",
                    "Select ID Type"
                )
            )
            passenger["govt_id_number"].insert(
                0,
                data.get("govt_id_number", "")
            )
            passenger["phone"].insert(
                0,
                data.get("phone", "")
            )
            passenger["email"].insert(
                0,
                data.get("email", "")
            )
            passenger["meal"].set(
                data.get(
                    "meal",
                    "Select Meal"
                )
            )
            passenger["wheelchair"].set(
                data.get(
                    "wheelchair",
                    False
                )
            )
    except Exception as e:
        print(
            "Could not restore passenger details:",e
        )
def go_to_flight_results():
    try:
        conn = pymysql.connect(
            **DB_CONFIG
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT source_city, destination_city
            FROM flight_info
            WHERE id = %s
            """,
            (flight_id,)
        )
        flight = cursor.fetchone()
        if not flight:
            messagebox.showerror(
                "Error",
                "Could not find the selected flight."
            )
            return
        source_city = flight["source_city"]
        destination_city = flight["destination_city"]
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except OSError:
                pass
        root.destroy()
        script_path = os.path.join(
            os.path.dirname(__file__),
            "flight_results.py"
        )
        subprocess.Popen([
            sys.executable,
            script_path,
            source_city,
            destination_city,
            str(num_passengers),
            user_email
        ])
    except Exception as e:
        messagebox.showerror(
            "Database Error",
            f"Could not return to flight results.\n\n{e}"
        )
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()
button_frame = tk.Frame(
    root,
    bg="#D0E6F5"
)
button_frame.pack(
    pady=20
)
tk.Button(
    button_frame,
    text="Back to Flight Results",
    command=go_to_flight_results,
    font=("Arial", 12, "bold"),
    bg="#4682B4",
    fg="white",
    activebackground="#315F7D",
    activeforeground="white",
    width=22,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2"
).pack(
    side="left",
    padx=10
)
submit_btn = tk.Button(
    button_frame,
    text="Continue to Payment",
    command=submit_all,
    font=("Arial", 12, "bold"),
    bg="#0D2E91",
    fg="white",
    activebackground="#09246F",
    activeforeground="white",
    width=22,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2"
)
submit_btn.pack(
    side="left",
    padx=10
)
root.mainloop()