import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sqlite3
import pandas as pd

TABLES = [
    "STGS_ARTICLE_CSM",
    "STGS_ARTICLEM",
    "STGS_COLORM",
    "ARTICLE_SIZEM",
    "FACOA",
    "ARTICLE_SIZE_TYPE"
]

# Stgs_article_cs, stgs_article, stgs_color, article_size


LOCAL_DB = "local_pos.db"

class TableViewerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_table = ctk.StringVar(value=TABLES[0])
        self.columns_list = []

        # Table Dropdown
        dropdown = ctk.CTkComboBox(self, values=TABLES, variable=self.selected_table, command=lambda e: self.load_columns())
        dropdown.pack(pady=20)

        # Columns Listbox (Keeping standard Listbox for now but in ctk frame)
        self.listbox_frame = ctk.CTkFrame(self)
        self.listbox_frame.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(self.listbox_frame, text="Select Columns:").pack(pady=5)
        self.listbox = tk.Listbox(self.listbox_frame, selectmode="multiple", height=5, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.listbox.pack(fill="x", padx=10, pady=5)

        # Treeview
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        ctk.CTkButton(self, text="Load Data", command=self.load_table).pack(pady=20)

        self.load_columns()

    def load_columns(self):
        """Load columns from selected table into the listbox"""
        self.listbox.delete(0, tk.END)
        conn = sqlite3.connect(LOCAL_DB)
        cursor = conn.cursor()
        table = self.selected_table.get()
        cursor.execute(f'SELECT * FROM "{table}" LIMIT 1')
        cols = [desc[0] for desc in cursor.description]
        conn.close()

        self.columns_list = cols
        for col in cols:
            self.listbox.insert(tk.END, col)
            self.listbox.selection_set(tk.END)  # Select all by default

    def load_table(self):
        """Load table data based on selected columns in listbox"""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Select at least one column!")
            return

        selected_cols = [self.columns_list[i] for i in selected_indices]

        try:
            conn = sqlite3.connect(LOCAL_DB)
            # Quote column names to handle special characters like #
            quoted_cols = [f'"{col}"' for col in selected_cols]
            query = f'SELECT {",".join(quoted_cols)} FROM "{self.selected_table.get()}" LIMIT 50'
            df = pd.read_sql_query(query, conn)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Clear and setup treeview
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))
