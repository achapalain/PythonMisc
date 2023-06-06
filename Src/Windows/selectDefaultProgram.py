from tkinter import *
from tkinter import filedialog
import os

master = Tk()
Label(master, text="This is an helper to set an program as default for a extension. Use at your own risk. (It worked well for me as windows as buggy and could not set any default program using regular steps)").grid(row=0, column=1)
Label(master, text="Extension").grid(row=1)
Label(master, text="Program").grid(row=2)

e1 = Entry(master)
e2 = Entry(master, width=80)

e1.grid(row=1, column=1)
e2.grid(row=2, column=1)


def chooseFile():
    master.sourceFile = filedialog.askopenfilename(parent=master, initialdir= "/", title='Please select a directory')
    print(master.sourceFile)
    e2.delete(0,END)
    e2.insert(0, master.sourceFile)


def setDefaultProgram():
    extension = e1.get().replace(".", "")
    execPath = e2.get().replace("/", "\\")
    print("Extension: ." + extension)
    print("Program: " + execPath)
    os.system("REG ADD \"HKCU\\Software\\Classes\\" + e1.get() + "file\\DefaultIcon\" /ve /t REG_SZ /d \"" + execPath + ",0\" /f")
    os.system("REG ADD \"HKCU\\Software\\Classes\\" + e1.get() + "file\\shell\\open\\command\" /ve /t REG_SZ /d \"\\\"" + execPath + "\\\" \\\"%1\\\"\" /f")
    os.system("REG ADD \"HKCU\\Software\\Classes\\." + e1.get() + "\" /ve /t REG_SZ /d \"" + extension + "file\" /f")

b1 = Button(master, text = "Browse", command = chooseFile)
b1.grid(row=2, column=2)

b2 = Button(master, text = "SetAsDefaultProgram", command = setDefaultProgram)
b2.grid(row=3, column=1)

mainloop( )