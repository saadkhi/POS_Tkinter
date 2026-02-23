# main_app.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import threading
import customtkinter as ctk

from pos_page import POSFrame
from table_viewer_page import TableViewerFrame
from sync_service import sync_oracle_to_sqlite

# -------------------- CONFIG --------------------
LOCAL_DB = "local_pos.db"

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def sync_all_tables():
    # Call the synchronization service
    success, message = sync_oracle_to_sqlite()
    if success:
        messagebox.showinfo("Success", message)
    else:
        messagebox.showerror("Error", message)

def init_db():
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # Insert default admin user if it doesn't exist
    admin_user = "admin"
    admin_pass = hash_password("admin")
    cursor.execute("SELECT * FROM users WHERE username=?", (admin_user,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (admin_user, admin_pass))
    
    # Ensure other tables mentioned in TableViewerFrame exist to prevent crashes
    tables = [
        "STGS_ARTICLE_CSM", "STGS_ARTICLEM", "STGS_COLORM", 
        "ARTICLE_SIZEM", "FACOA", "ARTICLE_SIZE_TYPE"
    ]
    for table in tables:
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table}" (id INTEGER PRIMARY KEY)')

    conn.commit()
    conn.close()

# -------------------- MAIN APP --------------------
# -------------------- MAIN APP --------------------
class POSApp(ctk.CTk):
    def __init__(self, username):
        super().__init__()
        self.title(f"POS System - Logged in as {username}")
        self.geometry("1300x800")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Navbar
        nav_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        nav_frame.pack(fill="x", side="top")
        
        ctk.CTkButton(nav_frame, text="POS Sale", command=self.show_pos, width=100).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(nav_frame, text="Table Viewer", command=self.show_table, width=100).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(nav_frame, text="Sync Oracle", command=lambda: threading.Thread(target=sync_all_tables).start(), width=100, fg_color="green", hover_color="darkgreen").pack(side="right", padx=10, pady=5)

        # Container for frames
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Frames
        self.pos_frame = POSFrame(self.container)
        self.table_frame = TableViewerFrame(self.container)

        self.pos_frame.pack(fill="both", expand=True)
        self.table_frame.pack_forget()

    def show_pos(self):
        self.table_frame.pack_forget()
        self.pos_frame.pack(fill="both", expand=True)

    def show_table(self):
        self.pos_frame.pack_forget()
        self.table_frame.pack(fill="both", expand=True)

# -------------------- LOGIN --------------------
# -------------------- LOGIN --------------------
class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("POS Login")
        self.geometry("400x350")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(self.main_frame, text="POS SYSTEM LOGIN", font=("Arial Bold", 20)).pack(pady=20)
        
        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=10)
        
        ctk.CTkButton(self.main_frame, text="Login", command=self.login, width=250).pack(pady=30)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_pw = hash_password(password)
        conn = sqlite3.connect(LOCAL_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.destroy()
            app = POSApp(username)
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

# -------------------- RUN --------------------
if __name__ == "__main__":
    init_db()
    login_app = LoginApp()
    login_app.mainloop()
