'''
Cyrus' Password Generator
by Cyrus Stonebanks (2026)

Icon made by Freepik from www.flaticon.com

Docstring for passwordGenerator
'''

import random
import string
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import sv_ttk
import os
import sys
from cryptography.fernet import Fernet

def generatePassword(size, specialChars, digitsChars,  upperChars, lowerChars):      # Generates a random password based on the given criteria
    
    output.delete(1.0, tk.END)                  # Clear previous output

    letterBank = ''                      # Initialize an empty string to hold possible characters

    if specialChars:                            # Adds certain character types to the letter bank based on user preferences
        letterBank += string.punctuation
    if digitsChars:
        letterBank += string.digits
    if lowerChars:
        letterBank += string.ascii_lowercase
    if upperChars:
        letterBank += string.ascii_uppercase

    password = ''                      # Initialize an empty string to hold the generated password

    for i in range(size):                               # Loop to generate password of specified size
        x = random.randrange(len(letterBank))
        password += letterBank[x]

    print("Generated Password: ", password)         # Print the generated password to the console for debugging
    return password

def savePassword(password):                     # Saves the generated password to the listbox if it's not already present
    
    if password in passList.get(0, tk.END):     # Check for duplicates
        messagebox.showwarning("Duplicate Password", "This password is already saved.")
        return

    if password != "\n":                         # Avoid saving empty passwords
        passList.insert(tk.END, password)
    else:
        messagebox.showwarning("No Password", "No password to save.")
    
def validateCheckboxes(box):                  # Returns a function that ensures at least one checkbox is always selected
    
    def check():                            # Use a list to avoid referencing variables before they're defined
        all_vars = [specialVar, digitVar, upperVar, lowerVar]
        checked_count = sum([v.get() for v in all_vars])
        
        if checked_count == 0:
            box.set(True)  # Re-check the box that was just unchecked
    return check

