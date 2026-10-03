import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import os
import sys
import subprocess
from db_config import DB_CONFIG
if len(sys.argv) > 1:
    user_email = sys.argv[1].strip()
else:
    temp = tk.Tk()
    temp.withdraw()
    messagebox.showerror(
        "Error",
        "User not logged in."
    )
    temp.destroy()
    sys.exit()
def get_connection():
    return pymysql.connect(**DB_CONFIG)
def fetch_bookings():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                b.booking_id,
                b.flight_id,
                b.booking_code,
                b.source_city,
                b.destination_city,
                b.departure_date,
                b.return_date,
                b.num_passenger,
                b.total_amount,
                b.status,
                b.booked_on,
                b.payment_method,
                f.flight_name,
                f.flight_number,
                f.depart_time,
                f.arrival_time,
                f.duration,
                f.price
            FROM bookings b
            LEFT JOIN flight_info f
                ON b.flight_id = f.id
            WHERE b.email = %s
            ORDER BY b.booking_id DESC
            """,
            (user_email,)
        )
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror(
            "Database Error",
            f"Could not load your bookings.\n\n{e}"
        )
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def refresh_bookings():
    try:
        for item in booking_tree.get_children():
            booking_tree.delete(item)
        bookings = fetch_bookings()
        for booking in bookings:
            booking_id = booking["booking_id"]
            booking_code = booking["booking_code"]
            flight_id = booking["flight_id"]
            flight_number = booking["flight_number"]
            flight_name = booking["flight_name"]
            source_city = booking["source_city"]
            destination_city = booking["destination_city"]
            departure_date = booking["departure_date"]
            return_date = booking["return_date"]
            num_passenger = booking["num_passenger"]
            total_amount = booking["total_amount"]
            status = booking["status"]
            booked_on = booking["booked_on"]
            payment_method = booking["payment_method"]
            departure = (
                departure_date.strftime("%d-%m-%Y")
                if departure_date
                else "-"
            )
            return_display = (
                return_date.strftime("%d-%m-%Y")
                if return_date
                else "One Way"
            )
            booked_on_display = (
                booked_on.strftime("%d-%m-%Y %I:%M %p")
                if booked_on
                else "-"
            )
            if total_amount is not None:
                amount_display = (
                    f"₹{float(total_amount):,.2f}"
                )
            else:
                amount_display = "₹0.00"
            if flight_number:
                flight_display = flight_number
            elif flight_name:
                flight_display = flight_name
            else:
                flight_display = "N/A"
            flight_id_display = (
                str(flight_id)
                if flight_id is not None
                else "N/A"
            )
            route_display = (
                f"{source_city or '-'} → "
                f"{destination_city or '-'}"
            )
            booking_tree.insert(
                "",
                "end",
                iid=str(booking_id),
                values=(
                    booking_code or "-",
                    flight_id_display,
                    flight_display,
                    route_display,
                    departure,
                    return_display,
                    num_passenger or 0,
                    amount_display,
                    status or "-",
                    booked_on_display,
                    payment_method or "-"
                )
            )
        if bookings:
            count_label.config(
                text=f"{len(bookings)} booking"
                     f"{'s' if len(bookings) != 1 else ''}"
            )
            empty_label.config(
                text=""
            )
        else:
            count_label.config(
                text="0 bookings"
            )
            empty_label.config(
                text="You don't have any bookings yet.\n"
                     "Book a flight and it will appear here."
            )
    except Exception as e:
        messagebox.showerror(
            "Refresh Error",
            f"Could not refresh bookings.\n\n{e}"
        )
def get_selected_booking():
    selected = booking_tree.selection()
    if not selected:
        messagebox.showwarning(
            "Select Booking",
            "Please select a booking first."
        )
        return None
    booking_id = selected[0]
    values = booking_tree.item(
        booking_id,
        "values"
    )
    return booking_id, values
def cancel_booking():
    selected = get_selected_booking()
    if not selected:
        return
    booking_id, values = selected
    booking_code = values[0]
    status = values[8]
    if not status:
        messagebox.showwarning(
            "Cancellation Failed",
            "Could not determine the booking status."
        )
        return
    if status.lower() == "cancelled":
        messagebox.showinfo(
            "Already Cancelled",
            f"Booking {booking_code} is already cancelled."
        )
        return
    if status.lower() != "confirmed":
        messagebox.showwarning(
            "Cannot Cancel",
            f"Booking {booking_code} cannot be cancelled "
            f"because its current status is '{status}'."
        )
        return
    confirm = messagebox.askyesno(
        "Cancel Booking",
        f"Are you sure you want to cancel booking "
        f"{booking_code}?\n\n"
        "This action will change the booking status to Cancelled."
    )
    if not confirm:
        return
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE bookings
            SET status = 'Cancelled'
            WHERE booking_id = %s
              AND email = %s
              AND status = 'Confirmed'
            """,
            (
                booking_id,
                user_email
            )
        )
        if cursor.rowcount == 0:
            conn.rollback()
            messagebox.showwarning(
                "Cancellation Failed",
                "The booking could not be cancelled.\n\n"
                "It may already be cancelled, or it may not "
                "belong to the logged-in user."
            )
            return
        conn.commit()
        messagebox.showinfo(
            "Booking Cancelled",
            f"Booking {booking_code} has been cancelled successfully."
        )
        refresh_bookings()
    except Exception as e:
        if conn:
            conn.rollback()
        messagebox.showerror(
            "Database Error",
            f"Could not cancel the booking.\n\n{e}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def go_to_flight_search():
    try:
        script_path = os.path.join(
            os.path.dirname(__file__),
            "flight_search.py"
        )
        root.destroy()
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
root = tk.Tk()
root.title(
    "SkyNest - My Bookings"
)
root.geometry(
    "1400x800"
)
root.minsize(
    1100,
    600
)
root.configure(
    bg="#D0E6F5"
)
style = ttk.Style()
style.theme_use(
    "clam"
)
style.configure(
    "Treeview",
    font=("Arial", 10),
    rowheight=34,
    background="white",
    fieldbackground="white"
)
style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold"),
    padding=8
)
top_bar = tk.Frame(
    root,
    bg="#D0E6F5"
)
top_bar.pack(
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
        top_bar,
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
    top_bar,
    text=f"Logged in as: {user_email}",
    font=("Arial", 10),
    bg="#D0E6F5",
    fg="#555555"
).pack(
    side="right",
    padx=25
)
heading_frame = tk.Frame(
    root,
    bg="#D0E6F5"
)
heading_frame.pack(
    fill="x",
    padx=30,
    pady=(5, 10)
)
tk.Label(
    heading_frame,
    text="My Bookings",
    font=("Georgia", 30, "bold", "italic"),
    bg="#D0E6F5",
    fg="#2F4F4F"
).pack()
tk.Label(
    heading_frame,
    text="View and manage your SkyNest flight bookings",
    font=("Georgia", 14, "italic"),
    bg="#D0E6F5",
    fg="#6A5ACD"
).pack(
    pady=(5, 0)
)
count_label = tk.Label(
    root,
    text="",
    font=("Arial", 11, "bold"),
    bg="#D0E6F5",
    fg="#0D2E91"
)
count_label.pack(
    anchor="w",
    padx=35,
    pady=(10, 5)
)
table_frame = tk.Frame(
    root,
    bg="white",
    bd=1,
    relief="solid"
)
table_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(0, 5)
)
columns = (
    "booking_code",
    "flight_id",
    "flight",
    "route",
    "departure",
    "return",
    "passengers",
    "amount",
    "status",
    "booked_on",
    "payment"
)
booking_tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)
headings = {
    "booking_code": "Booking Code",
    "flight_id": "Flight ID",
    "flight": "Flight",
    "route": "Route",
    "departure": "Departure",
    "return": "Return",
    "passengers": "Passengers",
    "amount": "Amount",
    "status": "Status",
    "booked_on": "Booked On",
    "payment": "Payment"
}
widths = {
    "booking_code": 105,
    "flight_id": 75,
    "flight": 110,
    "route": 180,
    "departure": 95,
    "return": 95,
    "passengers": 85,
    "amount": 100,
    "status": 100,
    "booked_on": 150,
    "payment": 90
}
for column in columns:
    booking_tree.heading(
        column,
        text=headings[column]
    )
    booking_tree.column(
        column,
        width=widths[column],
        minwidth=70,
        anchor="center"
    )
