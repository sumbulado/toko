import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import messagebox, simpledialog, ttk

def initialize_database():
    conn = sqlite3.connect("kasir.db")
    cursor = conn.cursor()
    # Create table for units
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        satuan TEXT NOT NULL,
        keterangan TEXT NOT NULL
    )
    """)
    # Create table for product types
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jenis_produks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jenis_produk TEXT NOT NULL,
        keterangan TEXT NOT NULL
    )
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT,
        nama_produk TEXT,
        jenis_produk TEXT,
        keterangan TEXT,
        satuan_dasar TEXT,
        harga_pokok REAL,
        barcode TEXT
    )
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS unit_conversions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        satuan TEXT,
        konversi INTEGER,
        barcode TEXT,
        harga_pokok REAL,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS product_prices (
        product_id TEXT,
        satuan TEXT,
        jumlah_sampai INTEGER,
        harga_jual REAL,
        tipe_harga TEXT,
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )
    """)

    conn.commit()
    conn.close()

class KasirApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Kasir")
        self.root.state('zoomed')  # Atur jendela menjadi maksimal

        # Frame untuk menampung konten yang berubah
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # Menu utama
        menu = tk.Menu(root)
        root.config(menu=menu)

        # Menu
        self.transaction_menu = TransactionMenu(self.content_frame)
        self.product_menu = ProductMenu(self.content_frame)
        self.report_menu = ReportMenu(self.content_frame)

        self.settings_var = tk.StringVar()
        settings_menu = tk.Menu(menu, tearoff=0)
        settings_menu.add_command(label="Satuan", command=self.show_unit_settings)
        settings_menu.add_command(label="Jenis Produk", command=self.show_jenis_produk_settings)
        settings_menu.add_command(label="Pengaturan Lainnya", command=self.show_other_settings)

        menu.add_command(label="Transaksi", command=self.transaction_menu.show)
        menu.add_command(label="Daftar Produk", command=self.product_menu.show)
        menu.add_command(label="Laporan", command=self.report_menu.show)
        menu.add_cascade(label="Pengaturan", menu=settings_menu)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_unit_settings(self):
        self.clear_content()
        UnitSettingsMenu(self.content_frame).show()

    def show_jenis_produk_settings(self):
        self.clear_content()
        ProductTypeSettingsMenu(self.content_frame).show()

    def show_other_settings(self):
        self.clear_content()
        label = tk.Label(self.content_frame, text="Ini adalah Pengaturan Lainnya", font=("Arial", 16))
        label.pack(pady=20)

class TransactionMenu:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()  # Clear previous content
        label = tk.Label(self.parent, text="Ini adalah menu Transaksi", font=("Arial", 16))
        label.pack(pady=20)

