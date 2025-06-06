import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os

class PersonalFinanceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Database connection
        self.db_connection = None
        self.connect_to_database()
        
        # Create tables if they don't exist
        self.create_tables()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.header_frame, text="Personal Finance Manager", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Navigation buttons
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(self.nav_frame, text="Add Transaction", command=self.show_add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="View Transactions", command=self.show_transactions).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="View Reports", command=self.show_reports).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # Content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Default view
        self.show_transactions()
    
    def connect_to_database(self):
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password=""
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {err}")
            self.root.destroy()
    
    def create_tables(self):
        try:
            cursor = self.db_connection.cursor()

            cursor.execute("CREATE DATABASE IF NOT EXISTS finance_manager")
            cursor.execute("USE finance_manager")
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    type VARCHAR(10) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    description VARCHAR(255),
                    date DATE NOT NULL
                )
            """)
            
            # Create categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    type VARCHAR(10) NOT NULL
                )
            """)
            
            # Insert default categories if they don't exist
            default_categories = [
                ('Salary', 'income'),
                ('Freelance', 'income'),
                ('Investments', 'income'),
                ('Gifts', 'income'),
                ('Food', 'expense'),
                ('Transport', 'expense'),
                ('Housing', 'expense'),
                ('Utilities', 'expense'),
                ('Entertainment', 'expense'),
                ('Healthcare', 'expense'),
                ('Education', 'expense'),
                ('Shopping', 'expense'),
                ('Other', 'income'),
                ('Other', 'expense')
            ]
            
            for category in default_categories:
                try:
                    cursor.execute("INSERT INTO categories (name, type) VALUES (%s, %s)", category)
                except mysql.connector.IntegrityError:
                    # Category already exists
                    pass
            
            self.db_connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error creating tables: {err}")
    
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_add_transaction(self):
        self.clear_content_frame()
        
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(pady=20)
        
        # Transaction type
        ttk.Label(form_frame, text="Transaction Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.trans_type = tk.StringVar(value="income")
        ttk.Radiobutton(form_frame, text="Income", variable=self.trans_type, value="income").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(form_frame, text="Expense", variable=self.trans_type, value="expense").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.category = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category, state="readonly")
        self.category_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Update categories based on transaction type
        self.trans_type.trace('w', self.update_categories)
        self.update_categories()
        
        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.amount = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.amount).grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.description = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description).grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Date
        ttk.Label(form_frame, text="Date:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        self.date = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=self.date).grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Add Transaction", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add New Category", command=self.show_add_category).pack(side=tk.LEFT, padx=5)
    
    def update_categories(self, *args):
        trans_type = self.trans_type.get()
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT name FROM categories WHERE type = %s ORDER BY name", (trans_type,))
            categories = [row[0] for row in cursor.fetchall()]
            self.category_combo['values'] = categories
            if categories:
                self.category.set(categories[0])
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading categories: {err}")
    
    def show_add_category(self):
        add_category_window = tk.Toplevel(self.root)
        add_category_window.title("Add New Category")
        add_category_window.geometry("400x200")
        
        ttk.Label(add_category_window, text="Category Name:").pack(pady=5)
        category_name = tk.StringVar()
        ttk.Entry(add_category_window, textvariable=category_name).pack(pady=5)
        
        ttk.Label(add_category_window, text="Category Type:").pack(pady=5)
        category_type = tk.StringVar(value="expense")
        ttk.Radiobutton(add_category_window, text="Income", variable=category_type, value="income").pack()
        ttk.Radiobutton(add_category_window, text="Expense", variable=category_type, value="expense").pack()
        
        def save_category():
            name = category_name.get().strip()
            if not name:
                messagebox.showerror("Error", "Category name cannot be empty")
                return
            
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("INSERT INTO categories (name, type) VALUES (%s, %s)", (name, category_type.get()))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Category added successfully")
                add_category_window.destroy()
                self.update_categories()  # Refresh the category list
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Category already exists")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error adding category: {err}")
        
        ttk.Button(add_category_window, text="Save", command=save_category).pack(pady=10)
    
    def add_transaction(self):
        trans_type = self.trans_type.get()
        category = self.category.get()
        amount = self.amount.get()
        description = self.description.get()
        date = self.date.get()
        
        # Validation
        if not category:
            messagebox.showerror("Error", "Please select a category")
            return
        
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive")
            return
        
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO transactions (type, category, amount, description, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (trans_type, category, amount, description, date))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Transaction added successfully")
            
            # Clear form
            self.amount.set(0)
            self.description.set("")
            self.date.set(datetime.now().strftime('%Y-%m-%d'))
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding transaction: {err}")
    
    def show_transactions(self):
        self.clear_content_frame()
        
        # Filter controls
        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=5)
        
        self.filter_type = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_type, value="all").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Income", variable=self.filter_type, value="income").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Expense", variable=self.filter_type, value="expense").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.filter_from = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_from, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.filter_to = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_to, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Apply", command=self.load_transactions).pack(side=tk.LEFT, padx=10)
        
        # Transactions treeview
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "type", "category", "amount", "description", "date")
        self.transactions_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse"
        )
        
        # Configure columns
        self.transactions_tree.heading("id", text="ID")
        self.transactions_tree.heading("type", text="Type")
        self.transactions_tree.heading("category", text="Category")
        self.transactions_tree.heading("amount", text="Amount")
        self.transactions_tree.heading("description", text="Description")
        self.transactions_tree.heading("date", text="Date")
        
        self.transactions_tree.column("id", width=50, anchor=tk.CENTER)
        self.transactions_tree.column("type", width=80, anchor=tk.CENTER)
        self.transactions_tree.column("category", width=120, anchor=tk.CENTER)
        self.transactions_tree.column("amount", width=100, anchor=tk.CENTER)
        self.transactions_tree.column("description", width=200)
        self.transactions_tree.column("date", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transactions_tree.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Refresh", command=self.load_transactions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_transaction).pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self.load_transactions()
    
    def load_transactions(self):
        # Clear existing data
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Build query based on filters
        query = "SELECT id, type, category, amount, description, date FROM transactions"
        conditions = []
        params = []
        
        filter_type = self.filter_type.get()
        if filter_type != "all":
            conditions.append("type = %s")
            params.append(filter_type)
        
        date_from = self.filter_from.get()
        if date_from:
            try:
                datetime.strptime(date_from, '%Y-%m-%d')
                conditions.append("date >= %s")
                params.append(date_from)
            except ValueError:
                messagebox.showerror("Error", "Invalid 'From' date format. Use YYYY-MM-DD")
                return
        
        date_to = self.filter_to.get()
        if date_to:
            try:
                datetime.strptime(date_to, '%Y-%m-%d')
                conditions.append("date <= %s")
                params.append(date_to)
            except ValueError:
                messagebox.showerror("Error", "Invalid 'To' date format. Use YYYY-MM-DD")
                return
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC"
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                # Format amount with 2 decimal places
                formatted_row = list(row)
                formatted_row[3] = f"{row[3]:.2f}"
                self.transactions_tree.insert("", tk.END, values=formatted_row)
            
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading transactions: {err}")
    
    def edit_transaction(self):
        selected_item = self.transactions_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a transaction to edit")
            return
        
        item_data = self.transactions_tree.item(selected_item)['values']
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Transaction")
        edit_window.geometry("400x300")
        
        # Transaction ID (hidden)
        trans_id = item_data[0]
        
        # Transaction type
        ttk.Label(edit_window, text="Transaction Type:").pack(pady=5)
        trans_type = tk.StringVar(value=item_data[1])
        type_frame = ttk.Frame(edit_window)
        type_frame.pack()
        ttk.Radiobutton(type_frame, text="Income", variable=trans_type, value="income").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Expense", variable=trans_type, value="expense").pack(side=tk.LEFT, padx=5)
        
        # Category
        ttk.Label(edit_window, text="Category:").pack(pady=5)
        category = tk.StringVar(value=item_data[2])
        category_combo = ttk.Combobox(edit_window, textvariable=category, state="readonly")
        category_combo.pack()
        
        # Update categories based on transaction type
        def update_edit_categories(*args):
            current_type = trans_type.get()
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT name FROM categories WHERE type = %s ORDER BY name", (current_type,))
                categories = [row[0] for row in cursor.fetchall()]
                category_combo['values'] = categories
                if categories:
                    category.set(item_data[2] if item_data[2] in categories else categories[0])
                cursor.close()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error loading categories: {err}")
        
        trans_type.trace('w', update_edit_categories)
        update_edit_categories()
        
        # Amount
        ttk.Label(edit_window, text="Amount:").pack(pady=5)
        amount = tk.DoubleVar(value=float(item_data[3]))
        ttk.Entry(edit_window, textvariable=amount).pack()
        
        # Description
        ttk.Label(edit_window, text="Description:").pack(pady=5)
        description = tk.StringVar(value=item_data[4])
        ttk.Entry(edit_window, textvariable=description).pack()
        
        # Date
        ttk.Label(edit_window, text="Date:").pack(pady=5)
        date = tk.StringVar(value=item_data[5])
        ttk.Entry(edit_window, textvariable=date).pack()
        
        def save_changes():
            # Validation
            if not category.get():
                messagebox.showerror("Error", "Please select a category")
                return
            
            if amount.get() <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return
            
            try:
                datetime.strptime(date.get(), '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE transactions 
                    SET type = %s, category = %s, amount = %s, description = %s, date = %s
                    WHERE id = %s
                """, (trans_type.get(), category.get(), amount.get(), description.get(), date.get(), trans_id))
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Transaction updated successfully")
                edit_window.destroy()
                self.load_transactions()  # Refresh the transactions list
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error updating transaction: {err}")
        
        ttk.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
    
    def delete_transaction(self):
        selected_item = self.transactions_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a transaction to delete")
            return
        
        item_data = self.transactions_tree.item(selected_item)['values']
        
        if not messagebox.askyesno("Confirm", f"Delete transaction #{item_data[0]} - {item_data[2]} ({item_data[3]})?"):
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = %s", (item_data[0],))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Transaction deleted successfully")
            self.load_transactions()  # Refresh the transactions list
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error deleting transaction: {err}")
    
    def show_reports(self):
        self.clear_content_frame()
        
        # Report type selection
        report_frame = ttk.Frame(self.content_frame)
        report_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(report_frame, text="Report Type:").pack(side=tk.LEFT, padx=5)
        
        self.report_type = tk.StringVar(value="summary")
        ttk.Radiobutton(report_frame, text="Summary", variable=self.report_type, value="summary").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(report_frame, text="Income by Category", variable=self.report_type, value="income_categories").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(report_frame, text="Expenses by Category", variable=self.report_type, value="expense_categories").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(report_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.report_from = tk.StringVar()
        ttk.Entry(report_frame, textvariable=self.report_from, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(report_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.report_to = tk.StringVar()
        ttk.Entry(report_frame, textvariable=self.report_to, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(report_frame, text="Generate", command=self.generate_report).pack(side=tk.LEFT, padx=10)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.content_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Summary statistics
        self.summary_frame = ttk.Frame(self.content_frame)
        
        # Generate initial report
        self.generate_report()
    
    def generate_report(self):
        # Clear previous content
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        report_type = self.report_type.get()
        date_from = self.report_from.get()
        date_to = self.report_to.get()
        
        # Validate dates
        try:
            if date_from:
                datetime.strptime(date_from, '%Y-%m-%d')
            if date_to:
                datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        if report_type == "summary":
            self.generate_summary_report(date_from, date_to)
        elif report_type == "income_categories":
            self.generate_category_report("income", date_from, date_to)
        elif report_type == "expense_categories":
            self.generate_category_report("expense", date_from, date_to)
    
    def generate_summary_report(self, date_from, date_to):
        try:
            cursor = self.db_connection.cursor()
            
            # Build query with date filters
            income_query = "SELECT SUM(amount) FROM transactions WHERE type = 'income'"
            expense_query = "SELECT SUM(amount) FROM transactions WHERE type = 'expense'"
            params = []
            
            conditions = []
            if date_from:
                conditions.append("date >= %s")
                params.append(date_from)
            if date_to:
                conditions.append("date <= %s")
                params.append(date_to)
            
            if conditions:
                where_clause = " WHERE " + " AND ".join(conditions)
                income_query += where_clause
                expense_query += where_clause
            
            # Get total income
            cursor.execute(income_query, params)
            total_income = cursor.fetchone()[0] or 0
            
            # Get total expenses
            cursor.execute(expense_query, params)
            total_expenses = cursor.fetchone()[0] or 0
            
            # Calculate balance
            balance = total_income - total_expenses
            
            # Display summary
            self.summary_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(self.summary_frame, text="Financial Summary", font=('Arial', 12, 'bold')).pack(pady=5)
            
            summary_text = f"Total Income: ${total_income:.2f}\n"
            summary_text += f"Total Expenses: ${total_expenses:.2f}\n"
            summary_text += f"Balance: ${balance:.2f}"
            
            ttk.Label(self.summary_frame, text=summary_text).pack()
            
            # Create pie chart for income vs expenses
            fig, ax = plt.subplots(figsize=(6, 4))
            
            if total_income > 0 or total_expenses > 0:
                labels = ['Income', 'Expenses']
                sizes = [total_income, total_expenses]
                colors = ['#4CAF50', '#F44336']
                
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle
                ax.set_title('Income vs Expenses')
                
                canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(self.chart_frame, text="No data available for the selected period").pack()
            
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error generating summary report: {err}")
    
    def generate_category_report(self, trans_type, date_from, date_to):
        try:
            cursor = self.db_connection.cursor()
            
            # Build query with date filters
            query = """
                SELECT category, SUM(amount) 
                FROM transactions 
                WHERE type = %s
            """
            params = [trans_type]
            
            conditions = []
            if date_from:
                conditions.append("date >= %s")
                params.append(date_from)
            if date_to:
                conditions.append("date <= %s")
                params.append(date_to)
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            query += " GROUP BY category ORDER BY SUM(amount) DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if not results:
                ttk.Label(self.chart_frame, text=f"No {trans_type} data available for the selected period").pack()
                return
            
            # Prepare data for chart
            categories = [row[0] for row in results]
            amounts = [float(row[1]) for row in results]
            
            # Create bar chart
            fig, ax = plt.subplots(figsize=(8, 5))
            
            color = '#4CAF50' if trans_type == 'income' else '#F44336'
            ax.bar(categories, amounts, color=color)
            
            ax.set_xlabel('Category')
            ax.set_ylabel('Amount ($)')
            ax.set_title(f'{trans_type.capitalize()} by Category')
            plt.xticks(rotation=45, ha='right')
            
            # Add data labels
            for i, v in enumerate(amounts):
                ax.text(i, v, f"${v:.2f}", ha='center', va='bottom')
            
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error generating category report: {err}")
    
    def export_data(self):
        # Ask user for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Transactions As"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT type, category, amount, description, date 
                FROM transactions 
                ORDER BY date DESC
            """)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Write header
                csvwriter.writerow(['Type', 'Category', 'Amount', 'Description', 'Date'])
                
                # Write data
                for row in cursor.fetchall():
                    csvwriter.writerow(row)
            
            cursor.close()
            messagebox.showinfo("Success", f"Data exported successfully to {os.path.basename(file_path)}")
        except (mysql.connector.Error, IOError) as err:
            messagebox.showerror("Error", f"Error exporting data: {err}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonalFinanceManager(root)
    root.mainloop()