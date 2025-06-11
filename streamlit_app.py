import streamlit as st

st.title("Emotionplot")
st.write(
    "Instructions for user."
)

import tkinter as tk

def submit():
    link = link_entry.get()
    number = number_entry.get()
    print(f"Link: {link}")
    print(f"Number: {number}")

# Create the main window
root = tk.Tk()
root.title("User Input Interface")

# Create and place widgets
tk.Label(root, text="Enter Link:").pack(pady=5)
link_entry = tk.Entry(root, width=50)
link_entry.pack(pady=5)

tk.Label(root, text="Enter Number:").pack(pady=5)
number_entry = tk.Entry(root, width=50)
number_entry.pack(pady=5)

submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.pack(pady=10)

# Run the GUI loop
root.mainloop()
