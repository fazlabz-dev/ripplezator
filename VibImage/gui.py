import tkinter as tk
from tkinter import filedialog
from tkinter import *

from jpg import *

magick_path, exiftool_path = check_executables()

def ImportImageAction(event=None):
    filename = filedialog.askopenfilename()
    print('Selected:', filename)

    output_path = filedialog.asksaveasfile(defaultextension=".JPG")
    print(output_path)
    if output_path and filename:
        create_thumbnail(filename, output_path.name, magick_path, exiftool_path)

root = tk.Tk()
root.title('Vib-Image')
root.geometry('800x600')

l = Label(root, text = "Vib-Image")
l.config(font=("Verdana", 32))
l.pack()

button = tk.Button(root, text='Open image', command=ImportImageAction)
button.place(relx=0.5, rely=0.5, anchor='center')

root.mainloop()
