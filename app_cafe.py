import tkinter as tk
from tkinter import messagebox, Toplevel, Text
import sqlite3
from datetime import datetime

# ----------------- MENU -----------------
menu_items = {
    "Coffee": 50,
    "Tea": 30,
    "Sandwich": 70,
    "Burger": 90,
    "Cake": 60
}

# ----------------- DATABASE SETUP -----------------
def setup_database():
    db = sqlite3.connect("simple_pos.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            item TEXT,
            quantity INTEGER,
            price REAL
        )
    """)
    db.commit()
    db.close()

# ----------------- SAVE TO DATABASE -----------------
def save_order(order_list):
    db = sqlite3.connect("simple_pos.db")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item, qty, price in order_list:
        db.execute("INSERT INTO orders (date, item, quantity, price) VALUES (?, ?, ?, ?)",
                   (now, item, qty, price))
    db.commit()
    db.close()

# ----------------- SHOW RECEIPT -----------------
def show_receipt(order_list, subtotal, tax, total):
    receipt = "------ Receipt ------\n"
    for item, qty, price in order_list:
        receipt += f"{item} x{qty} = ₹{price:.2f}\n"
    receipt += f"\nSubtotal: ₹{subtotal:.2f}"
    receipt += f"\nTax (5%): ₹{tax:.2f}"
    receipt += f"\nTotal: ₹{total:.2f}\n"
    receipt += "---------------------"

    win = Toplevel()
    win.title("Receipt")
    txt = Text(win, width=40, height=20)
    txt.pack()
    txt.insert("1.0", receipt)

# ----------------- CALCULATE -----------------
def calculate():
    try:
        subtotal = 0
        order_list = []

        for item in menu_items:
            if var_items[item].get():
                qty = int(entry_qty[item].get())
                if qty > 0:
                    price = qty * menu_items[item]
                    subtotal += price
                    order_list.append((item, qty, price))

        tax = subtotal * 0.05
        total = subtotal + tax

        total_var.set(f"₹ {subtotal:.2f}")
        tax_var.set(f"₹ {tax:.2f}")
        final_var.set(f"₹ {total:.2f}")

        save_order(order_list)
        show_receipt(order_list, subtotal, tax, total)

    except ValueError:
        messagebox.showerror("Error", "Enter valid quantities!")

# ----------------- RESET -----------------
def reset():
    for item in menu_items:
        var_items[item].set(0)
        entry_qty[item].delete(0, tk.END)
        entry_qty[item].insert(0, "0")
        entry_qty[item].config(state='disabled')
    total_var.set("")
    tax_var.set("")
    final_var.set("")

# ----------------- ENABLE QUANTITY -----------------
def enable_qty(item):
    if var_items[item].get():
        entry_qty[item].config(state='normal')
        if entry_qty[item].get() == "0":
            entry_qty[item].delete(0, tk.END)
            entry_qty[item].insert(0, "1")
        row_frames[item].config(bg='lightgreen') 
    else:
        entry_qty[item].delete(0, tk.END)
        entry_qty[item].insert(0, "0")
        entry_qty[item].config(state='disabled')
        row_frames[item].config(bg='white')  


# ----------------- GUI SETUP -----------------
root = tk.Tk()
root.title("Simple Cafe POS")
root.geometry("400x550")

tk.Label(root, text="Cafe Menu", font=("Arial", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack()
row_frames={}
var_items = {}
entry_qty = {}

for item, price in menu_items.items():
    row = tk.Frame(frame, bg='white')  # Default background
    row.pack(pady=5, anchor='w')
    row_frames[item] = row 

    var = tk.IntVar()
    chk = tk.Checkbutton(row, text=f"{item} (₹{price})", font=("Arial", 12),
                         variable=var, command=lambda i=item: enable_qty(i))
    chk.pack(side=tk.LEFT)

    qty = tk.Entry(row, width=5, font=("Arial", 12), state='disabled', justify='center')
    qty.insert(0, "0")
    qty.pack(side=tk.RIGHT, padx=10)

    var_items[item] = var
    entry_qty[item] = qty

# Totals
total_var = tk.StringVar()
tax_var = tk.StringVar()
final_var = tk.StringVar()

tk.Label(root, text="Subtotal:", font=("Arial", 12)).pack(pady=(15,0))
tk.Label(root, textvariable=total_var, font=("Arial", 12)).pack()

tk.Label(root, text="Tax (5%):", font=("Arial", 12)).pack(pady=(10,0))
tk.Label(root, textvariable=tax_var, font=("Arial", 12)).pack()

tk.Label(root, text="Total:", font=("Arial", 12)).pack(pady=(10,0))
tk.Label(root, textvariable=final_var, font=("Arial", 12)).pack()

# Buttons
btns = tk.Frame(root)
btns.pack(pady=20)

tk.Button(btns, text="Calculate", font=("Arial", 12), command=calculate).pack(side=tk.LEFT, padx=5)
tk.Button(btns, text="Reset", font=("Arial", 12), command=reset).pack(side=tk.LEFT, padx=5)
tk.Button(btns, text="Exit", font=("Arial", 12), command=root.destroy).pack(side=tk.LEFT, padx=5)

# Run setup and app
setup_database()
root.mainloop()
