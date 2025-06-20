import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
import datetime

# Initialize the database
def init_db():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity_sold INTEGER,
        date TEXT,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )''')
    conn.commit()
    conn.close()

# User registration and login
def register_user(username, password):
    try:
        conn = sqlite3.connect("inventory.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def authenticate_user(username, password):
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()
    return user is not None

# Product-related functions
def add_product(name, quantity, price):
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def update_product(product_id, name, quantity, price):
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?", (name, quantity, price, product_id))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows

# Sales functions
def record_sale(product_id, quantity):
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM products WHERE id=?", (product_id,))
    current_quantity = cur.fetchone()
    if not current_quantity or current_quantity[0] < quantity:
        conn.close()
        return False
    cur.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, product_id))
    cur.execute("INSERT INTO sales (product_id, quantity_sold, date) VALUES (?, ?, ?)", (product_id, quantity, datetime.date.today().isoformat()))
    conn.commit()
    conn.close()
    return True

def get_sales_summary():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name, 
               SUM(s.quantity_sold), 
               SUM(s.quantity_sold * p.price)
        FROM sales s 
        JOIN products p ON s.product_id = p.id 
        GROUP BY p.name
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_low_stock(threshold=5):
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE quantity < ?", (threshold,))
    rows = cur.fetchall()
    conn.close()
    return rows

# GUI Classes
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Dashboard")
        self.root.configure(bg='#ffffff')
        self.frame = tk.Frame(self.root, bg='#ffffff')
        self.frame.pack(padx=10, pady=10)

        tk.Label(self.frame, text="Inventory Management System", font=("Arial", 16, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=6, pady=10)

        tk.Button(self.frame, text="Add Product", bg="#4CAF50", fg="white", command=self.add_product_popup).grid(row=1, column=0, padx=5)
        tk.Button(self.frame, text="Delete Product", bg="#f44336", fg="white", command=self.delete_product_popup).grid(row=1, column=1, padx=5)
        tk.Button(self.frame, text="Update Product", bg="#FFC107", fg="black", command=self.update_product_popup).grid(row=1, column=2, padx=5)
        tk.Button(self.frame, text="Record Sale", bg="#2196F3", fg="white", command=self.record_sale_popup).grid(row=1, column=3, padx=5)
        tk.Button(self.frame, text="Low Stock Alert", bg="#9C27B0", fg="white", command=self.show_low_stock).grid(row=1, column=4, padx=5)
        tk.Button(self.frame, text="Sales Summary", bg="#009688", fg="white", command=self.show_sales_summary).grid(row=1, column=5, padx=5)

        self.product_tree = ttk.Treeview(self.frame, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        for col in ("ID", "Name", "Quantity", "Price"):
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, anchor=tk.CENTER)
        self.product_tree.grid(row=2, column=0, columnspan=6, pady=10)

        self.refresh_product_list()

    def refresh_product_list(self):
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        for product in get_products():
            tag = "low" if product[2] < 5 else "normal"
            self.product_tree.insert("", tk.END, values=product, tags=(tag,))
        self.product_tree.tag_configure("low", background="#FFCDD2")

    def add_product_popup(self):
        self.product_form_popup("Add New Product", add_product)

    def update_product_popup(self):
        selected = self.product_tree.focus()
        if not selected:
            messagebox.showwarning("Select Product", "Please select a product to update.")
            return
        values = self.product_tree.item(selected, 'values')
        pid = int(values[0])
        self.product_form_popup("Update Product", lambda name, qty, price: update_product(pid, name, qty, price))

    def product_form_popup(self, title, action):
        popup = tk.Toplevel(self.root)
        popup.title(title)

        tk.Label(popup, text="Product Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(popup)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(popup, text="Quantity:").grid(row=1, column=0, padx=10, pady=5)
        qty_entry = tk.Entry(popup)
        qty_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(popup, text="Price:").grid(row=2, column=0, padx=10, pady=5)
        price_entry = tk.Entry(popup)
        price_entry.grid(row=2, column=1, padx=10, pady=5)

        def submit():
            try:
                name = name_entry.get()
                qty = int(qty_entry.get())
                price = float(price_entry.get())
                if not name:
                    raise ValueError("Empty name")
                action(name, qty, price)
                self.refresh_product_list()
                popup.destroy()
            except:
                messagebox.showerror("Invalid Input", "Please fill all fields with valid data.")

        tk.Button(popup, text="Submit", command=submit, bg="#4CAF50", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

    def delete_product_popup(self):
        selected = self.product_tree.focus()
        if not selected:
            messagebox.showwarning("Select Product", "Please select a product to delete.")
            return
        pid = int(self.product_tree.item(selected, 'values')[0])
        delete_product(pid)
        self.refresh_product_list()

    def record_sale_popup(self):
        selected = self.product_tree.focus()
        if not selected:
            messagebox.showwarning("Select Product", "Please select a product to sell.")
            return
        pid = int(self.product_tree.item(selected, 'values')[0])
        qty = simpledialog.askinteger("Sale Quantity", "Enter quantity sold:")
        if qty is None:
            return
        if record_sale(pid, qty):
            messagebox.showinfo("Sale Recorded", "Sale successfully recorded.")
            self.refresh_product_list()
        else:
            messagebox.showwarning("Stock Error", "Insufficient stock for this sale.")

    def show_low_stock(self):
        items = get_low_stock()
        if not items:
            messagebox.showinfo("Low Stock", "All items are sufficiently stocked.")
        else:
            msg = "\n".join([f"{item[1]}: {item[2]} left" for item in items])
            messagebox.showwarning("Low Stock Alert", msg)

    def show_sales_summary(self):
        summary = get_sales_summary()
        if not summary:
            messagebox.showinfo("Sales Summary", "No sales recorded yet.")
        else:
            msg = "\n".join([
                f"{item[0]}: {item[1]} sold, ₹{item[2]:.2f} revenue" for item in summary
            ])
            messagebox.showinfo("Sales Report", msg)

# Login window
class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("300x200")

        tk.Label(master, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(master)
        self.username_entry.pack(pady=5)

        tk.Label(master, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(master, text="Login", bg="#2196F3", fg="white", command=self.login).pack(pady=5)
        tk.Button(master, text="Register", bg="#4CAF50", fg="white", command=self.register).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if authenticate_user(username, password):
            messagebox.showinfo("Success", "Login successful!")
            self.master.destroy()
            root = tk.Tk()
            InventoryApp(root)
            root.mainloop()
        else:
            messagebox.showerror("Failed", "Invalid username or password")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if register_user(username, password):
            messagebox.showinfo("Success", "User registered successfully!")
        else:
            messagebox.showerror("Failed", "Registration failed. Username may already exist.")

# Run the app
if __name__ == '__main__':
    init_db()
    login_root = tk.Tk()
    LoginWindow(login_root)
    login_root.mainloop()
