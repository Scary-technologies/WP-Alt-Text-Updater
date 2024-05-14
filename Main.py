import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import os

def update_image_alts(host, user, password, database, table_prefix, alt_text, valid_extensions, treeview):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = f"""
                SELECT pm1.post_id, pm1.meta_value AS image_url, pm2.meta_value AS alt_text
                FROM {table_prefix}postmeta pm1
                LEFT JOIN {table_prefix}postmeta pm2 ON pm1.post_id = pm2.post_id AND pm2.meta_key = '_wp_attachment_image_alt'
                WHERE pm1.meta_key = '_wp_attached_file';
            """
            cursor.execute(query)
            images = cursor.fetchall()

            for image in images:
                post_id, image_url, alt_text_existing = image
                image_name = os.path.basename(image_url)  # استخراج نام تصویر از URL
                if any(image_url.lower().endswith(ext.strip()) for ext in valid_extensions):
                    if not alt_text_existing or alt_text_existing.strip() == "":
                        cursor.execute(f"""
                            INSERT INTO {table_prefix}postmeta (post_id, meta_key, meta_value)
                            VALUES (%s, '_wp_attachment_image_alt', %s)
                            ON DUPLICATE KEY UPDATE meta_value = VALUES(meta_value);
                        """, (post_id, alt_text))
                        connection.commit()
                    
                    # اضافه کردن اطلاعات تصویر به Treeview
                    treeview.insert("", "end", values=(image_name, alt_text_existing or alt_text))

            messagebox.showinfo("Success", "ALT texts updated successfully.")

    except Error as e:
        messagebox.showerror("Error", f"Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

def submit():
    host = host_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    database = database_entry.get()
    table_prefix = table_prefix_entry.get()
    alt_text = alt_text_entry.get()
    valid_extensions = extensions_entry.get().split(',')

    # پاک کردن اطلاعات قدیمی از Treeview
    for item in treeview.get_children():
        treeview.delete(item)

    update_image_alts(host, user, password, database, table_prefix, alt_text, valid_extensions, treeview)

# ایجاد پنجره اصلی
root = tk.Tk()
Title_V=  " تصاویر در وردپرس"+ " Alt "+ "بروزرسانی" 
root.title(Title_V)

# ایجاد و جایگذاری برچسب‌ها و ورودی‌ها
ttk.Label(root, text="Host:").grid(row=0, column=0, padx=10, pady=5)
host_entry = ttk.Entry(root)
host_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(root, text="User:").grid(row=1, column=0, padx=10, pady=5)
user_entry = ttk.Entry(root)
user_entry.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=5)
password_entry = ttk.Entry(root, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(root, text="Database:").grid(row=3, column=0, padx=10, pady=5)
database_entry = ttk.Entry(root)
database_entry.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(root, text="Table Prefix:").grid(row=4, column=0, padx=10, pady=5)
table_prefix_entry = ttk.Entry(root)
table_prefix_entry.grid(row=4, column=1, padx=10, pady=5)

ttk.Label(root, text="Alt Text:").grid(row=5, column=0, padx=10, pady=5)
alt_text_entry = ttk.Entry(root)
alt_text_entry.grid(row=5, column=1, padx=10, pady=5)

ttk.Label(root, text="Valid Extensions (comma-separated):").grid(row=6, column=0, padx=10, pady=5)
extensions_entry = ttk.Entry(root)
extensions_entry.grid(row=6, column=1, padx=10, pady=5)
extensions_entry.insert(0, '.jpg, .jpeg, .png, .gif, .webp, .svg')  # Default extensions

# ایجاد و جایگذاری دکمه ارسال
submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.grid(row=7, column=0, columnspan=2, pady=10)

# ایجاد ویجت Treeview برای نمایش اطلاعات تصاویر
columns = ("Image Name", "ALT Text")
treeview = ttk.Treeview(root, columns=columns, show="headings")
treeview.heading("Image Name", text="Image Name")
treeview.heading("ALT Text", text="ALT Text")
treeview.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

# تنظیم اسکرول بار برای Treeview
scrollbar = ttk.Scrollbar(root, orient="vertical", command=treeview.yview)
treeview.configure(yscroll=scrollbar.set)
scrollbar.grid(row=8, column=2, sticky='ns')

# تنظیم اولویت ستون‌ها
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(8, weight=1)

# شروع حلقه اصلی
root.mainloop()
