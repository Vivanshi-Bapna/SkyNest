import tkinter as tk
from tkinter import messagebox
import pymysql
from datetime import datetime
import random
import string
import os
import sys
import subprocess
import re
import json
from db_config import DB_CONFIG
try:
    user_email = sys.argv[1]
    flight_id = int(sys.argv[2])
    flight_price = float(sys.argv[3])
    num_passengers = int(sys.argv[4])
except (IndexError, ValueError):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Error",
        "Payment information or flight information was not passed correctly."
    )
    root.destroy()
    sys.exit()
if len(sys.argv) >= 6:
    state_file = sys.argv[5]
else:
    state_file = None
def generate_transaction_id():
    return "TXN" + ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=12
        )
    )
def generate_booking_code():
    return "SKY" + ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=8
        )
    )
def validate_expiry(expiry):
    if not re.fullmatch(
        r"(0[1-9]|1[0-2])/[0-9]{2}",
        expiry
    ):
        return False
    try:
        month, year = expiry.split("/")
        month = int(month)
        year = int("20" + year)
        current_date = datetime.now()
        if year < current_date.year:
            return False
        if (
            year == current_date.year
            and month < current_date.month
        ):
            return False
        return True
    except ValueError:
        return False
def load_passenger_state():
    if not state_file:
        messagebox.showerror(
            "Passenger Details Error",
            "Passenger information could not be found.\n\n"
            "Please go back and enter the passenger details again."
        )
        return None
    if not os.path.exists(state_file):
        messagebox.showerror(
            "Passenger Details Error",
            "Passenger information could not be found.\n\n"
            "Please go back and enter the passenger details again."
        )
        return None
    try:
        with open(
            state_file,
            "r",
            encoding="utf-8"
        ) as file:
            state = json.load(file)
        return state
    except Exception as e:
        messagebox.showerror(
            "Passenger Details Error",
            f"Could not read passenger information.\n\n{e}"
        )
        return None
def go_back_to_details():
    state = load_passenger_state()
    if not state:
        return
    passenger_type = state.get(
        "passenger_type"
    )
    if passenger_type == "domestic":
        script_name = "domestic_passenger_details.py"
    elif passenger_type == "international":
        script_name = "international_passenger_details.py"
    else:
        messagebox.showerror(
            "Error",
            "Passenger type could not be determined."
        )
        return
    script_path = os.path.join(
        os.path.dirname(__file__),
        script_name
    )
    try:
        root.destroy()
        subprocess.Popen([
            sys.executable,
            script_path,
            str(num_passengers),
            user_email,
            str(flight_id),
            str(flight_price),
            state_file
        ])
    except Exception as e:
        messagebox.showerror(
            "Navigation Error",
            f"Could not return to passenger details.\n\n{e}"
        )
