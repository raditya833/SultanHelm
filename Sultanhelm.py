import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Sultan Helm",
    page_icon=":helmet_with_white_cross:",
    layout="wide",
    initial_sidebar_state="expanded", 
)
# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')
conn.commit()

# Function to check username and password
def check_credentials(username, password):
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    if user:
        return True
    return False

# Function to add a new user to the database
def register_user(username, password):
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# Function to display the login page
def login_page():
    st.title("Login Page")

    # Input fields for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Login button
    if st.button("Login"):
        if check_credentials(username, password):
            st.success("Login successful!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
        else:
            st.error("Invalid username or password")

    st.write("Don't have an account? Register below.")
    if st.button("Go to Register"):
        st.session_state['register'] = True

# Function to display the registration page
def register_page():
    st.title("Register Page")

    # Input fields for new username and password
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")

    # Register button
    if st.button("Register"):
        if register_user(new_username, new_password):
            st.success("Registration successful! Please log in.")
            st.session_state['register'] = False
        else:
            st.error("Username already exists. Please choose a different username.")

    if st.button("Back to Login"):
        st.session_state['register'] = False

# Fungsi untuk membuat atau menghubungkan database
def connect_database():
    conn = sqlite3.connect('transactions.db')  # Nama database: transactions.db
    c = conn.cursor()
    # Buat tabel transactions jika belum ada
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, transaction_date TEXT, description TEXT,
                 debit_account TEXT, debit_amount REAL, credit_account TEXT, credit_amount REAL)''')
    # Buat tabel inventory jika belum ada
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY, item_name TEXT, quantity INTEGER, price REAL)''')
    conn.commit()
    conn.close()

# Fungsi untuk menyimpan transaksi ke dalam database
def save_transaction(transaction_date, description, debit_account, debit_amount, credit_account, credit_amount):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute('''INSERT INTO transactions (transaction_date, description, debit_account, debit_amount, credit_account, credit_amount)
                 VALUES (?, ?, ?, ?, ?, ?)''', (transaction_date, description, debit_account, debit_amount, credit_account, credit_amount))
    conn.commit()
    conn.close()

# Fungsi untuk menghapus transaksi dari database
def delete_transaction(transaction_id):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

# Fungsi untuk menampilkan jurnal umum dari database
def show_general_ledger():
    conn = sqlite3.connect('transactions.db')
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    st.title("Jurnal Umum")
    st.write(df)

    # Input teks untuk menghapus transaksi berdasarkan ID
    transaction_id = st.text_input("Enter Transaction ID to Delete")

    # Tombol untuk menghapus transaksi
    if st.button("Delete"):
        if transaction_id.strip() == "":
            st.warning("Please enter a valid transaction ID.")
        else:
            try:
                transaction_id = int(transaction_id)
                delete_transaction(transaction_id)
                st.success(f"Transaction {transaction_id} deleted successfully!")
                st.experimental_rerun()
            except ValueError:
                st.error("Invalid transaction ID. Please enter a valid integer ID.")

    # Menghitung saldo akun
    account_balances = calculate_account_balance()

    # Menampilkan buku besar sebagai tabel
    st.title("Neraca Saldo")

    # Buat DataFrame untuk tabel neraca saldo
    ledger_table = pd.DataFrame(list(account_balances.items()), columns=['Account', 'Balance'])

    # Hitung total saldo dari semua akun
    total_balance = sum(account_balances.values())

    # Menambahkan total saldo ke dalam tabel buku besar
    ledger_table.loc[len(ledger_table)] = ['Total', total_balance]

    # Format balance tanpa tambahan nol dan dengan koma setiap 3 digit
    ledger_table['Balance'] = ledger_table['Balance'].apply(lambda x: f"{x:,.2f}".rstrip('0').rstrip('.'))

    st.table(ledger_table)

    # Menampilkan neraca saldo dengan rincian akun debit dan kredit
    trial_balance_df = calculate_trial_balance()
    st.title("Buku Besar")
    st.write(trial_balance_df)

