import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
from hashlib import sha256
from datetime import datetime

# -------------------- DATABASE --------------------
conn = sqlite3.connect("inventory.db", check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    quantity INTEGER,
    price REAL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    staff_name TEXT,
    quantity INTEGER,
    total REAL,
    date TEXT,
    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")
conn.commit()


# -------------------- UTILS --------------------
def hash_password(password):
    return sha256(password.encode()).hexdigest()

def create_user(username, password, role):
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, hash_password(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    return c.fetchone()

def add_product(name, qty, price):
    try:
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_products():
    c.execute("SELECT * FROM products")
    return c.fetchall()

def delete_product(pid):
    c.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()

def update_product(pid, qty, price):
    c.execute("UPDATE products SET quantity=?, price=? WHERE id=?", (qty, price, pid))
    conn.commit()

def record_sale(product_id, staff_name, qty):
    c.execute("SELECT quantity, price FROM products WHERE id=?", (product_id,))
    product = c.fetchone()
    if not product:
        return "Product not found"
    current_qty, price = product
    if qty > current_qty:
        return "Not enough stock"

    total = qty * price
    new_qty = current_qty - qty

    # Update stock
    c.execute("UPDATE products SET quantity=? WHERE id=?", (new_qty, product_id))

    # Record sale
    c.execute("INSERT INTO sales (product_id, staff_name, quantity, total, date) VALUES (?, ?, ?, ?, ?)",
              (product_id, staff_name, qty, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    return "Sale recorded successfully!"

def get_all_sales():
    c.execute("""
        SELECT sales.id, products.name, sales.staff_name, sales.quantity, sales.total, sales.date
        FROM sales
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.date DESC
    """)
    return c.fetchall()

def get_sales_summary():
    c.execute("SELECT SUM(total), SUM(quantity), COUNT(*) FROM sales")
    result = c.fetchone()
    total_revenue = result[0] if result[0] else 0
    total_qty = result[1] if result[1] else 0
    total_txn = result[2] if result[2] else 0
    return total_revenue, total_qty, total_txn


# -------------------- UI COMPONENTS --------------------
def signup():
    st.subheader("Create Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Admin", "Staff"])
    if st.button("Sign Up"):
        if create_user(username, password, role):
            st.success("Account created successfully!")
        else:
            st.error("Username already exists.")


def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state["user"] = user
            st.success(f"Welcome {user[1]} ({user[3]})")
            st.rerun()
        else:
            st.error("Invalid username or password.")


def admin_dashboard():
    st.subheader("📊 Admin Dashboard - Inventory & Sales Overview")

    # --- Summary Metrics ---
    total_revenue, total_qty, total_txn = get_sales_summary()
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Revenue", f"₹{total_revenue:,.2f}")
    col2.metric("📦 Items Sold", f"{total_qty}")
    col3.metric("🧾 Total Transactions", f"{total_txn}")

    st.write("---")

    # --- Product Chart ---
    products = get_all_products()
    if products:
        names = [p[1] for p in products]
        quantities = [p[2] for p in products]

        fig, ax = plt.subplots()
        ax.bar(names, quantities)
        plt.xticks(rotation=45)
        plt.title("Current Stock Levels")
        st.pyplot(fig)

        # --- Product Table ---
        st.write("### 🧾 List of All Products")
        st.table(
            [{"Product ID": p[0], "Name": p[1], "Quantity": p[2], "Price": f"₹{p[3]:.2f}"} for p in products]
        )
    else:
        st.info("No products in inventory yet.")

    # --- Sales Table ---
    st.write("---")
    st.write("### 💰 Recent Sales Transactions")
    sales = get_all_sales()
    if sales:
        st.table(
            [{
                "Sale ID": s[0],
                "Product": s[1],
                "Staff": s[2],
                "Qty": s[3],
                "Total": f"₹{s[4]:.2f}",
                "Date": s[5]
            } for s in sales]
        )
    else:
        st.info("No sales recorded yet.")


def staff_dashboard():
    st.subheader("📦 Staff Dashboard - Stock Overview")

    products = get_all_products()
    if products:
        st.table(
            [{"Product": p[1], "Quantity": p[2], "Price": f"₹{p[3]:.2f}"} for p in products]
        )
    else:
        st.info("No products available.")


def admin_products():
    st.subheader("🧰 Product Management (Admin Only)")

    # --- Add Product Section ---
    name = st.text_input("Product Name")
    qty_str = st.text_input("Quantity")
    price_str = st.text_input("Price")

    if st.button("Add Product"):
        if not qty_str or not price_str:
            st.error("Please enter quantity and price.")
        elif not qty_str.isdigit() or not price_str.replace('.', '', 1).isdigit():
            st.error("Quantity and Price must be numeric.")
        else:
            qty = int(qty_str)
            price = float(price_str)
            if add_product(name, qty, price):
                st.success("Product added successfully!")
                st.rerun()
            else:
                st.error("Product already exists.")

    st.write("---")
    st.write("### Existing Products")

    # --- Existing Product List ---
    products = get_all_products()
    if products:
        for p in products:
            st.write(f"**{p[1]}** — Qty: {p[2]} | Price: ₹{p[3]:.2f}")
            col1, col2, _ = st.columns([1, 1, 3])
            with col1:
                if st.button(f"Delete {p[1]}", key=f"del_{p[0]}"):
                    delete_product(p[0])
                    st.success("Deleted!")
                    st.rerun()
            with col2:
                new_qty_str = st.text_input(f"New Qty for {p[1]}", value=str(p[2]), key=f"qty_{p[0]}")
                new_price_str = st.text_input(f"New Price for {p[1]}", value=str(p[3]), key=f"price_{p[0]}")
                if st.button(f"Update {p[1]}", key=f"upd_{p[0]}"):
                    if not new_qty_str or not new_price_str:
                        st.error("Please enter both fields.")
                    elif not new_qty_str.isdigit() or not new_price_str.replace('.', '', 1).isdigit():
                        st.error("Invalid number format.")
                    else:
                        update_product(p[0], int(new_qty_str), float(new_price_str))
                        st.success("Updated!")
                        st.rerun()


def staff_sales(staff_name):
    st.subheader("💸 Sell Product (Staff)")

    products = get_all_products()
    if not products:
        st.info("No products to sell.")
        return

    product_dict = {p[1]: p for p in products}
    product_name = st.selectbox("Select Product", list(product_dict.keys()))
    selected = product_dict[product_name]

    st.write(f"Available stock: **{selected[2]}** | Price per unit: ₹{selected[3]:.2f}")

    qty = st.number_input("Quantity to sell", min_value=1, step=1)
    if st.button("Sell"):
        result = record_sale(selected[0], staff_name, qty)
        if "successfully" in result:
            st.success(result)
            st.rerun()
        else:
            st.error(result)


# -------------------- MAIN APP --------------------
def main():
    st.title("🏪 Inventory Management System")

    if "user" not in st.session_state:
        menu = ["Login", "Sign Up"]
    else:
        user = st.session_state["user"]
        if user[3] == "Admin":
            menu = ["Dashboard", "Products", "Logout"]
        else:
            menu = ["Dashboard", "Sell Product", "Logout"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Sign Up":
        signup()
    elif choice == "Login":
        login()
    elif choice == "Logout":
        st.session_state.pop("user", None)
        st.success("Logged out successfully!")
        st.rerun()
    elif choice == "Dashboard":
        user = st.session_state.get("user")
        if user:
            if user[3] == "Admin":
                admin_dashboard()
            else:
                staff_dashboard()
        else:
            st.error("Please login first.")
    elif choice == "Products":
        user = st.session_state.get("user")
        if user and user[3] == "Admin":
            admin_products()
        else:
            st.error("Access denied.")
    elif choice == "Sell Product":
        user = st.session_state.get("user")
        if user and user[3] == "Staff":
            staff_sales(user[1])
        else:
            st.error("Access denied.")


if __name__ == "__main__":
    main()