def process_payment():
    card_number = card_entry.get().replace(
        " ",
        ""
    )
    expiry_date = expiry_entry.get().strip()
    cvv = cvv_entry.get().strip()
    name_on_card = name_entry.get().strip()
    if (
        not card_number.isdigit()
        or len(card_number) != 16
    ):
        messagebox.showerror(
            "Invalid Card",
            "Card number must contain exactly 16 digits."
        )
        return
    if (
        not cvv.isdigit()
        or len(cvv) != 3
    ):
        messagebox.showerror(
            "Invalid CVV",
            "CVV must contain exactly 3 digits."
        )
        return
    if not validate_expiry(expiry_date):
        messagebox.showerror(
            "Invalid Expiry Date",
            "Enter a valid expiry date in MM/YY format."
        )
        return
    if not name_on_card:
        messagebox.showerror(
            "Invalid Name",
            "Please enter the name on the card."
        )
        return
    state = load_passenger_state()
    if not state:
        return
    passenger_type = state.get(
        "passenger_type"
    )
    passengers = state.get(
        "passengers",
        []
    )
    if passenger_type not in [
        "domestic",
        "international"
    ]:
        messagebox.showerror(
            "Passenger Error",
            "Invalid passenger information."
        )
        return
    if len(passengers) != num_passengers:
        messagebox.showerror(
            "Passenger Error",
            "The passenger information does not match "
            "the number of passengers."
        )
        return
    connection = None
    cursor = None
    try:
        connection = pymysql.connect(
            **DB_CONFIG
        )
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                id,
                flight_name,
                flight_number,
                source_city,
                destination_city,
                depart_time,
                arrival_time,
                duration,
                price
            FROM flight_info
            WHERE id = %s
            """,
            (flight_id,)
        )
        flight = cursor.fetchone()
        if not flight:
            messagebox.showerror(
                "Flight Error",
                "The selected flight could not be found."
            )
            return
        flight_price = float(
            flight["price"]
        )
        source_city = flight[
            "source_city"
        ]
        destination_city = flight[
            "destination_city"
        ]
        total_amount = int(
            flight_price * num_passengers
        )
        cursor.execute(
            """
            SELECT
                departure_date,
                return_date,
                num_passenger
            FROM flight_searches
            WHERE email = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_email,)
        )
        search_data = cursor.fetchone()
        if not search_data:
            messagebox.showerror(
                "Booking Error",
                "Flight search information could not be found."
            )
            return
        departure_date = search_data[
            "departure_date"
        ]
        return_date = search_data[
            "return_date"
        ]
        transaction_id = generate_transaction_id()
        booking_code = generate_booking_code()
        masked_card_number = (
            "************"
            + card_number[-4:]
        )
        cursor.execute(
            """
            INSERT INTO payment_info
            (
                card_number,
                name_on_card,
                expiry_date,
                transaction_id
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                masked_card_number,
                name_on_card,
                expiry_date,
                transaction_id
            )
        )
        cursor.execute(
            """
            INSERT INTO bookings
            (
                flight_id,
                booking_code,
                source_city,
                destination_city,
                departure_date,
                return_date,
                num_passenger,
                total_amount,
                status,
                booked_on,
                payment_method,
                email
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Confirmed',
                NOW(),
                %s,
                %s
            )
            """,
            (
                flight_id,
                booking_code,
                source_city,
                destination_city,
                departure_date,
                return_date,
                num_passengers,
                total_amount,
                "Card",
                user_email
            )
        )
        if passenger_type == "domestic":
            for passenger in passengers:
                dob = datetime.strptime(
                    passenger["dob"],
                    "%d/%m/%Y"
                ).date()
                cursor.execute(
                    """
                    INSERT INTO domestic_passenger
                    (
                        name,
                        gender,
                        dob,
                        nationality,
                        govt_id_type,
                        govt_id_number,
                        phone,
                        email,
                        meal_preference,
                        wheelchair_assistance
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        passenger["name"],
                        passenger["gender"],
                        dob,
                        passenger["nationality"],
                        passenger["govt_id_type"],
                        passenger["govt_id_number"],
                        passenger["phone"],
                        passenger["email"],
                        passenger["meal"],
                        int(
                            passenger["wheelchair"]
                        )
                    )
                )
        elif passenger_type == "international":
            for passenger in passengers:
                dob = datetime.strptime(
                    passenger["dob"],
                    "%d/%m/%Y"
                ).date()
                passport_expiry = datetime.strptime(
                    passenger["expiry"],
                    "%d/%m/%Y"
                ).date()
                cursor.execute(
                    """
                    INSERT INTO international_passenger
                    (
                        name,
                        gender,
                        dob,
                        nationality,
                        residence,
                        passport_number,
                        passport_expiry,
                        issuing_country,
                        phone,
                        email,
                        meal_preference,
                        wheelchair_assistance,
                        unaccompanied_minor
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        passenger["name"],
                        passenger["gender"],
                        dob,
                        passenger["nationality"],
                        passenger["residence"],
                        passenger["passport"],
                        passport_expiry,
                        passenger["issuing"],
                        passenger["phone"],
                        passenger["email"],
                        passenger["meal"],
                        int(
                            passenger["wheelchair"]
                        ),
                        int(
                            passenger["minor"]
                        )
                    )
                )
        connection.commit()
        if state_file and os.path.exists(state_file):
            try:
                os.remove(
                    state_file
                )
            except OSError:
                pass
        messagebox.showinfo(
            "Payment Successful",
            f"Payment successful!\n\n"
            f"Transaction ID: {transaction_id}\n"
            f"Booking Code: {booking_code}\n"
            f"Flight: {flight['flight_number']}\n"
            f"Route: {source_city} → {destination_city}\n"
            f"Passengers: {num_passengers}\n"
            f"Total Amount: ₹{total_amount}"
        )
        root.destroy()
        script_path = os.path.join(
            os.path.dirname(__file__),
            "booking_confirm.py"
        )
        subprocess.Popen([
            sys.executable,
            script_path,
            user_email,
            booking_code,
            transaction_id,
            flight["flight_number"],
            source_city,
            destination_city,
            str(num_passengers),
            str(total_amount)
        ])
    except Exception as e:
        if connection:
            connection.rollback()
        messagebox.showerror(
            "Payment Error",
            f"Something went wrong:\n\n{e}"
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
root = tk.Tk()
root.title(
    "SkyNest - Payment"
)
root.geometry(
    "600x750"
)
root.configure(
    bg="#D0E6F5"
)
root.resizable(
    False,
    False
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
title_label = tk.Label(
    root,
    text="SkyNest Payment",
    font=("Arial", 24, "bold"),
    bg="#D0E6F5",
    fg="#1F3A5F"
)
title_label.pack(
    pady=(10, 20)
)
payment_frame = tk.Frame(
    root,
    bg="#D0E6F5",
    padx=30,
    pady=25
)
payment_frame.pack(
    padx=40,
    pady=5,
    fill="x"
)
tk.Label(
    payment_frame,
    text="Card Number",
    font=("Arial", 12, "bold"),
    bg="#D0E6F5"
).pack(
    anchor="w",
    pady=(5, 5)
)
card_entry = tk.Entry(
    payment_frame,
    font=("Arial", 13),
    width=35
)
card_entry.pack(
    pady=(0, 15),
    ipady=7
)
tk.Label(
    payment_frame,
    text="Expiry Date (MM/YY)",
    font=("Arial", 12, "bold"),
    bg="#D0E6F5"
).pack(
    anchor="w",
    pady=(5, 5)
)
expiry_entry = tk.Entry(
    payment_frame,
    font=("Arial", 13),
    width=35
)
expiry_entry.pack(
    pady=(0, 15),
    ipady=7
)
tk.Label(
    payment_frame,
    text="CVV",
    font=("Arial", 12, "bold"),
    bg="#D0E6F5"
).pack(
    anchor="w",
    pady=(5, 5)
)
cvv_entry = tk.Entry(
    payment_frame,
    font=("Arial", 13),
    width=35,
    show="*"
)
cvv_entry.pack(
    pady=(0, 15),
    ipady=7
)
tk.Label(
    payment_frame,
    text="Name on Card",
    font=("Arial", 12, "bold"),
    bg="#D0E6F5"
).pack(
    anchor="w",
    pady=(5, 5)
)
name_entry = tk.Entry(
    payment_frame,
    font=("Arial", 13),
    width=35
)
name_entry.pack(
    pady=(0, 15),
    ipady=7
)
total_preview = int(
    flight_price * num_passengers
)
tk.Label(
    payment_frame,
    text=f"Total Amount: ₹{total_preview}",
    font=("Arial", 16, "bold"),
    bg="#D0E6F5",
    fg="#1F3A5F"
).pack(
    pady=10
)
pay_button = tk.Button(
    payment_frame,
    text="Pay Now",
    font=("Arial", 14, "bold"),
    bg="#1F3A5F",
    fg="white",
    activebackground="#162B46",
    activeforeground="white",
    width=20,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2",
    command=process_payment
)
pay_button.pack(
    pady=(15, 10)
)
back_button = tk.Button(
    payment_frame,
    text="Back to Passenger Details",
    font=("Arial", 14, "bold"),
    bg="#4682B4",
    fg="white",
    activebackground="#315F7D",
    activeforeground="white",
    width=20,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2",
    command=go_back_to_details
)
back_button.pack(
    pady=(10, 5)
)
root.mainloop()