def show_home():
    st.title("About Us")
    st.write("Selamat datang di Sultan Helm, destinasi utama bagi para pecinta sepeda motor yang mengutamakan keselamatan, kenyamanan, dan gaya dalam berkendara. Kami adalah toko helm terpercaya yang berdedikasi untuk menyediakan helm berkualitas tinggi dengan desain terkini dan fitur keselamatan terbaik")
    st.write("Dengan pengalaman bertahun-tahun di industri otomotif, kami memahami pentingnya perlindungan kepala saat berkendara. Oleh karena itu, kami hanya bekerja sama dengan merek helm ternama dan teruji, untuk memastikan setiap produk yang kami tawarkan memenuhi standar keamanan internasional.")
    st.write("Di Sultan Helm, kami tidak hanya fokus pada keamanan, tetapi juga kenyamanan dan gaya. Kami memiliki berbagai macam helm, mulai dari helm full-face, half-face, modular, hingga helm retro dan klasik, yang dirancang untuk berbagai jenis pengendara dan preferensi.")

def show_menu_list():
    st.title("Catalog Product")
    st.write("Here are some catalog product that we provide:")
    st.write("- Hijab Cargloss   190K")
    st.write("- Cargloss KW      195K")
    st.write("- Day              230K")
    st.write("- KYT DJ Maru      335K")
    st.write("- Classic GTX      160K")
    st.write("- VOG Extreme      250K")
    st.write("- Classic Baru     125K")
    st.write("- HRV              185K")
    st.write("- JS               295K")
    st.write("- Leopard          240K")
    st.write("- Kaca Cembung      50K")
    st.write("- Kanebo            22K")
    st.write("- Pet Polos         20K")
    st.write("- Kaca Injak Orange 60K")
    st.write("- Kaca Injak Pink   50K")
    st.write("- Pengait           10K")
    st.write("- Baut               5K")
    st.write("- Plastic JC        15K")
    st.write("- Reflecta JC       80K")
    st.write("- Kaca Cencen       35K")
    st.write("- Kaca Vitano       50K")
    st.write("- Cencen Vitano     70K")
    

def show_contact():
    st.title("Contact Us")
    st.write("Address: Jl. Taman Siswa No.10, RT.1/RW.2, Sekaran, Kec. Gn. Pati, Kota Semarang, Jawa Tengah 50229")
    st.write("Email: sultanhelm@gmail.com")
    st.write("Phone: +628123456789")

def show_transaction():
    st.title("Transaction")
    show_transaction_form()

def show_transaction_form():
    st.subheader("Enter Transaction Details")

    # Buat input form untuk detail transaksi
    transaction_date = st.date_input("Transaction Date", value=pd.Timestamp.now().date())
    description = st.text_input("Description")
    debit_account = st.text_input("Debit Account")
    debit_amount = st.number_input("Debit Amount", min_value=0.0)
    credit_account = st.text_input("Credit Account")
    credit_amount = st.number_input("Credit Amount", min_value=0.0)

    if st.button("Submit"):
        # Proses penyimpanan transaksi ke dalam jurnal umum atau basis data lainnya
        save_transaction(transaction_date, description, debit_account, debit_amount, credit_account, credit_amount)
        st.success("Transaction recorded successfully!")

def calculate_account_balance():
    conn = sqlite3.connect('transactions.db')
    df = pd.read_sql_query("SELECT debit_account, SUM(debit_amount) AS total_debit, \
                            credit_account, SUM(credit_amount) AS total_credit \
                            FROM transactions \
                            GROUP BY debit_account, credit_account", conn)
    conn.close()

    # Menggabungkan debet dan kredit berdasarkan akun
    account_balances = {}
    for index, row in df.iterrows():
        debit_account = row['debit_account']
        credit_account = row['credit_account']
        total_debit = row['total_debit']
        total_credit = row['total_credit']

        if debit_account not in account_balances:
            account_balances[debit_account] = 0
        if credit_account not in account_balances:
            account_balances[credit_account] = 0

        account_balances[debit_account] += total_debit
        account_balances[credit_account] -= total_credit

    return account_balances