class ProductMenu: 
    def __init__(self, parent):
        self.parent = parent
        self.produk_list = []
        self.no_product_label = None  # Store the label to show/hide it later
        self.show()  # Call show to display the products when the menu is initialized

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()  # Clear previous content

        label = tk.Label(self.parent, text="Daftar Produk", font=("Arial", 16))
        label.pack(pady=10)

        # Frame untuk daftar produk
        self.product_frame = tk.Frame(self.parent)
        self.product_frame.pack(fill=tk.BOTH, expand=True)

        # Frame untuk pencarian
        self.search_frame = tk.Frame(self.product_frame)
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_label = tk.Label(self.search_frame, text="Cari Produk:")
        self.search_label.pack(side=tk.LEFT)

        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_products)  # Bind the key release event

        # Frame untuk Treeview dan scrollbar
        self.tree_frame = tk.Frame(self.product_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        # Tabel untuk menampilkan produk
        self.tree = ttk.Treeview(self.tree_frame, columns=("Kode Produk", "Barcode", "Nama Produk", "Stok", "Satuan", "Jenis", "Harga Pokok", "Harga Jual", "Keterangan"), show="headings")
        self.tree.heading("Kode Produk", text="Kode Produk", anchor=tk.CENTER)
        self.tree.heading("Barcode", text="Barcode", anchor=tk.CENTER)
        self.tree.heading("Nama Produk", text="Nama Produk", anchor=tk.CENTER)
        self.tree.heading("Stok", text="Stok", anchor=tk.CENTER)
        self.tree.heading("Satuan", text="Satuan", anchor=tk.CENTER)
        self.tree.heading("Jenis", text="Jenis", anchor=tk.CENTER)
        self.tree.heading("Harga Pokok", text="Harga Pokok", anchor=tk.CENTER)
        self.tree.heading("Harga Jual", text="Harga Jual", anchor=tk.CENTER)
        self.tree.heading("Keterangan", text="Keterangan", anchor=tk.CENTER)

        # Set lebar kolom
        for col in self.tree["columns"]:
            self.tree.column(col, anchor=tk.CENTER, width=100)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar untuk Treeview
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Tombol untuk tambah, edit, hapus produk
        self.button_frame = tk.Frame(self.product_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.add_button = tk.Button(self.button_frame, text="Tambah Produk", command=self.add_product)
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.edit_button = tk.Button(self.button_frame, text="Edit Produk", command=self.edit_product)
        self.edit_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = tk.Button(self.button_frame, text="Hapus Produk", command=self.delete_product)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.load_products()  # Load products when displaying the menu

    def get_units(self):
        """ Fetch the list of units from the database. """
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("SELECT satuan FROM units")  # Fetch unit options
        units = cursor.fetchall()
        conn.close()
        
        return [unit[0] for unit in units]  # Return a list of unit names

    def load_products(self):
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()

        # Fetch products with their base unit information
        cursor.execute(""" 
            SELECT 
                p.product_id, 
                p.barcode, 
                p.nama_produk, 
                '0' AS stok, 
                p.satuan_dasar, 
                p.jenis_produk, 
                p.harga_pokok, 
                pp.harga_jual,  -- Get harga_jual for the base unit
                p.keterangan 
            FROM products p
            LEFT JOIN product_prices pp ON p.product_id = pp.product_id AND pp.satuan = p.satuan_dasar
        """)

        base_products = cursor.fetchall()

        # Store the products in self.produk_list for searching
        self.produk_list = base_products.copy()

        # Clear the tree view before loading
        self.tree.delete(*self.tree.get_children())

        for product in base_products:
            # Insert the base unit as the parent row
            parent_id = self.tree.insert("", tk.END, values=product)

            # Fetch other units related to this product
            cursor.execute(""" 
                SELECT 
                    uc.satuan, 
                    uc.barcode, 
                    uc.harga_pokok, 
                    pp.harga_jual 
                FROM unit_conversions uc
                LEFT JOIN product_prices pp ON uc.product_id = pp.product_id AND uc.satuan = pp.satuan
                WHERE uc.product_id = ? 
            """, (product[0],))  # Fetch related units based on the product kode

            alternative_units = cursor.fetchall()

            # Insert child rows for each alternative unit
            for unit in alternative_units:
                self.tree.insert(parent_id, tk.END, values=(
                    "",  # Empty Kode Produk for child rows
                    unit[1],  # Barcode
                    "",  # Empty Nama Produk for child rows
                    "",  # Empty Stok for child rows
                    unit[0],  # Satuan (alternative unit)
                    "",  # Empty Jenis Produk for child rows
                    unit[2],  # Harga Pokok for the alternative unit
                    unit[3],  # Harga Jual for the alternative unit
                    ""  # Empty Keterangan for child rows
                ))

        conn.close()

        if not base_products:
            # Show message if there are no products
            self.show_no_products_message("Tidak ada produk tersedia.")
        else:
            self.hide_no_products_message()

    def search_products(self, event):
        """ Search products based on input in the search entry. """
        search_text = self.search_entry.get().lower()  # Convert search text to lowercase

        # Clear the current treeview
        self.tree.delete(*self.tree.get_children())

        # Check if search text is empty to display all products
        if search_text == "":
            self.load_products()  # Reload all products if the search is empty
            return

        matched_products = []

        for product in self.produk_list:
            # Check if any of the product fields match the search text (case-insensitive)
            if (search_text in product[0].lower() or  # Kode Produk
                search_text in product[1].lower() or  # Barcode
                search_text in product[2].lower() or  # Nama Produk
                search_text in product[5].lower() or  # Jenis Produk
                (search_text in product[8].lower() if product[8] else False)):  # Keterangan

                matched_products.append(product)

        # Insert matched products into the Treeview
        for product in matched_products:
            parent_id = self.tree.insert("", tk.END, values=product)

            # Fetch and insert related units for matching products
            conn = sqlite3.connect("kasir.db")
            cursor = conn.cursor()
            cursor.execute(""" 
                SELECT 
                    uc.satuan, 
                    uc.barcode, 
                    uc.harga_pokok, 
                    pp.harga_jual 
                FROM unit_conversions uc
                LEFT JOIN product_prices pp ON uc.product_id = pp.product_id AND uc.satuan = pp.satuan
                WHERE uc.product_id = ? 
            """, (product[0],))  # Fetch related units based on the product kode

            alternative_units = cursor.fetchall()
            for unit in alternative_units:
                self.tree.insert(parent_id, tk.END, values=(
                    "",  # Empty Kode Produk for child rows
                    unit[1],  # Barcode
                    "",  # Empty Nama Produk for child rows
                    "",  # Empty Stok for child rows
                    unit[0],  # Satuan (alternative unit)
                    "",  # Empty Jenis Produk for child rows
                    unit[2],  # Harga Pokok for the alternative unit
                    unit[3],  # Harga Jual for the alternative unit
                    ""  # Empty Keterangan for child rows
                ))

            conn.close()

        if not matched_products:
            # Show message if no products match the search
            self.show_no_products_message("Tidak ada produk ditemukan.")
        else:
            # Remove any previous "no products found" message if products are displayed
            self.hide_no_products_message()

    def show_no_products_message(self, message):
        if self.no_product_label is None:
            self.no_product_label = tk.Label(self.parent, text=message, font=("Arial", 12), fg="red")
            self.no_product_label.pack(pady=20)

    def hide_no_products_message(self):
        if self.no_product_label:
            self.no_product_label.destroy()
            self.no_product_label = None  # Clear the reference
    def show_no_products_message(self, message):
        if self.no_product_label is None:
            self.no_product_label = tk.Label(self.parent, text=message, font=("Arial", 12), fg="red")
            self.no_product_label.pack(pady=20)

    def hide_no_products_message(self):
        if self.no_product_label:
            self.no_product_label.destroy()
            self.no_product_label = None  # Clear the reference

    def add_product(self):
        AddProductWindow(self.parent)

    def edit_product(self):
        selected_item = self.tree.selection()
        
        if selected_item:
            item_values = self.tree.item(selected_item[0])['values']  # Get the selected item's values
            
            # Check if the selected row is a base product or a child unit row
            if item_values[0] == "":  # If product_id is empty, it's a unit row, not a base product
                messagebox.showwarning("Peringatan", "Pilih produk utama, bukan unit alternatif!")
                return

            product_id = item_values[0]  # product_id is the first value
            
            # Open a product editing window and pass the selected product details
            EditProductWindow(self.parent, product_id, item_values)

        else:
            messagebox.showwarning("Peringatan", "Silakan pilih produk yang ingin diedit!")


    def delete_product(self):
        selected_item = self.tree.selection()
        
        if selected_item:
            item_values = self.tree.item(selected_item[0])['values']  # Get the selected item's values
            
            # Check if the selected row is a base product or a child unit row
            if item_values[0] == "":  # If product_id is empty, it's a unit row
                messagebox.showwarning("Peringatan", "Pilih produk utama, bukan unit alternatif!")
                return
            
            product_id = item_values[0]  # Get the product_id of the selected product
            
            # Confirm deletion
            confirm = messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus produk ini?")
            if confirm:
                conn = sqlite3.connect("kasir.db")
                cursor = conn.cursor()
                
                # Delete the product from the products table
                cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
                
                # Delete related unit conversions and product prices
                cursor.execute("DELETE FROM unit_conversions WHERE product_id = ?", (product_id,))
                cursor.execute("DELETE FROM product_prices WHERE product_id = ?", (product_id,))
                
                conn.commit()
                conn.close()
                
                # Remove the product from the Treeview
                self.tree.delete(selected_item)
                messagebox.showinfo("Sukses", "Produk berhasil dihapus!")
        
        else:
            messagebox.showwarning("Peringatan", "Silakan pilih produk yang ingin dihapus!")


    def update_price_based_on_unit(self, selected_unit, product_id):
        """ Update the price in the Treeview based on the selected unit """
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("SELECT harga_jual FROM product_prices WHERE product_id = ? AND satuan = ?", (product_id, selected_unit))
        price_data = cursor.fetchone()
        conn.close()

        if price_data:
            harga_jual = price_data[0]
            # Update the Treeview here based on the selected unit and product_id
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == product_id:
                    values = list(self.tree.item(item)['values'])
                    values[7] = harga_jual  # Update harga_jual column
                    self.tree.item(item, values=values)

        else:
            # Handle case where no price data is found
            print(f"No price data found for {product_id} with unit {selected_unit}.")

class ReportMenu:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()  # Clear previous content
        label = tk.Label(self.parent, text="Ini adalah menu Laporan", font=("Arial", 16))
        label.pack(pady=20)

class UnitSettingsMenu:
    def __init__(self, parent):
        self.parent = parent
        self.satuan_list = []

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()  # Clear previous content

        label = tk.Label(self.parent, text="Pengaturan Satuan", font=("Arial", 16))
        label.pack(pady=10)

        self.tree_frame = tk.Frame(self.parent)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        # Tabel untuk menampilkan satuan
        self.tree = ttk.Treeview(self.tree_frame, columns=("Satuan", "Keterangan"), show="headings", height=10)
        self.tree.heading("Satuan", text="Satuan", anchor=tk.CENTER)
        self.tree.heading("Keterangan", text="Keterangan", anchor=tk.CENTER)

        # Set lebar kolom
        self.tree.column("Satuan", anchor=tk.CENTER, width=150)
        self.tree.column("Keterangan", anchor=tk.CENTER, width=150)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar untuk Treeview
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Frame untuk input satuan
        self.input_frame = tk.Frame(self.parent)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.unit_entry = tk.Entry(self.input_frame, font=("Arial", 14))
        self.unit_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.unit_entry.insert(0, "Satuan")

        # Bind unit entry to automatic uppercase conversion
        self.unit_entry.bind("<KeyRelease>", self.capitalize_unit)

        self.description_entry = tk.Entry(self.input_frame, font=("Arial", 14))
        self.description_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.description_entry.insert(0, "Keterangan")

        # Bind description entry to capitalize each word
        self.description_entry.bind("<KeyRelease>", self.capitalize_description)

        # Tombol untuk menambah satuan
        self.add_unit_button = tk.Button(self.input_frame, text="Tambah Satuan", command=self.add_unit)
        self.add_unit_button.pack(side=tk.LEFT, padx=10)

        # Tombol untuk menghapus satuan
        self.delete_unit_button = tk.Button(self.input_frame, text="Hapus Satuan", command=self.delete_unit)
        self.delete_unit_button.pack(side=tk.LEFT, padx=10)

        # Load existing units from the database
        self.load_units_from_database()

        # Bind click event to clear selection
        self.tree.bind("<Button-1>", self.clear_selection)

    def load_units_from_database(self):
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("SELECT satuan, keterangan FROM units")
        rows = cursor.fetchall()

        for row in rows:
            self.tree.insert("", "end", values=row)  # Insert existing units into treeview

        conn.close()

    def capitalize_unit(self, event):
        """Ensure that all input in the 'Satuan' field is uppercase."""
        current_text = self.unit_entry.get()
        self.unit_entry.delete(0, tk.END)
        self.unit_entry.insert(0, current_text.upper())

    def capitalize_description(self, event):
        """Ensure that the first letter of each word in 'Keterangan' is capitalized."""
        current_text = self.description_entry.get()
        capitalized_text = " ".join(word.capitalize() for word in current_text.split())
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, capitalized_text)

    def add_unit(self):
        unit = self.unit_entry.get().strip()
        description = self.description_entry.get().strip()

        if unit and description:
            self.satuan_list.append((unit, description))
            self.tree.insert("", "end", values=(unit, description))  # Insert into treeview
            
            # Save to database
            self.save_unit_to_database(unit, description)
            
            self.unit_entry.delete(0, tk.END)  # Clear entry
            self.description_entry.delete(0, tk.END)  # Clear entry
        else:
            messagebox.showwarning("Peringatan", "Satuan dan keterangan tidak boleh kosong!")

    def save_unit_to_database(self, unit, description):
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO units (satuan, keterangan) VALUES (?, ?)", (unit, description))
        conn.commit()
        conn.close()

    def delete_unit(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item)['values']
            unit = item_values[0]
            
            # Remove from database
            self.remove_unit_from_database(unit)
            
            # Remove from treeview
            self.tree.delete(selected_item)
        else:
            messagebox.showwarning("Peringatan", "Pilih satuan yang ingin dihapus!")

    def remove_unit_from_database(self, unit):
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM units WHERE satuan=?", (unit,))
        conn.commit()
        conn.close()

    def clear_selection(self, event):
        self.tree.selection_remove(self.tree.selection())  # Clear selection


class ProductTypeSettingsMenu:
    def __init__(self, parent):
        self.parent = parent
        self.jenis_produk_list = []

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()  # Clear previous content

        label = tk.Label(self.parent, text="Pengaturan Jenis Produk", font=("Arial", 16))
        label.pack(pady=10)

        self.tree_frame = tk.Frame(self.parent)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        # Tabel untuk menampilkan jenis produk
        self.tree = ttk.Treeview(self.tree_frame, columns=("Jenis Produk", "Keterangan"), show="headings", height=10)
        self.tree.heading("Jenis Produk", text="Jenis Produk", anchor=tk.CENTER)
        self.tree.heading("Keterangan", text="Keterangan", anchor=tk.CENTER)

        # Set lebar kolom
        self.tree.column("Jenis Produk", anchor=tk.CENTER, width=150)
        self.tree.column("Keterangan", anchor=tk.CENTER, width=150)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar untuk Treeview
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Frame untuk input jenis produk
        self.input_frame = tk.Frame(self.parent)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.type_entry = tk.Entry(self.input_frame, font=("Arial", 14))
        self.type_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.type_entry.insert(0, "Jenis Produk")

        # Bind jenis produk entry to automatic uppercase conversion
        self.type_entry.bind("<KeyRelease>", self.capitalize_type)

        self.description_entry = tk.Entry(self.input_frame, font=("Arial", 14))
        self.description_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.description_entry.insert(0, "Keterangan")

        # Bind description entry to capitalize each word
        self.description_entry.bind("<KeyRelease>", self.capitalize_description)

        # Tombol untuk menambah jenis produk
        self.add_type_button = tk.Button(self.input_frame, text="Tambah Jenis Produk", command=self.add_jenis_produk)
        self.add_type_button.pack(side=tk.LEFT, padx=10)

        # Tombol untuk menghapus jenis produk
        self.delete_type_button = tk.Button(self.input_frame, text="Hapus Jenis Produk", command=self.delete_jenis_produk)
        self.delete_type_button.pack(side=tk.LEFT, padx=10)

        # Load existing product types from the database
        self.load_jenis_produks_from_database()

        # Bind click event to clear selection
        self.tree.bind("<Button-1>", self.clear_selection)

    def load_jenis_produks_from_database(self):
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("SELECT jenis_produk, keterangan FROM jenis_produks")
        rows = cursor.fetchall()

        for row in rows:
            self.tree.insert("", "end", values=row)  # Insert existing product types into treeview

        conn.close()

    def capitalize_type(self, event):
        """Ensure that all input in the 'Jenis Produk' field is uppercase."""
        current_text = self.type_entry.get()
        self.type_entry.delete(0, tk.END)
        self.type_entry.insert(0, current_text.upper())

    def capitalize_description(self, event):
        """Ensure that the first letter of each word in 'Keterangan' is capitalized."""
        current_text = self.description_entry.get()
        capitalized_text = " ".join(word.capitalize() for word in current_text.split())
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, capitalized_text)

    def add_jenis_produk(self):
        type_name = self.type_entry.get().strip()
        description = self.description_entry.get().strip()

        if type_name and description:
            self.jenis_produk_list.append((type_name, description))
            self.tree.insert("", "end", values=(type_name, description))  # Insert into treeview
            
            # Save to database
            self.save_jenis_produk_to_database(type_name, description)
            
            self.type_entry.delete(0, tk.END)  # Clear entry
            self.description_entry.delete(0, tk.END)  # Clear entry
        else:
            messagebox.showwarning("Peringatan", "Jenis produk dan keterangan tidak boleh kosong!")

    def save_jenis_produk_to_database(self, type_name, description):
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO jenis_produks (jenis_produk, keterangan) VALUES (?, ?)", (type_name, description))
        conn.commit()
        conn.close()

    def delete_jenis_produk(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item)['values']
            type_name = item_values[0]
            
            # Remove from database
            self.remove_jenis_produk_from_database(type_name)
            
            # Remove from treeview
            self.tree.delete(selected_item)
        else:
            messagebox.showwarning("Peringatan", "Pilih jenis produk yang ingin dihapus!")

    def remove_jenis_produk_from_database(self, type_name):
        conn = sqlite3.connect("kasir.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jenis_produks WHERE jenis_produk=?", (type_name,))
        conn.commit()
        conn.close()

    def clear_selection(self, event):
        self.tree.selection_remove(self.tree.selection())  # Clear selection

class AddProductWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Tambah Produk")
        
        # Koneksi ke database
        self.conn = sqlite3.connect('kasir.db')
        self.cursor = self.conn.cursor()
        
        # Inisialisasi window dan widget
        self.initialize_window()

        # Load data untuk combobox Jenis Produk dan Satuan Dasar
        self.load_jenis_produks()
        self.load_units()

    def initialize_window(self):
        # Set window size
        self.top.geometry("850x600")
        self.center_window(850, 600)

        self.canvas = tk.Canvas(self.top)
        self.scroll_y = ttk.Scrollbar(self.top, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # Frame untuk data umum
        self.general_frame = tk.LabelFrame(self.scrollable_frame, text="Data Umum", font=("Arial", 14))
        self.general_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.general_frame, text="Kode Produk").grid(row=0, column=0, padx=5, pady=5)
        self.product_id_entry = tk.Entry(self.general_frame)
        self.product_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.general_frame, text="Nama Produk").grid(row=1, column=0, padx=5, pady=5)
        self.nama_produk_entry = tk.Entry(self.general_frame)
        self.nama_produk_entry.grid(row=1, column=1, padx=5, pady=5)
        self.nama_produk_entry.bind("<FocusOut>", self.format_nama_produk)

        tk.Label(self.general_frame, text="Jenis Produk").grid(row=2, column=0, padx=5, pady=5)
        self.jenis_produk_combobox = ttk.Combobox(self.general_frame)
        self.jenis_produk_combobox.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.general_frame, text="Keterangan").grid(row=3, column=0, padx=5, pady=5)
        self.keterangan_text = tk.Text(self.general_frame, height=5, width=30)
        self.keterangan_text.grid(row=3, column=1, padx=5, pady=5)

        # Frame untuk satuan
        self.unit_frame = tk.LabelFrame(self.scrollable_frame, text="Satuan", font=("Arial", 14))
        self.unit_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.unit_frame, text="Satuan Dasar").grid(row=0, column=0, padx=5, pady=5)
        self.satuan_dasar_combobox = ttk.Combobox(self.unit_frame)
        self.satuan_dasar_combobox.grid(row=0, column=1, padx=5, pady=5)

        # Input harga pokok dan barcode
        tk.Label(self.unit_frame, text="Harga Pokok").grid(row=1, column=0, padx=5, pady=5)
        self.harga_pokok_entry = tk.Entry(self.unit_frame)
        self.harga_pokok_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.unit_frame, text="Barcode").grid(row=2, column=0, padx=5, pady=5)
        self.barcode_entry = tk.Entry(self.unit_frame)
        self.barcode_entry.grid(row=2, column=1, padx=5, pady=5)

        # Tabel konversi
        self.conversion_frame = tk.Frame(self.unit_frame)
        self.conversion_frame.grid(row=3, columnspan=2, padx=5, pady=5)

        self.conversion_tree = ttk.Treeview(self.conversion_frame, columns=("Satuan", "Konversi", "Barcode", "Harga Pokok"), show="headings")
        self.conversion_tree.heading("Satuan", text="Satuan")
        self.conversion_tree.heading("Konversi", text="Konversi")
        self.conversion_tree.heading("Barcode", text="Barcode")
        self.conversion_tree.heading("Harga Pokok", text="Harga Pokok")

        self.conversion_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.conversion_tree.bind("<Double-1>", self.on_conversion_item_select)

        self.conversion_scrollbar = ttk.Scrollbar(self.conversion_frame, orient="vertical", command=self.conversion_tree.yview)
        self.conversion_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conversion_tree.configure(yscrollcommand=self.conversion_scrollbar.set)

        # Tombol untuk menambah konversi
        self.add_conversion_button = tk.Button(self.unit_frame, text="Tambah Konversi", command=self.add_conversion)
        self.add_conversion_button.grid(row=4, columnspan=2, pady=10)

        # Tombol untuk menghitung harga pokok dasar
        self.calculate_harga_pokok_button = tk.Button(self.unit_frame, text="Hitung Harga Pokok Dasar", command=self.calculate_harga_pokok)
        self.calculate_harga_pokok_button.grid(row=5, columnspan=2, pady=10)

        # Frame untuk harga jual
        self.price_frame = tk.LabelFrame(self.scrollable_frame, text="Harga Jual", font=("Arial", 14))
        self.price_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Label untuk pilihan harga jual
        tk.Label(self.price_frame, text="Pilihan Harga Jual :").grid(row=0, column=0, padx=5, pady=5)

        # Variable untuk pilihan harga, set default to "single"
        self.price_option_var = tk.StringVar(value="single")

        # Daftar opsi harga
        price_options = [
            ("Satu Harga", "single"),
            ("Berdasarkan Jumlah", "by_amount"),
            ("Level Harga", "level"),
            ("Berdasarkan Satuan", "by_unit"),
        ]

        # Buat radio button untuk setiap opsi harga dengan anchor 'w' (west)
        for index, (text, value) in enumerate(price_options):
            radio_button = tk.Radiobutton(self.price_frame, text=text, variable=self.price_option_var, value=value, anchor='w', command=self.on_price_option_change)
            radio_button.grid(row=index + 1, column=0, padx=5, pady=5, sticky='w')

        # Frame untuk input harga (akan di-update sesuai pilihan)
        self.price_input_frame = tk.Frame(self.price_frame)
        self.price_input_frame.grid(row=len(price_options) + 1, column=0, padx=5, pady=5)


        # Tombol simpan
        self.save_button = tk.Button(self.scrollable_frame, text="Simpan", command=self.save_product)
        self.save_button.pack(pady=10)

        # Bind keyboard events for scrolling
        self.top.bind("<Up>", self.scroll_up)
        self.top.bind("<Down>", self.scroll_down)

        # Bind mouse wheel event for scrolling
        self.top.bind("<MouseWheel>", self.on_mouse_wheel)  # For Windows
        self.top.bind("<Button-4>", self.on_mouse_wheel)  # For Linux
        self.top.bind("<Button-5>", self.on_mouse_wheel)  # For Linux

    def format_nama_produk(self, event):
        # Ambil teks dari Entry dan format sesuai keinginan
        formatted_name = self.nama_produk_entry.get().title()
        self.nama_produk_entry.delete(0, tk.END)
        self.nama_produk_entry.insert(0, formatted_name)

    def on_price_option_change(self):
        # Hapus semua widget di frame input harga
        for widget in self.price_input_frame.winfo_children():
            widget.destroy()

        # Jika opsi "Satu Harga" dipilih
        if self.price_option_var.get() == "single":
            self.create_single_price_input()
        # Jika opsi "Berdasarkan Jumlah" dipilih
        elif self.price_option_var.get() == "by_amount":
            self.create_by_quantity_input()
        # Jika opsi "Level Harga" dipilih
        elif self.price_option_var.get() == "level":
            messagebox.showinfo("Opsi Belum Tersedia", "Opsi ini belum tersedia pada versi ini.")
        # Jika opsi "Berdasarkan Satuan" dipilih
        elif self.price_option_var.get() == "by_unit":
            self.create_by_unit_input()

    def create_single_price_input(self):
        # Input harga berdasarkan persentase
        tk.Label(self.price_input_frame, text="Harga (%)").grid(row=0, column=0, padx=5, pady=5)
        self.price_percentage_entry = tk.Entry(self.price_input_frame)
        self.price_percentage_entry.grid(row=0, column=1, padx=5, pady=5)

        # Input harga berdasarkan IDR
        tk.Label(self.price_input_frame, text="Harga (IDR)").grid(row=1, column=0, padx=5, pady=5)
        self.price_idr_entry = tk.Entry(self.price_input_frame)
        self.price_idr_entry.grid(row=1, column=1, padx=5, pady=5)

        # Bind perubahan input persentase dan IDR
        self.price_percentage_entry.bind("<KeyRelease>", self.update_idr_from_percentage)
        self.price_idr_entry.bind("<KeyRelease>", self.update_percentage_from_idr)

    def update_idr_from_percentage(self, event):
        try:
            harga_pokok = float(self.harga_pokok_entry.get())
            percentage = float(self.price_percentage_entry.get())
            idr_price = harga_pokok + (harga_pokok * percentage / 100)
            self.price_idr_entry.delete(0, tk.END)
            self.price_idr_entry.insert(0, f"{idr_price:.2f}")
        except ValueError:
            pass

    def update_percentage_from_idr(self, event):
        try:
            harga_pokok = float(self.harga_pokok_entry.get())
            idr_price = float(self.price_idr_entry.get())
            percentage = ((idr_price - harga_pokok) / harga_pokok) * 100
            self.price_percentage_entry.delete(0, tk.END)
            self.price_percentage_entry.insert(0, f"{percentage:.2f}")
        except ValueError:
            pass

    def create_by_quantity_input(self):
        # Tabel untuk input harga berdasarkan jumlah
        self.by_quantity_tree = ttk.Treeview(self.price_input_frame, columns=("Satuan", "Jumlah Sampai", "Harga Jual"), show="headings")
        self.by_quantity_tree.heading("Satuan", text="Satuan")
        self.by_quantity_tree.heading("Jumlah Sampai", text="Jumlah Sampai")
        self.by_quantity_tree.heading("Harga Jual", text="Harga Jual")
        self.by_quantity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Entry fields for new quantity price entry
        tk.Label(self.price_input_frame, text="Satuan").pack(side=tk.TOP, padx=5, pady=5)
        self.quantity_unit_entry = ttk.Combobox(self.price_input_frame)
        self.quantity_unit_entry['values'] = [row[0] for row in self.cursor.execute("SELECT satuan FROM units")]
        self.quantity_unit_entry.pack(side=tk.TOP, padx=5, pady=5)

        tk.Label(self.price_input_frame, text="Jumlah Sampai").pack(side=tk.TOP, padx=5, pady=5)
        self.quantity_amount_entry = tk.Entry(self.price_input_frame)
        self.quantity_amount_entry.pack(side=tk.TOP, padx=5, pady=5)

        tk.Label(self.price_input_frame, text="Harga Jual").pack(side=tk.TOP, padx=5, pady=5)
        self.quantity_price_entry = tk.Entry(self.price_input_frame)
        self.quantity_price_entry.pack(side=tk.TOP, padx=5, pady=5)

        # Button to add the new quantity price entry
        add_button = tk.Button(self.price_input_frame, text="Tambah Harga Berdasarkan Jumlah", command=self.add_quantity_price)
        add_button.pack(side=tk.TOP, padx=5, pady=5)

        # Tombol hapus
        add_button = tk.Button(self.price_input_frame, text="Hapus", command=self.delete_selected_quantity_row)
        add_button.pack(side=tk.TOP, padx=5, pady=5)

    def create_by_unit_input(self):
        # Tabel untuk input harga berdasarkan satuan
        self.by_unit_tree = ttk.Treeview(self.price_input_frame, columns=("Satuan", "Harga Jual"), show="headings")
        self.by_unit_tree.heading("Satuan", text="Satuan")
        self.by_unit_tree.heading("Harga Jual", text="Harga Jual")
        self.by_unit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Entry fields for new unit price entry
        tk.Label(self.price_input_frame, text="Satuan").pack(side=tk.TOP, padx=5, pady=5)
        self.unit_price_entry = ttk.Combobox(self.price_input_frame)
        self.unit_price_entry['values'] = [row[0] for row in self.cursor.execute("SELECT satuan FROM units")]
        self.unit_price_entry.pack(side=tk.TOP, padx=5, pady=5)

        tk.Label(self.price_input_frame, text="Harga Jual").pack(side=tk.TOP, padx=5, pady=5)
        self.unit_price_value_entry = tk.Entry(self.price_input_frame)
        self.unit_price_value_entry.pack(side=tk.TOP, padx=5, pady=5)

        # Button to add the new unit price entry
        add_button = tk.Button(self.price_input_frame, text="Tambah Harga Berdasarkan Satuan", command=self.add_unit_price)
        add_button.pack(side=tk.TOP, padx=5, pady=5)

        # Tombol hapus
        add_button = tk.Button(self.price_input_frame, text="Hapus", command=self.delete_selected_unit_row)
        add_button.pack(side=tk.TOP, padx=5, pady=5)

    def add_quantity_price(self):
        unit = self.quantity_unit_entry.get()
        amount = self.quantity_amount_entry.get()
        price = self.quantity_price_entry.get()

        if unit and amount and price:
            self.by_quantity_tree.insert("", "end", values=(unit, amount, price))
            self.quantity_unit_entry.delete(0, tk.END)
            self.quantity_amount_entry.delete(0, tk.END)
            self.quantity_price_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Peringatan", "Semua field harus diisi!")

    def add_unit_price(self):
        unit = self.unit_price_entry.get()
        price = self.unit_price_value_entry.get()

        if unit and price:
            self.by_unit_tree.insert("", "end", values=(unit, price))
            self.unit_price_entry.delete(0, tk.END)
            self.unit_price_value_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Peringatan", "Semua field harus diisi!")


    def delete_selected_quantity_row(self):
        selected_item = self.by_quantity_tree.selection()
        if selected_item:
            self.by_quantity_tree.delete(selected_item)

    def delete_selected_unit_row(self):
        selected_item = self.by_unit_tree.selection()
        if selected_item:
            self.by_unit_tree.delete(selected_item)

    def load_jenis_produks(self):
        # Ambil data jenis produk dari tabel yang benar di database
        self.cursor.execute("SELECT jenis_produk FROM jenis_produks")
        jenis_produks = [row[0] for row in self.cursor.fetchall()]
        
        # Set data ke combobox
        self.jenis_produk_combobox['values'] = jenis_produks


    def load_units(self):
        # Ambil data satuan dari tabel di database
        self.cursor.execute("SELECT satuan FROM units")
        units = [row[0] for row in self.cursor.fetchall()]
        
        # Set data ke combobox
        self.satuan_dasar_combobox['values'] = units

    def center_window(self, width, height):
        # Get screen width and height
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()

        # Calculate x and y coordinates to center the window
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 4) - (height // 4)

        # Set the position of the window
        self.top.geometry(f"{width}x{height}+{x}+{y}")

    def on_mouse_wheel(self, event):
        # Scroll the canvas based on mouse wheel movement
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def scroll_up(self, event):
        # Scroll up the canvas
        self.canvas.yview_scroll(-1, "units")

    def scroll_down(self, event):
        # Scroll down the canvas
        self.canvas.yview_scroll(1, "units")

    def add_conversion(self):
        conversion_window = tk.Toplevel(self.top)
        conversion_window.title("Tambah Konversi")

        tk.Label(conversion_window, text="Satuan").grid(row=0, column=0, padx=5, pady=5)
        unit_entry = ttk.Combobox(conversion_window)
        unit_entry['values'] = [row[0] for row in self.cursor.execute("SELECT satuan FROM units")]
        unit_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(conversion_window, text="Konversi").grid(row=1, column=0, padx=5, pady=5)
        conversion_entry = tk.Entry(conversion_window)
        conversion_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(conversion_window, text="Barcode").grid(row=2, column=0, padx=5, pady=5)
        barcode_entry = tk.Entry(conversion_window)
        barcode_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(conversion_window, text="Harga Pokok").grid(row=3, column=0, padx=5, pady=5)
        price_entry = tk.Entry(conversion_window)
        price_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_conversion():
            unit = unit_entry.get()
            conversion = conversion_entry.get()
            barcode = barcode_entry.get()
            price = price_entry.get()

            if unit and conversion and barcode and price:
                self.conversion_tree.insert("", "end", values=(unit, conversion, barcode, price))
                conversion_window.destroy()
            else:
                messagebox.showwarning("Peringatan", "Semua field harus diisi!")

        save_button = tk.Button(conversion_window, text="Simpan", command=save_conversion)
        save_button.grid(row=4, columnspan=2, pady=10)

    def calculate_harga_pokok(self):
        total_price = 0
        total_units = 0
        for child in self.conversion_tree.get_children():
            item = self.conversion_tree.item(child)["values"]
            conversion = int(item[1])  # Konversi
            price = float(item[3])  # Harga Pokok

            total_units += conversion
            total_price += conversion * price

        if total_units > 0:
            harga_pokok = total_price / total_units
            self.harga_pokok_entry.delete(0, tk.END)
            self.harga_pokok_entry.insert(0, f"{harga_pokok:.2f}")
        else:
            messagebox.showwarning("Peringatan", "Tidak ada konversi yang valid untuk menghitung harga pokok dasar!")


    def on_conversion_item_select(self, event):
        selected_item = self.conversion_tree.selection()
        # Implement logic for selected conversion item if needed

    def save_product(self):
        # Validate required fields
        if not self.product_id_entry.get() or not self.nama_produk_entry.get() or not self.jenis_produk_combobox.get() or not self.harga_pokok_entry.get() or not self.satuan_dasar_combobox.get() or not self.barcode_entry.get():
            messagebox.showwarning("Peringatan", "Semua kolom yang wajib diisi harus terisi!")
            return

        # Gather information from the fields
        product_id = self.product_id_entry.get()
        nama_produk = self.nama_produk_entry.get()
        jenis_produk = self.jenis_produk_combobox.get()
        keterangan = self.keterangan_text.get("1.0", tk.END).strip()
        satuan_dasar = self.satuan_dasar_combobox.get()
        harga_pokok = self.harga_pokok_entry.get()
        barcode = self.barcode_entry.get()

        # Insert product data into the products table
        self.cursor.execute("""
            INSERT INTO products (product_id, nama_produk, jenis_produk, keterangan, satuan_dasar, harga_pokok, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, nama_produk, jenis_produk, keterangan, satuan_dasar, harga_pokok, barcode))

        # Save conversion data
        for child in self.conversion_tree.get_children():
            conversion_data = self.conversion_tree.item(child)['values']
            if conversion_data:
                satuan, konversi, konversi_barcode, konversi_harga_pokok = conversion_data
                self.cursor.execute("""
                    INSERT INTO unit_conversions (product_id, satuan, konversi, barcode, harga_pokok)
                    VALUES (?, ?, ?, ?, ?)
                """, (product_id, satuan, konversi, konversi_barcode, konversi_harga_pokok))

        # Save product prices based on selected price option
        if self.price_option_var.get() == "single":
            # Simpan harga satuan
            harga_idr = self.price_idr_entry.get()
            self.cursor.execute("""
                INSERT INTO product_prices (product_id, harga_jual, jenis_harga)
                VALUES (?, ?, ?)
            """, (product_id, harga_idr, 'satuan'))

        elif self.price_option_var.get() == "by_amount":
            # Simpan semua data dari tabel berdasarkan jumlah
            for child in self.by_quantity_tree.get_children():
                quantity_data = self.by_quantity_tree.item(child)['values']
                if quantity_data:
                    satuan, jumlah_sampai, harga_jual = quantity_data
                    self.cursor.execute("""
                        INSERT INTO product_prices (product_id, satuan, jumlah_sampai, harga_jual, jenis_harga)
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_id, satuan, jumlah_sampai, harga_jual, 'berdasarkan_jumlah'))

        elif self.price_option_var.get() == "by_unit":
            # Simpan semua data dari tabel berdasarkan satuan
            for child in self.by_unit_tree.get_children():
                unit_data = self.by_unit_tree.item(child)['values']
                if unit_data:
                    satuan, harga_jual = unit_data
                    self.cursor.execute("""
                        INSERT INTO product_prices (product_id, satuan, harga_jual, jenis_harga)
                        VALUES (?, ?, ?, ?)
                    """, (product_id, satuan, harga_jual, 'berdasarkan_satuan'))

        # Commit changes and close connection
        self.conn.commit()
        messagebox.showinfo("Sukses", "Produk berhasil disimpan!")
        self.top.destroy()


    
    # Jangan lupa menutup koneksi saat jendela ditutup
    def on_closing(self):
        self.conn.close()
        self.top.destroy()

