import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import oracledb

# -------------------- CONFIG --------------------
DB_USER = "botiq"
DB_PASS = "nasir786"
DB_HOST = "79.143.179.51"
DB_PORT = 1539
DB_SERVICE = "oracle"

# Employee List
EMPLOYEE_LIST = [
    "ADMIN",
    "AHTISHAM SHAH",
    "GHANZANFAR ALI",
    "IDRESS",
    "Idrees",
    "486-Jawed",
    "582-AAMIR",
    "MUNEEB",
    "NADEEM",
    "483-SAAD"
]

# -------------------- ORACLE UTILS --------------------
def get_articles_list(sale_return='N', loc_id=None):
    """Fetch article list from Oracle to populate Combobox"""
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            service_name=DB_SERVICE
        )
        cur = conn.cursor()
        query = """
        SELECT artcl_ID_SHOP || ' Color ' || COLOR_DESC || ' Size ' || size_nm AS D,
               Atlcs_id
        FROM Stgs_article_csm csm
        JOIN stgs_articlem art ON csm.atlcs_artcl_id = art.artcl_id
        JOIN stgs_colorm col ON csm.atlcs_color_id = col.color_id
        JOIN article_sizem sz ON csm.atlcs_size = sz.size_no
        WHERE csm.atlcs_id IN (
            SELECT DISTINCT STCKV_ATLCS_ID
            FROM STVW_STOCK_CARD
            GROUP BY STCKV_ATLCS_ID
            HAVING (:sale_return='Y') OR SUM(STCKV_QTY) > 0
        )
        ORDER BY artcl_ID_SHOP, COLOR_DESC, size_no
        """
        cur.execute(query, sale_return=sale_return)
        result = cur.fetchall()  # List of tuples (display_name, Atlcs_id)
        conn.close()
        return result  # Return full tuples
    except Exception as e:
        messagebox.showerror("Error fetching articles", str(e))
        return []

# -------------------- POS FRAME --------------------
class POSFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.sale_items = []

        # Sale Info Frame
        frame1 = tk.Frame(self)
        frame1.pack(fill="x", padx=10, pady=10)
        tk.Label(frame1, text="Salem Emply Id").grid(row=0, column=0)
        self.emp_entry = ttk.Combobox(frame1, values=EMPLOYEE_LIST, state="readonly")
        self.emp_entry.grid(row=0, column=1)
        self.emp_entry.set(EMPLOYEE_LIST[0])

        tk.Label(frame1, text="Salem Trans#").grid(row=0, column=2)
        self.trans_entry = tk.Entry(frame1)
        self.trans_entry.grid(row=0, column=3)

        tk.Label(frame1, text="Contact #").grid(row=1, column=0)
        self.contact_entry = tk.Entry(frame1)
        self.contact_entry.grid(row=1, column=1)

        tk.Label(frame1, text="Date").grid(row=1, column=2)
        self.date_entry = tk.Entry(frame1)
        self.date_entry.insert(0, datetime.now().strftime("%d-%b-%Y %H:%M:%S"))
        self.date_entry.grid(row=1, column=3)

        self.return_var = tk.IntVar()
        tk.Checkbutton(frame1, text="Return Item", variable=self.return_var).grid(row=2, column=0, pady=5)

        # Article Entry Frame
        frame2 = tk.Frame(self)
        frame2.pack(fill="x", padx=10, pady=10)

        tk.Label(frame2, text="Bar Code").grid(row=0, column=0)
        self.bar_entry = tk.Entry(frame2)
        self.bar_entry.grid(row=0, column=1)

        tk.Label(frame2, text="Article Description").grid(row=0, column=2)
        # Fetch articles dynamically
        result = get_articles_list(sale_return='N', loc_id=None)
        article_values = [r[0] for r in result]
        self.article_entry = ttk.Combobox(frame2, values=article_values, width=50)
        self.article_entry.grid(row=0, column=3)
        if article_values:
            self.article_entry.set(article_values[0])

        # Create articles_data dictionary
        self.articles_data = {}
        for display, atlcs_id in result:
            parts = display.split(" Color ")
            if len(parts) == 2:
                artcl_id_shop = parts[0]
                color_size = parts[1].split(" Size ")
                if len(color_size) == 2:
                    color = color_size[0]
                    size = color_size[1]
                else:
                    color = "Unknown"
                    size = "Unknown"
            else:
                color = "Unknown"
                size = "Unknown"
            self.articles_data[display] = {"Color": color, "Size": size, "Retail": 10000, "Atlcs_id": atlcs_id}

        tk.Label(frame2, text="Qty").grid(row=0, column=4)
        self.qty_entry = tk.Entry(frame2)
        self.qty_entry.grid(row=0, column=5)

        tk.Button(frame2, text="Add Item", command=self.add_item).grid(row=0, column=6, padx=5)

        # Items Table Frame
        frame3 = tk.Frame(self)
        frame3.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ["Article Name", "Color Desc", "Size", "Retail Rate", "Quantity",
                   "Final Price", "Salem Emply Id", "Sale Discount"]
        self.tree = ttk.Treeview(frame3, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(frame3, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Totals Frame
        frame4 = tk.Frame(self)
        frame4.pack(fill="x", padx=10, pady=10)
        tk.Label(frame4, text="Pay Mode").grid(row=0, column=0)
        self.pay_entry = tk.Entry(frame4)
        self.pay_entry.grid(row=0, column=1)

        tk.Label(frame4, text="Total Qty").grid(row=1, column=0)
        self.total_qty_entry = tk.Entry(frame4)
        self.total_qty_entry.grid(row=1, column=1)

        tk.Label(frame4, text="Original Price").grid(row=2, column=0)
        self.orig_price_entry = tk.Entry(frame4)
        self.orig_price_entry.grid(row=2, column=1)

        tk.Label(frame4, text="Total Discount").grid(row=3, column=0)
        self.discount_entry = tk.Entry(frame4)
        self.discount_entry.grid(row=3, column=1)

        tk.Label(frame4, text="Net Sale").grid(row=4, column=0)
        self.net_sale_entry = tk.Entry(frame4)
        self.net_sale_entry.grid(row=4, column=1)

    def add_item(self):
        article = self.article_entry.get()
        qty = self.qty_entry.get()
        if not qty.isdigit():
            messagebox.showerror("Error", "Qty must be a number!")
            return
        qty = int(qty)
        emp = self.emp_entry.get()
        retail = 10000  # Placeholder
        final_price = retail * qty
        discount = 0

        data = self.articles_data[article]
        color = data["Color"]
        size = data["Size"]
        retail = data["Retail"]
        final_price = retail * qty
        row = [article, color, size, retail, qty, final_price, emp, discount]
        self.sale_items.append(row)
        self.tree.insert("", tk.END, values=row)

        # Update totals
        total_qty = sum([r[4] for r in self.sale_items])
        orig_price = sum([r[3] for r in self.sale_items])
        total_discount = sum([r[7] for r in self.sale_items])
        net_sale = sum([r[5] for r in self.sale_items])

        self.total_qty_entry.delete(0, tk.END)
        self.total_qty_entry.insert(0, total_qty)
        self.orig_price_entry.delete(0, tk.END)
        self.orig_price_entry.insert(0, orig_price)
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, total_discount)
        self.net_sale_entry.delete(0, tk.END)
        self.net_sale_entry.insert(0, net_sale)

        # Clear input
        self.article_entry.set("")
        self.qty_entry.delete(0, tk.END)
        self.bar_entry.delete(0, tk.END)