def calculate_trial_balance():
    conn = sqlite3.connect('transactions.db')
    df_debit = pd.read_sql_query("SELECT debit_account, SUM(debit_amount) AS total_debit FROM transactions GROUP BY debit_account", conn)
    df_credit = pd.read_sql_query("SELECT credit_account, SUM(credit_amount) AS total_credit FROM transactions GROUP BY credit_account", conn)
    conn.close()

    # Gabungkan dataframe debit dan kredit
    trial_balance_df = pd.merge(df_debit, df_credit, left_on='debit_account', right_on='credit_account', how='outer')

    # Ubah nilai NaN menjadi 0
    trial_balance_df = trial_balance_df.fillna(0)

    # Hitung saldo akhir untuk setiap akun
    trial_balance_df['Balance'] = trial_balance_df['total_debit'] - trial_balance_df['total_credit']

    # Format balance tanpa tambahan nol dan dengan koma setiap 3 digit
    trial_balance_df['Balance'] = trial_balance_df['Balance'].apply(lambda x: f"{x:,.2f}".rstrip('0').rstrip('.'))

    return trial_balance_df

def calculate_profit_and_loss():
    conn = sqlite3.connect('transactions.db')

    # Menghitung total penjualan
    df_sales = pd.read_sql_query("SELECT SUM(credit_amount) AS total_sales FROM transactions WHERE credit_account = 'Penjualan'", conn)
    total_sales = df_sales['total_sales'][0] if not pd.isnull(df_sales['total_sales'][0]) else 0.0

    # Menghitung total pendapatan lainnya (jika ada)
    df_other_income = pd.read_sql_query("SELECT SUM(credit_amount) AS total_income FROM transactions WHERE credit_account = 'Pendapatan'", conn)
    total_other_income = df_other_income['total_income'][0] if not pd.isnull(df_other_income['total_income'][0]) else 0.0

    total_income = total_sales + total_other_income

    # Menghitung total biaya
    df_expenses = pd.read_sql_query("SELECT SUM(debit_amount) AS total_expenses FROM transactions WHERE debit_account = 'Biaya'", conn)
    total_expenses = df_expenses['total_expenses'][0] if not pd.isnull(df_expenses['total_expenses'][0]) else 0.0

    # Menghitung total pembelian
    df_purchases = pd.read_sql_query("SELECT SUM(debit_amount) AS total_purchases FROM transactions WHERE debit_account = 'Pembelian'", conn)
    total_purchases = df_purchases['total_purchases'][0] if not pd.isnull(df_purchases['total_purchases'][0]) else 0.0

    conn.close()

    return total_income, total_expenses, total_purchases

def show_profit_and_loss():
    st.title("Laporan Laba Rugi")

    total_income, total_expenses, total_purchases = calculate_profit_and_loss()
    net_profit = total_income - total_expenses - total_purchases

    # Buat dataframe untuk menampilkan laporan laba rugi dalam tabel
    profit_loss_df = pd.DataFrame({
        "Account": ["Pendapatan", "Biaya", "Pembelian", "Laba Bersih"],
        "Amount": [total_income, total_expenses, total_purchases, net_profit]
    })

    # Format amount tanpa tambahan nol dan dengan koma setiap 3 digit
    profit_loss_df['Amount'] = profit_loss_df['Amount'].apply(lambda x: f"{x:,.2f}".rstrip('0').rstrip('.'))

    # Tampilkan tabel laporan laba rugi
    st.table(profit_loss_df)

def show_inventory():
    st.title("Inventory Management")

    # Tampilkan daftar item persediaan dari database
    conn = sqlite3.connect('transactions.db')
    inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()

    if 'date' in inventory_df.columns:
        inventory_df['date'] = pd.to_datetime(inventory_df['date']).dt.strftime('%Y-%m-%d')

    st.write(inventory_df)

    # Input teks untuk menghapus item berdasarkan ID
    item_id = st.text_input("Enter Item ID to Delete")
    if st.button("Delete"):
        if item_id.strip() == "":
            st.warning("Please enter a valid item ID.")
        else:
            try:
                item_id = int(item_id)
                delete_inventory_item(item_id)
                st.success(f"Item {item_id} deleted successfully!")
                st.experimental_rerun()
            except ValueError:
                st.error("Invalid item ID. Please enter a valid integer ID.")
                
def update_inventory_table():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(inventory)")
    columns = [column[1] for column in c.fetchall()]
    if 'date' not in columns:
        c.execute("ALTER TABLE inventory ADD COLUMN date TEXT")
    conn.commit()
    conn.close()

