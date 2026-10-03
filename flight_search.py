import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import pymysql
from datetime import datetime, date
import subprocess
import sys
import os
from db_config import DB_CONFIG
if len(sys.argv) > 1:
    CURRENT_USER_EMAIL = sys.argv[1].strip()
else:
    CURRENT_USER_EMAIL = None
if not CURRENT_USER_EMAIL:
    temp_root = tk.Tk()
    temp_root.withdraw()
    messagebox.showerror(
        "Login Required",
        "User not logged in.\nPlease login before searching for flights."
    )
    temp_root.destroy()
    sys.exit()

def initialize_database(
    trip_type,
    source,
    dest,
    depart_date,
    return_date,
    passengers
):
    connection = None
    cursor = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = """
            INSERT INTO flight_searches
            (
                trip_type,
                source_city,
                destination_city,
                departure_date,
                return_date,
                num_passenger,
                email
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                trip_type,
                source,
                dest,
                depart_date,
                return_date,
                passengers,
                CURRENT_USER_EMAIL
            )
        )
        connection.commit()
        return True
    except pymysql.MySQLError as e:
        if connection:
            connection.rollback()
        messagebox.showerror(
            "Database Error",
            f"Could not save your flight search.\n\n{e}"
        )
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
def launch_flight_results(source, dest, passengers, departure_date):
    script_path = os.path.join(
        os.path.dirname(__file__),
        "flight_results.py"
    )
    subprocess.Popen([
        sys.executable,
        script_path,
        source,
        dest,
        str(passengers),
        CURRENT_USER_EMAIL,
        departure_date
    ])
def open_bookings():
    bookings_script_path = os.path.join(
        os.path.dirname(__file__),
        "my_booking.py"
    )
    try:
        root.destroy()
        subprocess.Popen([
            sys.executable,
            bookings_script_path,
            CURRENT_USER_EMAIL
        ])
    except Exception as e:
        messagebox.showerror(
            "Navigation Error",
            f"Could not open My Bookings.\n\n{e}"
        )
def update_return_date_field():
    if trip_type_var.get() == "One Way":
        return_date_entry.grid_remove()
        return_date_label.grid_remove()
        return_date_var.set("")
    else:
        return_date_label.grid()
        return_date_entry.grid()
def find_flights():
    trip_type = trip_type_var.get().strip()
    source = source_city_var.get().strip()
    dest = destination_city_var.get().strip()
    depart_str = departure_date_var.get().strip()
    return_str = return_date_var.get().strip()
    passengers_str = num_passengers_var.get().strip()
    if not source:
        messagebox.showerror(
            "Missing Source",
            "Please enter your departure city."
        )
        return
    if not dest:
        messagebox.showerror(
            "Missing Destination",
            "Please enter your destination city."
        )
        return
    if not depart_str:
        messagebox.showerror(
            "Missing Date",
            "Please select a departure date."
        )
        return
    if not passengers_str:
        messagebox.showerror(
            "Missing Passengers",
            "Please enter the number of passengers."
        )
        return
    if source.lower() == dest.lower():
        messagebox.showerror(
            "Invalid Cities",
            "Source and Destination cannot be the same."
        )
        return
    cities = [
        "London",
        "Singapore",
        "New York City",
        "Dubai",
        "Tokyo",
        "Seoul",
        "Ahmedabad",
        "Mumbai",
        "Delhi",
        "Bengaluru",
        "Pune",
        "Hyderabad"
    ]
    valid_cities = [city.lower() for city in cities]
    if source.lower() not in valid_cities:
        messagebox.showerror(
            "Invalid Source",
            f"{source} is not a supported city."
        )
        return
    if dest.lower() not in valid_cities:
        messagebox.showerror(
            "Invalid Destination",
            f"{dest} is not a supported city."
        )
        return
    try:
        passengers = int(passengers_str)
        if passengers <= 0:
            raise ValueError
        if passengers > 9:
            messagebox.showerror(
                "Invalid Passengers",
                "Maximum 9 passengers can be booked at once."
            )
            return
    except ValueError:
        messagebox.showerror(
            "Invalid Passengers",
            "Number of passengers must be a positive number."
        )
        return
    date_format = "%d-%m-%Y"
    try:
        depart_date = datetime.strptime(
            depart_str,
            date_format
        ).date()
    except ValueError:
        messagebox.showerror(
            "Date Error",
            "Please use the date format DD-MM-YYYY."
        )
        return
    if depart_date < date.today():
        messagebox.showerror(
            "Invalid Departure Date",
            "Departure date cannot be in the past."
        )
        return
    return_str_mysql = None
    if trip_type == "Round Trip":
        if not return_str:
            messagebox.showerror(
                "Missing Return Date",
                "Please select a return date for a round trip."
            )
            return
        try:
            return_date = datetime.strptime(
                return_str,
                date_format
            ).date()
        except ValueError:
            messagebox.showerror(
                "Date Error",
                "Please use the date format DD-MM-YYYY."
            )
            return
        if return_date < depart_date:
            messagebox.showerror(
                "Invalid Return Date",
                "Return date cannot be before the departure date."
            )
            return
        return_str_mysql = return_date.strftime(
            "%Y-%m-%d"
        )
    depart_str_mysql = depart_date.strftime(
        "%Y-%m-%d"
    )
    saved = initialize_database(
        trip_type,
        source,
        dest,
        depart_str_mysql,
        return_str_mysql,
        passengers
    )
    if not saved:
        return
    root.destroy()
    launch_flight_results(source, dest, passengers, depart_str_mysql)
root = tk.Tk()
root.title("SkyNest - Flight Search")
root.geometry("700x750")
root.configure(
    bg="#D0E6F5"
)
root.resizable(
    False,
    False
)
top_bar = tk.Frame(
    root,
    bg="#D0E6F5"
)
top_bar.pack(
    fill="x",
    pady=(10, 0),
    padx=0
)
# -----------------------------
# SkyNest Header / Logo
# -----------------------------
logo_path = os.path.join(
    os.path.dirname(__file__),
    "skynest_logo.png"
)

try:
    logo_image = tk.PhotoImage(file=logo_path)
    logo_image = logo_image.subsample(15, 15)

    logo_label = tk.Label(
        top_bar,
        image=logo_image,
        bg="#D0E6F5"
    )
    logo_label.pack(side="left")

except Exception as e:
    print("Could not load SkyNest logo:", e)

my_bookings_label = tk.Label(
    top_bar,
    text="My Bookings",
    font=("Arial", 12, "underline"),
    fg="#0000EE",
    bg="#D0E6F5",
    cursor="hand2"
)
my_bookings_label.pack(
    side="right",
    padx=20
)
my_bookings_label.bind(
    "<Button-1>",
    lambda event: open_bookings()
)
tk.Label(
    root,
    text="Find Your Flight!",
    font=("Georgia", 34, "bold italic"),
    bg="#D0E6F5",
    fg="#2F4F4F"
).pack(
    pady=(40, 10)
)
tk.Label(
    root,
    text="Search for the best deals",
    font=("Georgia", 20, "italic"),
    bg="#D0E6F5",
    fg="#6A5ACD"
).pack(
    pady=(0, 30)
)
form_frame = tk.Frame(
    root,
    bg="#D0E6F5",
    padx=30,
    pady=30
)
form_frame.pack(
    pady=20,
    padx=50,
    fill="both",
    expand=True
)
trip_type_var = tk.StringVar(
    value="Round Trip"
)
tk.Radiobutton(
    form_frame,
    text="Round Trip",
    variable=trip_type_var,
    value="Round Trip",
    bg="#D0E6F5",
    font=("Arial", 11),
    command=update_return_date_field
).grid(
    row=0,
    column=0,
    padx=20,
    pady=10
)
tk.Radiobutton(
    form_frame,
    text="One Way",
    variable=trip_type_var,
    value="One Way",
    bg="#D0E6F5",
    font=("Arial", 11),
    command=update_return_date_field
).grid(
    row=0,
    column=1,
    padx=20,
    pady=10
)
source_city_var = tk.StringVar()
destination_city_var = tk.StringVar()
departure_date_var = tk.StringVar()
return_date_var = tk.StringVar()
num_passengers_var = tk.StringVar()
tk.Label(
    form_frame,
    text="From",
    font=("Arial", 11, "bold"),
    bg="#D0E6F5"
).grid(
    row=1,
    column=0,
    sticky="w",
    padx=10,
    pady=(15, 5)
)
source_entry = tk.Entry(
    form_frame,
    textvariable=source_city_var,
    font=("Arial", 11),
    width=25
)
source_entry.grid(
    row=2,
    column=0,
    padx=10,
    pady=5
)
tk.Label(
    form_frame,
    text="To",
    font=("Arial", 11, "bold"),
    bg="#D0E6F5"
).grid(
    row=1,
    column=1,
    sticky="w",
    padx=10,
    pady=(15, 5)
)
destination_entry = tk.Entry(
    form_frame,
    textvariable=destination_city_var,
    font=("Arial", 11),
    width=25
)
destination_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=5
)
tk.Label(
    form_frame,
    text="Departure Date",
    font=("Arial", 11, "bold"),
    bg="#D0E6F5"
).grid(
    row=3,
    column=0,
    sticky="w",
    padx=10,
    pady=(20, 5)
)
departure_date_entry = DateEntry(
    form_frame,
    textvariable=departure_date_var,
    date_pattern="dd-mm-yyyy",
    mindate=date.today(),
    width=22
)
departure_date_entry.grid(
    row=4,
    column=0,
    padx=10,
    pady=5
)
return_date_label = tk.Label(
    form_frame,
    text="Return Date",
    font=("Arial", 11, "bold"),
    bg="#D0E6F5"
)
return_date_label.grid(
    row=3,
    column=1,
    sticky="w",
    padx=10,
    pady=(20, 5)
)
return_date_entry = DateEntry(
    form_frame,
    textvariable=return_date_var,
    date_pattern="dd-mm-yyyy",
    mindate=date.today(),
    width=22
)
return_date_entry.grid(
    row=4,
    column=1,
    padx=10,
    pady=5
)
tk.Label(
    form_frame,
    text="Number of Passengers",
    font=("Arial", 11, "bold"),
    bg="#D0E6F5"
).grid(
    row=5,
    column=0,
    columnspan=2,
    pady=(25, 5)
)
passenger_entry = tk.Entry(
    form_frame,
    textvariable=num_passengers_var,
    font=("Arial", 11),
    width=25,
    justify="center"
)
passenger_entry.grid(
    row=6,
    column=0,
    columnspan=2,
    pady=5
)
find_button = tk.Button(
    root,
    text="Find Flights",
    command=find_flights,
    bg="#4682B4",
    fg="white",
    font=("Arial", 12, "bold"),
    padx=30,
    pady=10,
    cursor="hand2"
)
find_button.pack(
    pady=30
)
update_return_date_field()
root.mainloop()