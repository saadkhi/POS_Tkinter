# main_app.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import threading

from pos_page import POSFrame
from table_viewer_page import TableViewerFrame

# -------------------- CONFIG --------------------
LOCAL_DB = "local_pos.db"

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def sync_all_tables():
    # Placeholder sync function
    messagebox.showinfo("Info", "Sync called!")

# -------------------- MAIN APP --------------------
class POSApp(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.title(f"POS System - Logged in as {username}")
        self.geometry("1200x700")

        # Navbar
        nav_frame = tk.Frame(self, bg="#333")
        nav_frame.pack(fill="x")
        tk.Button(nav_frame, text="POS Sale", fg="white", bg="#333", command=self.show_pos).pack(side="left", padx=5, pady=5)
        tk.Button(nav_frame, text="Table Viewer", fg="white", bg="#333", command=self.show_table).pack(side="left", padx=5, pady=5)
        tk.Button(nav_frame, text="Sync Oracle", fg="white", bg="#333", command=lambda: threading.Thread(target=sync_all_tables).start()).pack(side="right", padx=5, pady=5)

        # Container for frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

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
class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POS Login")
        self.geometry("400x250")
        tk.Label(self, text="Username").pack(pady=10)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        tk.Label(self, text="Password").pack(pady=10)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        tk.Button(self, text="Login", command=self.login).pack(pady=20)

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
    login_app = LoginApp()
    login_app.mainloop()