def delete_inventory_item(item_id):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def add_inventory_item():
    st.title("Add New Inventory Item")

    # Form input untuk menambah item
    item_name = st.text_input("Item Name")
    item_quantity = st.number_input("Quantity", min_value=0)
    item_price = st.number_input("Price", min_value=0.0)
    item_date = st.date_input("Date", value=pd.Timestamp.now().date())

    if st.button("Add Item"):
        # Simpan item baru ke database
        conn = sqlite3.connect('transactions.db')
        c = conn.cursor()
        c.execute("INSERT INTO inventory (item_name, quantity, price, date) VALUES (?, ?, ?, ?)",
                  (item_name, item_quantity, item_price, item_date))
        conn.commit()
        conn.close()

        # Tambahkan transaksi pembelian ke jurnal umum
        purchase_description = f"Purchase {item_quantity} units of {item_name}"
        total_amount = item_quantity * item_price
        save_transaction(item_date, purchase_description, "Pembelian", total_amount, "Kas", total_amount)

        st.success("Item added and transaction recorded successfully!")

def sell_item():
    st.title("Sell Item from Inventory")

    # Pilihan untuk menjual item
    conn = sqlite3.connect('transactions.db')
    inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()

    if inventory_df.empty:
        st.warning("No items available in inventory.")
        return

    item_options = inventory_df['item_name'].tolist()
    selected_item = st.selectbox("Select Item to Sell", item_options)

    # Dapatkan stok item yang dipilih
    item_stock = inventory_df[inventory_df['item_name'] == selected_item]['quantity'].values[0]

    selling_price = st.number_input("Selling Price per Unit", min_value=0.0)
    quantity_to_sell = st.number_input(
        "Quantity to Sell",
        min_value=0,
        max_value=int(item_stock),  # Pastikan jumlah tidak lebih dari stok tersedia
        step=1
    )
    sell_date = st.date_input("Date", value=pd.Timestamp.now().date(), key="sell_date")


    if st.button("Sell Item"):
        if quantity_to_sell == 0:
            st.warning("Please select a quantity greater than 0.")
        else:
            # Kurangi jumlah stok dari persediaan
            conn = sqlite3.connect('transactions.db')
            c = conn.cursor()

            try:
                # Update inventory untuk mengurangi stok
                c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?", (quantity_to_sell, selected_item))
                conn.commit()

                # Tambahkan transaksi penjualan ke jurnal umum
                sell_description = f"Selling {quantity_to_sell} units of {selected_item}"
                total_amount = quantity_to_sell * selling_price
                save_transaction(sell_date, sell_description, "Kas", total_amount, "Penjualan", total_amount)

                st.success(f"Item '{selected_item}' sold successfully!")
            except sqlite3.Error as e:
                st.error(f"Error processing sale: {e}")
            finally:
                conn.close()

def main():
    connect_database()  # Panggil fungsi untuk membuat/hubungkan database

    st.title("Sultan Helm")

    # Logika navigasi login dan logout
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'register' not in st.session_state:
        st.session_state['register'] = False

    if st.session_state['logged_in']:
        nav_option = st.sidebar.radio("Navigation", ["Home", "Catalog Product", "Inventory", "Transaction", "General Ledger", "Profit and Loss", "Contact", "Logout"])

        if nav_option == "Home":
            show_home()
        elif nav_option == "Catalog Product":
            show_menu_list()
        elif nav_option == "Inventory":
            show_inventory()
            add_inventory_item()
            sell_item()
        elif nav_option == "Transaction":
            show_transaction()
        elif nav_option == "General Ledger":
            show_general_ledger()
        elif nav_option == "Profit and Loss":
            show_profit_and_loss()
        elif nav_option == "Contact":
            show_contact()
        elif nav_option == "Logout":
            if st.button("Confirm Logout"):
                st.session_state['logged_in'] = False
                st.sidebar.write("You have been logged out.")
                login_page()
            elif st.button("Cancel"):
                st.sidebar.write("Logout cancelled.")

    else:
        if st.session_state['register']:
            register_page()
        else:
            login_page()

if __name__ == "__main__":
    main()