class EditProductWindow(AddProductWindow):
    def __init__(self, parent, product_id, item_values):
        self.parent = parent
        self.product_id = product_id
        self.item_values = item_values
        super().__init__(parent)
        self.top.title("Edit Produk")
        self.load_product_data()
        self.load_conversions()  # Load conversion data
        self.load_prices()       # Load price data

    def load_product_data(self):
        # Load product data from database
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (self.product_id,))
        product_data = self.cursor.fetchone()

        if product_data:
            self.product_id_entry.insert(0, product_data[1])  # Kolom kode produk
            self.nama_produk_entry.insert(0, product_data[2])  # Kolom nama produk
            self.jenis_produk_combobox.set(product_data[3])    # Kolom jenis produk
            self.keterangan_text.insert("1.0", product_data[4])  # Kolom keterangan
            self.satuan_dasar_combobox.set(product_data[5])  # Kolom satuan dasar
            self.harga_pokok_entry.insert(0, product_data[6])  # Kolom harga pokok
            self.barcode_entry.insert(0, product_data[7])  # Kolom barcode

    def load_conversions(self):
        # Clear existing entries in the conversion tree
        for item in self.conversion_tree.get_children():
            self.conversion_tree.delete(item)

        # Load conversion data from the database
        self.cursor.execute("SELECT satuan, konversi, barcode, harga_pokok FROM unit_conversions WHERE product_id = ?", (self.product_id,))
        conversions = self.cursor.fetchall()
        for conversion in conversions:
            self.conversion_tree.insert("", "end", values=conversion)

    def load_prices(self):
        # Load price data from the database
        self.cursor.execute("SELECT tipe_harga FROM product_prices WHERE product_id = ?", (self.product_id,))
        price_data = self.cursor.fetchall()

        # Set the radio button based on the loaded price data
        if price_data:
            # Assuming you want to select the first price type found
            price_type = price_data[0][0]
            self.price_option_var.set(price_type)

            # Now, call the function to update the price input frame based on the selected type
            self.on_price_option_change()

            # Load specific price details based on price type
            if price_type == "by_amount":
                self.load_by_quantity_prices()
            elif price_type == "by_unit":
                self.load_by_unit_prices()
    
    def load_by_quantity_prices(self):
        # Load prices based on quantity into the quantity tree
        for item in self.by_quantity_tree.get_children():
            self.by_quantity_tree.delete(item)

        self.cursor.execute("SELECT satuan, jumlah_sampai, harga_jual FROM product_prices WHERE product_id = ? AND tipe_harga = 'by_amount'", (self.product_id,))
        quantity_prices = self.cursor.fetchall()
        for price in quantity_prices:
            self.by_quantity_tree.insert("", "end", values=price)

    def load_by_unit_prices(self):
        # Load prices based on unit into the unit price tree
        for item in self.by_unit_tree.get_children():
            self.by_unit_tree.delete(item)

        self.cursor.execute("SELECT satuan, harga_jual FROM product_prices WHERE product_id = ? AND tipe_harga = 'by_unit'", (self.product_id,))
        unit_prices = self.cursor.fetchall()
        for price in unit_prices:
            self.by_unit_tree.insert("", "end", values=price)

    def save_product(self):
        # Save product changes
        product_id = self.product_id_entry.get()
        nama_produk = self.nama_produk_entry.get()
        jenis_produk = self.jenis_produk_combobox.get()
        keterangan = self.keterangan_text.get("1.0", tk.END)
        satuan_dasar = self.satuan_dasar_combobox.get()
        harga_pokok = self.harga_pokok_entry.get()
        barcode = self.barcode_entry.get()

        # Update product in database
        self.cursor.execute(
            "UPDATE products SET product_id=?, nama_produk=?, jenis_produk=?, keterangan=?, satuan_dasar=?, harga_pokok=?, barcode=? WHERE id=?",
            (product_id, nama_produk, jenis_produk, keterangan, satuan_dasar, harga_pokok, barcode, self.product_id)
        )
        self.conn.commit()
        self.top.destroy()


        
if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = KasirApp(root)
    root.mainloop()