def exportPasswords(passwords):                # Exports the saved passwords to a text file
    
    if len(passwords) == 0:                     # Warn the user if there are no passwords to export
        messagebox.showwarning("No Passwords", "No passwords to export. Please save some passwords first.")
        return
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ask user for file location using file dialog
    file_path = filedialog.asksaveasfilename(
        initialdir=script_dir,
        initialfile="saved_passwords.txt",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if not file_path:  # User cancelled
        return
    
    try:
        with open(file_path, "w") as file:
            for password in passwords:
                file.write(password + "\n")
        
        messagebox.showinfo("Export Successful", f"Passwords exported to:\n{file_path}")
        print(f"Passwords exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Failed", f"Failed to export passwords:\n{str(e)}")
        print(f"Error exporting passwords: {e}")

def encryptFile(file_path):

    result = messagebox.askyesno("Encrypt File", "Does this file already have an encryption key? If not, a new key will be generated and you will be prompted to save it.")
    
    if result == False:
        # Generate a new encryption key
        messagebox.showinfo("Save Key File", "Please choose a location to save the new encryption key.\nNote: You will need this key to decrypt the file later, so keep it in a safe place.")
        key = Fernet.generate_key()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = filedialog.asksaveasfilename(
            initialdir=script_dir,
            initialfile="file_key.key",
            defaultextension=".key",
            filetypes=[("Key files", "*.key"), ("All files", "*.*")]
        )
        
        if not key_path:  # User cancelled
            messagebox.showwarning("Encryption Cancelled", "No key file selected. Encryption cancelled.")
            return
        
        # Save the new encryption key to a file
        with open(key_path, "wb") as key_file:
            key_file.write(key)
    else:
        # Use an existing encryption key
        messagebox.showinfo("Select Key File", "Please select the existing key file to use for encryption.")
        key_path = filedialog.askopenfilename(title="Select existing key file", filetypes=[("Key files", "*.key"), ("All files", "*.*")])
        if not key_path:
            messagebox.showwarning("No Key Selected", "No key file selected. Encryption cancelled.")
            return
        
        # Read the existing encryption key from the file
        with open(key_path, "rb") as key_file:
            key = key_file.read()

    fernet = Fernet(key)  # Create a Fernet object with the encryption key

    with open(file_path, "rb") as original_file:
        original = original_file.read()  # Read the original file data

    encrypted = fernet.encrypt(original)  # Encrypt the file data

    with open(file_path, "wb") as encrypted_file:
        encrypted_file.write(encrypted)  # Write the encrypted data back to the file

    messagebox.showinfo("Encryption Successful", f"File encrypted successfully.\nEncryption key saved to:\n{key_path}")
    
def decryptFile(file_path, key_path):
    
    with open(key_path, "rb") as key_file:
        key = key_file.read()  # Read the encryption key from the file

    fernet = Fernet(key)  # Create a Fernet object with the encryption key

    with open(file_path, "rb") as encrypted_file:
        encrypted = encrypted_file.read()  # Read the encrypted file data

    try:
        decrypted = fernet.decrypt(encrypted)  # Decrypt the file data
    except Exception as e:
        messagebox.showerror("Decryption Failed", f"Failed to decrypt file:\n{str(e)}")
        print(f"Error decrypting file: {e}")
        return

    with open(file_path, "wb") as decrypted_file:
        decrypted_file.write(decrypted)  # Write the decrypted data back to the file

    messagebox.showinfo("Decryption Successful", "File decrypted successfully.")

def encryptFilePrompt():    # Wrapper function that shows info message before prompting for file selection
    
    message = """You will be asked to:

1. Select the file you want to encrypt
2. Choose if you have an existing encryption key
3. If NO: Choose where to save a new encryption key
4. If YES: Select your existing key file

The selected file will be encrypted and overwritten.

IMPORTANT: Keep your encryption key safe - you'll need it to decrypt the file!"""
    
    result = messagebox.askokcancel("Encrypt File", message)
    
    if not result:
        messagebox.showwarning("Encryption Cancelled", "Encryption cancelled by user.")
        return

    file_path = filedialog.askopenfilename(title="Select file to encrypt")
    
    if file_path:
        encryptFile(file_path)
    else:
        messagebox.showwarning("No File Selected", "No file selected. Encryption cancelled.")

def decryptFilePrompt():    # Wrapper function that shows info message before prompting for file selection
    
    message = """You will be asked to:

1. Select the encrypted file you want to decrypt
2. Select the encryption key file (.key) for that file

The encrypted file will be decrypted and overwritten with the original content.

Make sure you select the correct key file!"""
    
    result = messagebox.askokcancel("Decrypt File", message)
    
    if not result:
        messagebox.showwarning("Decryption Cancelled", "Decryption cancelled by user.")
        return

    file_path = filedialog.askopenfilename(title="Select file to decrypt")
    if file_path:
        key_path = filedialog.askopenfilename(title="Select key file", filetypes=[("Key files", "*.key"), ("All files", "*.*")])
        if key_path:
            decryptFile(file_path, key_path)
    else:
        messagebox.showwarning("No File Selected", "No file selected. Decryption cancelled.")

def resource_path(relative_path):   # Gets the absolute path to icon file

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.geometry("600x300")                        # Main window setup
root.title("Cyrus' Password Generator")


try:                                        # Set the window icon using resource path
    icon_path = resource_path("key.ico")
    root.iconbitmap(icon_path)
except:
    pass                                    # Continue without icon if file not found

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

sv_ttk.set_theme("light")                      # Set the theme for the application using sv_ttk

frame = tk.Frame(root)
frame.grid(row=0, column=0)

frame.columnconfigure(0, weight=1, uniform="col")
frame.columnconfigure(1, weight=1, uniform="col")
frame.columnconfigure(2, weight=1, uniform="col")
frame.columnconfigure(3, weight=1, uniform="col")
frame.rowconfigure(0, weight=2)

output = tk.Text(frame, height=1, width=34)         # Text widget to display the generated password
output.grid(row=0, column=0, columnspan=3, sticky="ew")

textSize = tk.IntVar(value=12)                      # Variable to hold the desired password length, defaulting to 12

# Scale widget to allow the user to select the desired password length, ranging from 8 to 32 characters
textScale = tk.Scale(root, variable=textSize, from_=8, to=32, orient=tk.HORIZONTAL, label="Password Length")
textScale.grid(row=3, column=0, columnspan=4, sticky="ew")

specialVar = tk.BooleanVar(value=True)          # Checkbox for including special characters, defaulting to True
specialCheck = tk.Checkbutton(frame, text="Special", width=12, anchor="w", cursor="hand2", variable=specialVar, command= validateCheckboxes(specialVar))
specialCheck.grid(row=3, column=0)

digitVar = tk.BooleanVar(value=True)            # Checkbox for including digits, defaulting to True
digitCheck = tk.Checkbutton(frame, text="Digits", width=12, anchor="w", cursor="hand2", variable=digitVar, command=validateCheckboxes(digitVar))
digitCheck.grid(row=3, column=1)

upperVar = tk.BooleanVar(value=True)            # Checkbox for including uppercase letters, defaulting to True
upperCheck = tk.Checkbutton(frame, text="Uppercase", width=12, anchor="w", cursor="hand2", variable=upperVar, command=validateCheckboxes(upperVar))
upperCheck.grid(row=3, column=2)

lowerVar = tk.BooleanVar(value=True)            # Checkbox for including lowercase letters, defaulting to True
lowerCheck = tk.Checkbutton(frame, text="Lowercase", width=12, anchor="w", cursor="hand2", variable=lowerVar, command=validateCheckboxes(lowerVar))
lowerCheck.grid(row=3, column=3)

genBut = tk.Button(frame, text="Generate", cursor="hand2", command=lambda: output.insert(tk.END, generatePassword(textSize.get(), specialVar.get(), digitVar.get(), upperVar.get(), lowerVar.get())))
genBut.grid(row=0, column=4)            # Generates a new password based on the current settings and displays it in the output text widget when clicked

saveBut = tk.Button(frame, text="Save", cursor="hand2", command=lambda: savePassword(output.get(1.0, tk.END)))
saveBut.grid(row=4, column=4)           # Saves the currently displayed password to the listbox if it's not empty and not already saved when clicked

clearBut = tk.Button(frame, text="Clear", cursor="hand2", command=lambda: passList.delete(0, tk.END))
clearBut.grid(row=5, column=4)      # Clears all saved passwords from the listbox when clicked

exportBut = tk.Button(frame, text="Export", cursor="hand2", command=lambda: exportPasswords(passList.get(0, tk.END)))
exportBut.grid(row=6, column=4)     # Exports the saved passwords to a text file when clicked, prompting the user to choose a location and filename

encryptBut = tk.Button(frame, text="Encrypt", cursor="hand2", command=encryptFilePrompt)
encryptBut.grid(row=7, column=4)    # Prompts the user to select a file to encrypt and then encrypts it using the Fernet encryption method when clicked

decrtyptBut = tk.Button(frame, text="Decrypt", cursor="hand2", command=decryptFilePrompt)
decrtyptBut.grid(row=8, column=4)   # Prompts the user to select a file to decrypt and a key file, then decrypts the selected file using the Fernet decryption method when clicked

passList = tk.Listbox(frame)                # Listbox to display saved passwords, allowing the user to see and manage their saved passwords
passList.grid(row=4, column=0, columnspan=4, rowspan=5, sticky="ew")
passList.configure(bg="lightyellow")



root.mainloop()

