import tkinter as tk
from tkinter import Toplevel


class CopyTextWindow:
    def __init__(self, master, txt):
        self.top = Toplevel(master)
        self.top.title("Copy Text Example")
        self.top.geometry("300x150")
        
        self.text_field = tk.Text(self.top, height=5, wrap="word")
        self.text_field.insert("1.0", txt)
        self.text_field.config(state="disabled")  # Make text read-only
        self.text_field.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.close_button = tk.Button(self.top, text="Close", command=self.top.destroy)
        self.close_button.pack(pady=5)
