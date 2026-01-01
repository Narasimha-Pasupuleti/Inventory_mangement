🏪 Inventory Management System

A simple yet powerful Inventory Management System built using Python, SQLite, and Streamlit.
It supports Admin and Staff roles with distinct permissions for managing and selling products.


---

📋 Features

👑 Admin Features

User Role Management: Admin and Staff roles with separate permissions

Add, Update, Delete Products

View Dashboard:

📊 Bar chart of current stock levels

🧾 List of all products

💰 Recent sales transactions

💵 Sales Summary (Total Revenue, Items Sold, Transactions)


View Real-time Inventory and Sales Data


👷 Staff Features

View Available Products and Stock

Sell Products (quantity automatically deducted from stock)

Track Transactions Automatically


💾 System Features

SQLite3 Database (lightweight, no setup required)

Secure Password Hashing using SHA-256

Dynamic UI with Streamlit

Real-time Updates using st.rerun()



---

🧰 Tech Stack

Component	Technology

Frontend	Streamlit
Backend	Python
Database	SQLite3
Data Visualization	Matplotlib
Security	SHA-256 Password Hashing



---

📂 Project Structure

inventory-management/
│
├── app.py                # Main Streamlit Application
├── inventory.db          # SQLite Database (auto-created)
├── README.md             # Project Documentation
└── requirements.txt      # Python Dependencies


---

⚙️ Installation & Setup

1️⃣ Clone the Repository

git clone https://github.com/yourusername/inventory-management.git
cd inventory-management

2️⃣ Create a Virtual Environment

python -m venv venv

3️⃣ Activate the Virtual Environment

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

4️⃣ Install Dependencies

Create a requirements.txt with:

streamlit
matplotlib

Then install:

pip install -r requirements.txt

5️⃣ Run the Application

streamlit run app.py


---

👨‍💻 How It Works

🔑 Authentication System

Users can Sign Up as either Admin or Staff.

Passwords are stored securely (hashed using SHA-256).

On login, the system checks credentials from the SQLite database.


🧮 Inventory Management

Admins can:

Add new products

Update product details (quantity, price)

Delete products


Staff can:

View available stock

Sell products (reduces stock automatically)

Each sale is recorded with timestamp and total value.



📊 Dashboard (Admin)

Displays:

Sales Summary:

Total revenue

Total items sold

Number of transactions


Bar Chart of stock levels

Full product list

Sales history table



---

🧾 Example Roles

Role	Username	Password	Permissions

Admin	admin	admin123	Add/Update/Delete products, View Dashboard
Staff	staff	staff123	Sell products only


(You can create these users manually on first run via Sign Up.)




🧑‍🏫 Author

Developed by: Narasimha
📧 Email: narasimhapasupuleti7730@gmail.com


---