vertical_scroll = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=booking_tree.yview
)
horizontal_scroll = ttk.Scrollbar(
    table_frame,
    orient="horizontal",
    command=booking_tree.xview
)
booking_tree.configure(
    yscrollcommand=vertical_scroll.set,
    xscrollcommand=horizontal_scroll.set
)
booking_tree.grid(
    row=0,
    column=0,
    sticky="nsew"
)
vertical_scroll.grid(
    row=0,
    column=1,
    sticky="ns"
)
horizontal_scroll.grid(
    row=1,
    column=0,
    sticky="ew"
)
table_frame.grid_rowconfigure(
    0,
    weight=1
)
table_frame.grid_columnconfigure(
    0,
    weight=1
)
empty_label = tk.Label(
    root,
    text="",
    font=("Arial", 12),
    bg="#D0E6F5",
    fg="#555555",
    justify="center"
)
empty_label.pack(
    pady=(0, 5)
)
button_frame = tk.Frame(
    root,
    bg="#D0E6F5"
)
button_frame.pack(
    pady=(10, 25)
)
tk.Button(
    button_frame,
    text="Cancel Selected Booking",
    command=cancel_booking,
    font=("Arial", 12, "bold"),
    bg="#DC3545",
    fg="white",
    activebackground="#B02A37",
    activeforeground="white",
    width=22,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2"
).grid(
    row=0,
    column=0,
    padx=10
)
tk.Button(
    button_frame,
    text="Refresh",
    command=refresh_bookings,
    font=("Arial", 12, "bold"),
    bg="#0D6EFD",
    fg="white",
    activebackground="#0B5ED7",
    activeforeground="white",
    width=15,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2"
).grid(
    row=0,
    column=1,
    padx=10
)
tk.Button(
    button_frame,
    text="Book Another Flight",
    command=go_to_flight_search,
    font=("Arial", 12, "bold"),
    bg="#0D6EFD",
    fg="white",
    activebackground="#0B5ED7",
    activeforeground="white",
    width=20,
    height=2,
    bd=0,
    relief="flat",
    cursor="hand2"
).grid(
    row=0,
    column=2,
    padx=10
)
refresh_bookings()
root.mainloop()