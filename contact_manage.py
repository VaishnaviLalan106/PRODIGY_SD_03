import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

CONTACTS_FILE = 'contacts.json'

def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return []
    with open(CONTACTS_FILE, 'r') as f:
        return json.load(f)

def save_contacts(contacts):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=4)

class ContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 Contact Manager")
        self.root.geometry("800x600")
        self.root.config(bg="#f0c3a5")

        self.contacts = load_contacts()

        self.title_label = tk.Label(root, text="📇 Contact Management System", font=("Segoe UI", 20, "bold"), bg="#e68484", fg="black")
        self.title_label.pack(pady=15)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_contacts)
        self.search_entry = tk.Entry(root, textvariable=self.search_var, font=("Segoe UI", 11), width=40, relief=tk.FLAT)
        self.search_entry.pack(pady=5)
        self.search_entry.insert(0, "Search by name...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END))

        self.button_frame = tk.Frame(root, bg="#f0c3a5")
        self.button_frame.pack(pady=10)

        self.make_button("➕ Add", self.add_contact_popup).pack(side=tk.LEFT, padx=10)
        self.make_button("✏ Edit", self.edit_contact_popup).pack(side=tk.LEFT, padx=10)
        self.make_button("❌ Delete", self.delete_contact_popup).pack(side=tk.LEFT, padx=10)
        self.make_button("🔄 Refresh", self.refresh_view).pack(side=tk.LEFT, padx=10)

        self.contact_frame = tk.Frame(root, bg="#daa7c6")
        self.contact_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(self.contact_frame, bg="#f3e0eb", highlightthickness=0)
        self.scroll_y = tk.Scrollbar(self.contact_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#efdddd")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        self.display_contacts(self.contacts)

    def make_button(self, text, command):
        btn = tk.Button(self.button_frame, text=text, font=("Segoe UI", 11, "bold"),
                        bg="#6c63ff", fg="white", activebackground="#574fd6", activeforeground="white",
                        relief=tk.FLAT, padx=10, pady=5, command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg="#574fd6"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#6c63ff"))
        return btn

    def display_contacts(self, contact_list):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not contact_list:
            tk.Label(self.scroll_frame, text="No contacts found.", bg="#daa7c6", font=("Segoe UI", 12)).pack(pady=20)
            return

        for idx, contact in enumerate(contact_list):
            frame = tk.Frame(self.scroll_frame, bg="white", bd=1, relief=tk.RIDGE)
            frame.pack(pady=5, padx=10, fill=tk.X)

            name = tk.Label(frame, text=contact['name'], font=("Segoe UI", 13, "bold"), bg="white", anchor="w")
            name.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))

            phone = tk.Label(frame, text="📞 " + contact['phone'], font=("Segoe UI", 11), bg="white", anchor="w")
            phone.grid(row=1, column=0, sticky="w", padx=10)

            email = tk.Label(frame, text="✉ " + contact['email'], font=("Segoe UI", 11), bg="white", anchor="w")
            email.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))

    def add_contact_popup(self):
        self.popup_window("Add Contact", self.add_contact)

    def add_contact(self, win, name, phone, email):
        if not name or not phone or not email:
            messagebox.showwarning("Missing Info", "Please fill out all fields.")
            return
        self.contacts.append({'name': name, 'phone': phone, 'email': email})
        save_contacts(self.contacts)
        messagebox.showinfo("Saved", "Contact added successfully.")
        win.destroy()
        self.display_contacts(self.contacts)

    def edit_contact_popup(self):
        self.index_popup("Edit Contact", self.edit_contact_fields)

    def edit_contact_fields(self, win, idx):
        if idx < 0 or idx >= len(self.contacts):
            messagebox.showerror("Invalid", "Contact does not exist.")
            win.destroy()
            return
        c = self.contacts[idx]
        self.popup_window("Edit Contact", lambda w, n, p, e: self.save_edit(w, idx, n, p, e), c['name'], c['phone'], c['email'])
        win.destroy()

    def save_edit(self, win, idx, name, phone, email):
        self.contacts[idx] = {'name': name, 'phone': phone, 'email': email}
        save_contacts(self.contacts)
        messagebox.showinfo("Updated", "Contact updated.")
        win.destroy()
        self.display_contacts(self.contacts)

    def delete_contact_popup(self):
        self.index_popup("Delete Contact", self.delete_contact)

    def delete_contact(self, win, idx):
        if idx < 0 or idx >= len(self.contacts):
            messagebox.showerror("Invalid", "Contact not found.")
        else:
            deleted = self.contacts.pop(idx)
            save_contacts(self.contacts)
            messagebox.showinfo("Deleted", f"Deleted {deleted['name']}")
        win.destroy()
        self.display_contacts(self.contacts)

    def popup_window(self, title, on_submit, name="", phone="", email=""):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("350x270")
        win.config(bg="#f0c3a5")

        tk.Label(win, text="Name:", font=("Segoe UI", 11), bg="white").pack(pady=(10, 0))
        name_entry = tk.Entry(win, font=("Segoe UI", 11), width=30)
        name_entry.insert(0, name)
        name_entry.pack()

        tk.Label(win, text="Phone:", font=("Segoe UI", 11), bg="white").pack(pady=(10, 0))
        phone_entry = tk.Entry(win, font=("Segoe UI", 11), width=30)
        phone_entry.insert(0, phone)
        phone_entry.pack()

        tk.Label(win, text="Email:", font=("Segoe UI", 11), bg="white").pack(pady=(10, 0))
        email_entry = tk.Entry(win, font=("Segoe UI", 11), width=30)
        email_entry.insert(0, email)
        email_entry.pack()

        tk.Button(win, text="Save", font=("Segoe UI", 11), bg="#2ecc71", fg="white", width=15,
                  command=lambda: on_submit(win, name_entry.get(), phone_entry.get(), email_entry.get())).pack(pady=15)

    def index_popup(self, title, on_submit):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x150")
        win.config(bg="white")

        tk.Label(win, text="Enter Contact Number (1-based):", font=("Segoe UI", 11), bg="white").pack(pady=10)
        idx_entry = tk.Entry(win, font=("Segoe UI", 11), width=20)
        idx_entry.pack()

        tk.Button(win, text="Next", font=("Segoe UI", 11), bg="#e67e22", fg="white", width=12,
                  command=lambda: self.handle_index_submit(win, idx_entry.get(), on_submit)).pack(pady=10)

    def handle_index_submit(self, win, index_str, callback):
        try:
            index = int(index_str) - 1
            callback(win, index)
        except:
            messagebox.showerror("Error", "Please enter a valid number.")

    def filter_contacts(self, *args):
        query = self.search_var.get().strip().lower()
        if not query:
            self.display_contacts(self.contacts)
            return
        filtered = [c for c in self.contacts if query in c['name'].lower()]
        self.display_contacts(filtered)

    def refresh_view(self):
        self.contacts = load_contacts()
        self.display_contacts(self.contacts)

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()
