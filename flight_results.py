import tkinter as tk
from tkinter import messagebox
import pymysql
import os
import sys
import subprocess
from datetime import datetime, date 
from db_config import DB_CONFIG
try:
    source_city = sys.argv[1]
    destination_city = sys.argv[2]
    num_passengers = int(sys.argv[3])
    user_email = sys.argv[4]
    departure_date = sys.argv[5]
except Exception as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", "Missing flight search data.")
    sys.exit()
def fetch_flights(source_city, destination_city, departure_date):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM flight_info 
            WHERE LOWER(source_city) = LOWER(%s) 
            AND LOWER(destination_city) = LOWER(%s)
        """, (source_city, destination_city))
        flights = cursor.fetchall()
        try:
            selected_date = datetime.strptime(
                departure_date,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            selected_date = datetime.strptime(
                departure_date,
                "%d-%m-%Y"
            ).date()
        today = date.today()
        if selected_date == today:
            current_time = datetime.now()
            current_seconds = (
                current_time.hour * 3600
                + current_time.minute * 60
                + current_time.second
            )
            filtered_flights = []
            for flight in flights:
                depart_time = flight["depart_time"]
                if hasattr(depart_time, "total_seconds"):
                    departure_seconds = depart_time.total_seconds()
                else:
                    departure_seconds = (
                        depart_time.hour * 3600
                        + depart_time.minute * 60
                        + depart_time.second
                    )
                if departure_seconds > current_seconds:
                    filtered_flights.append(flight)
            flights = filtered_flights
        elif selected_date < today:
            flights = []
        return flights
    except Exception as e:
        messagebox.showerror("Database Error", f"{e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
def show_flight_results():
    flights = fetch_flights(source_city, destination_city, departure_date)
    root = tk.Tk()
    root.title("Available Flights")
    root.geometry("650x700")
    root.configure(bg="#D0E6F5")
    top_bar = tk.Frame(
        root,
        bg="#D0E6F5"
    )
    top_bar.pack(
        fill="x",
        pady=(10, 0),
        padx=0
    )
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
    def go_back():
        root.destroy()
        path = os.path.join(os.path.dirname(__file__), "flight_search.py")
        subprocess.Popen([
            sys.executable,
            path,
            user_email  
        ])
    def handle_select_flight(flight_data):
        source = flight_data["source_city"]
        destination = flight_data["destination_city"]
        domestic_cities = [
            "Delhi", "Mumbai", "Bengaluru", "Chennai",
            "Kolkata", "Hyderabad", "Ahmedabad", "Pune"
        ]
        if (
            source.lower() in [city.lower() for city in domestic_cities]
            and destination.lower() in [city.lower() for city in domestic_cities]
        ):
            path = os.path.join(
                os.path.dirname(__file__),
                "domestic_passenger_details.py"
            )
        else:
            path = os.path.join(
                os.path.dirname(__file__),
                "international_passenger_details.py"
            )
        flight_id = flight_data["id"]
        flight_price = float(flight_data["price"])
        root.destroy()
        subprocess.Popen([
            sys.executable,
            path,
            str(num_passengers),
            user_email,
            str(flight_id),
            str(flight_price)
        ])
    tk.Label(
        root, 
        text="Available Flights",
        font=("Helvetica", 26, "bold"),
        bg="#D0E6F5",
        fg="#0A3D62"
        ).pack(pady=(20, 5))
    tk.Label(
        root, 
        text="Select the best flights for your journey.",
        font=("Helvetica", 14),
        bg="#D0E6F5", 
        fg="#555555"
        ).pack(pady=(0, 20))
    canvas = tk.Canvas(
        root, 
        bg="#D0E6F5", 
        highlightthickness=0
        )
    scrollbar = tk.Scrollbar(
        root, 
        orient="vertical", 
        command=canvas.yview
        )
    frame = tk.Frame(
        canvas, 
        bg="#D0E6F5"
        )
    frame.bind(
        "<Configure>", 
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
    frame_window = canvas.create_window(
        (0, 0), 
        window=frame, 
        anchor="nw"
        )
    def resize_frame(event):
        canvas.itemconfig(
            frame_window,
            width=event.width
        )
    canvas.bind("<Configure>",resize_frame)
    canvas.configure(
        yscrollcommand=scrollbar.set
        )
    canvas.pack(
        side="left", 
        fill="both", 
        expand=True
        )
    scrollbar.pack(
        side="right", 
        fill="y"
        )
    if not flights:
        tk.Label(frame, text="No flights found.",
                 font=("Helvetica", 14),
                 bg="#D0E6F5", fg="red").pack(pady=20)
    else:
        for flight in flights:
            box = tk.Frame(frame, bd=1, relief="solid", padx=10, pady=10, bg="#D0E6F5")
            box.pack(fill="x", pady=10, padx=20)
            for i in range(5):
                box.grid_columnconfigure(i, weight=1)
            def format_time(t):
                try:
                    return t.strftime("%H:%M")
                except(AttributeError, ValueError):
                    return str(t)
            departure = format_time(flight['depart_time'])
            arrival = format_time(flight['arrival_time'])
            total_price = flight['price'] * num_passengers
            tk.Label(box, text=flight['flight_name'],
                     font=("Helvetica", 11, "bold"),
                     bg="#D0E6F5").grid(row=0, column=0, sticky="w")
            tk.Label(box, text=departure,
                     font=("Helvetica", 12, "bold"),
                     bg="#D0E6F5").grid(row=0, column=1)
            tk.Label(box, text=arrival,
                     font=("Helvetica", 12, "bold"),
                     bg="#D0E6F5").grid(row=0, column=3)
            tk.Label(box, text=f"₹{total_price:,.2f}",
                     font=("Helvetica", 16, "bold"),
                     fg="blue", bg="#D0E6F5").grid(row=0, column=4)
            tk.Label(box, text=f"Flight No: {flight['flight_number']}",
                     bg="#D0E6F5").grid(row=1, column=0, sticky="w")
            tk.Label(box, text=flight['source_city'],
                     bg="#D0E6F5").grid(row=2, column=1)
            tk.Label(box, text=flight['destination_city'],
                     bg="#D0E6F5").grid(row=2, column=3)
            tk.Label(box, text=flight['duration'],
                     bg="#D0E6F5").grid(row=1, column=2)
            tk.Label(box, text=flight['flight_type'],
                     bg="#D0E6F5").grid(row=2, column=0, sticky="w")
            tk.Label(box, text=f"{num_passengers} passenger(s)",
                     font=("Helvetica", 8),
                     bg="#D0E6F5").grid(row=2, column=4)
            tk.Button(
                box,
                text="Select Flight",
                bg="#0D2E91",
                fg="white",
                activebackground="#09246F",
                activeforeground="white",
                font=("Arial",11,"bold"),
                width=15,
                height=2,
                bd=0,
                relief="flat",
                cursor="hand2",
                command=lambda f=flight: handle_select_flight(f)
            ).grid(
                row=3, 
                column=4, 
                pady=10,
                padx=5
                )
    tk.Button(
        frame,
        text="Back to Search",
        command=go_back,
        bg="#4682B4",
        fg="white",
        activebackground="#315F7D",
        activeforeground="white",
        font=("Arial", 11, "bold"),
        width=18,
        height=2,
        bd=0,
        relief="flat",
        cursor="hand2"
    ).pack(pady=30)
    root.mainloop()
show_flight_results()