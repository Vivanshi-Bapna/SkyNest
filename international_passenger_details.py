import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime, date
import pymysql
import sys
import subprocess
import os
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
            "residence": passenger["residence"].get().strip(),
            "passport": passenger["passport"].get().strip(),
            "expiry": passenger["expiry"].get().strip(),
            "issuing": passenger["issuing"].get().strip(),
            "phone": passenger["phone"].get().strip(),
            "email": passenger["email"].get().strip(),
            "meal": passenger["meal"].get().strip(),
            "wheelchair": bool(passenger["wheelchair"].get()),
            "minor": bool(passenger["minor"].get())
        })
    state = {
        "passenger_type": "international",
        "user_email": user_email,
        "flight_id": flight_id,
        "flight_price": flight_price,
        "num_passengers": num_passengers,
        "passengers": passengers
    }
    try:
        with open(state_file, "w", encoding="utf-8") as file:
            json.dump(state, file, indent=4)
        return True
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not save passenger details.\n\n{e}"
        )
        return False
def submit_all():
    submit_btn.config(state="disabled")
    try:
        for i, passenger in enumerate(passenger_entries):
            name = passenger["name"].get().strip()
            gender = passenger["gender"].get().strip()
            dob = passenger["dob"].get().strip()
            nationality = passenger["nationality"].get().strip()
            residence = passenger["residence"].get().strip()
            passport_num = passenger["passport"].get().strip()
            passport_expiry = passenger["expiry"].get().strip()
            issuing_country = passenger["issuing"].get().strip()
            phone = passenger["phone"].get().strip()
            email = passenger["email"].get().strip()
            meal = passenger["meal"].get().strip()
            wheelchair = int(passenger["wheelchair"].get())
            minor = int(passenger["minor"].get())
            if not all([
                name,
                gender,
                dob,
                nationality,
                residence,
                passport_num,
                passport_expiry,
                issuing_country,
                phone,
                email
            ]):
                messagebox.showwarning(
                    "Missing Fields",
                    f"Please fill all required fields for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            if gender not in ["Male", "Female", "Other"]:
                messagebox.showerror(
                    "Gender Error",
                    f"Please select a gender for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            if not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                email
            ):
                messagebox.showerror(
                    "Email Error",
                    f"Please enter a valid email for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            if not re.fullmatch(r"\d{10}", phone):
                messagebox.showerror(
                    "Phone Error",
                    f"Phone number must contain exactly 10 digits "
                    f"for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            try:
                dob_formatted = datetime.strptime(
                    dob,
                    "%d/%m/%Y"
                ).date()
                passport_expiry_formatted = datetime.strptime(
                    passport_expiry,
                    "%d/%m/%Y"
                ).date()
            except ValueError:
                messagebox.showerror(
                    "Date Error",
                    f"Use DD/MM/YYYY format for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            if dob_formatted > date.today():
                messagebox.showerror(
                    "DOB Error",
                    f"Date of birth cannot be in the future "
                    f"for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
            if passport_expiry_formatted < date.today():
                messagebox.showerror(
                    "Passport Error",
                    f"Passport has expired for passenger {i + 1}."
                )
                submit_btn.config(state="normal")
                return
        if not save_passenger_state():
            submit_btn.config(state="normal")
            return
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
            f"Something went wrong.\n\n{e}"
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
            width=40,
            bg="white"
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
    gender_var = tk.StringVar(
        value="Select Gender"
    )
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
    ttk.Combobox(
        frame,
        textvariable=gender_var,
        values=[
            "Select Gender",
            "Male",
            "Female",
            "Other"
        ],
        width=37,
        state="readonly"
    ).grid(
        row=1,
        column=1
    )
    entry_dob = add_field(
        "DOB (DD/MM/YYYY)*",
        2
    )
    entry_nat = add_field(
        "Nationality*",
        3
    )
    entry_res = add_field(
        "Country of Residence*",
        4
    )
    entry_pass = add_field(
        "Passport Number*",
        5
    )
    entry_exp = add_field(
        "Passport Expiry*",
        6
    )
    entry_iss = add_field(
        "Issuing Country*",
        7
    )
    entry_phone = add_field(
        "Phone Number*",
        8
    )
    entry_email = add_field(
        "Email Address*",
        9
    )
    tk.Label(
        frame,
        text="Meal Preference",
        bg="#D0E6F5",
        fg="#333333"
    ).grid(
        row=10,
        column=0,
        sticky="w"
    )
    meal_var = tk.StringVar(
        value="Select Meal"
    )
    ttk.Combobox(
        frame,
        textvariable=meal_var,
        values=[
            "Select Meal",
            "Non Vegetarian",
            "Vegetarian",
            "Vegan",
            "Jain",
            "Gluten-Free"
        ],
        width=37,
        state="readonly"
    ).grid(
        row=10,
        column=1
    )
    wheelchair_var = tk.BooleanVar(
        value=False
    )
    minor_var = tk.BooleanVar(
        value=False
    )
    tk.Checkbutton(
        frame,
        text="Wheelchair Assistance",
        variable=wheelchair_var,
        bg="#D0E6F5",
        activebackground="#D0E6F5"
    ).grid(
        row=11,
        column=1,
        sticky="w"
    )
    tk.Checkbutton(
        frame,
        text="Unaccompanied Minor",
        variable=minor_var,
        bg="#D0E6F5",
        activebackground="#D0E6F5"
    ).grid(
        row=12,
        column=1,
        sticky="w"
    )
    return {
        "name": entry_name,
        "gender": gender_var,
        "dob": entry_dob,
        "nationality": entry_nat,
        "residence": entry_res,
        "passport": entry_pass,
        "expiry": entry_exp,
        "issuing": entry_iss,
        "phone": entry_phone,
        "email": entry_email,
        "meal": meal_var,
        "wheelchair": wheelchair_var,
        "minor": minor_var
    }
root = tk.Tk()
root.title(
    "SkyNest - International Passenger Details"
)
root.geometry("700x800")
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
except (IndexError, ValueError):
    messagebox.showerror(
        "Error",
        "Passenger count, user email, or flight information "
        "was not passed correctly."
    )
    root.destroy()
    sys.exit()
if len(sys.argv) >= 6:
    state_file = sys.argv[5]
else:
    state_file = os.path.join(
        tempfile.gettempdir(),
        f"skynest_passengers_{uuid.uuid4().hex}.json"
    )
passenger_entries = []
for i in range(num_passengers):
    passenger_entries.append(
        create_passenger_form(
            scroll_frame,
            i
        )
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
        for i, data in enumerate(
            saved_passengers
        ):
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
            passenger["residence"].insert(
                0,
                data.get("residence", "")
            )
            passenger["passport"].insert(
                0,
                data.get("passport", "")
            )
            passenger["expiry"].insert(
                0,
                data.get("expiry", "")
            )
            passenger["issuing"].insert(
                0,
                data.get("issuing", "")
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
            passenger["minor"].set(
                data.get(
                    "minor",
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