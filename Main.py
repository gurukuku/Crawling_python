from tkinter import *
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import datetime
import re


fullUrl = re.compile("https?://.*")
twoSlash = re.compile("//[^/]*")
oneSlash = re.compile("/[^/]*")
noSlash = re.compile("[^/]*")
tsHeader = re.compile("[^:]*:")
osHeader = re.compile("[^/]*//[^/]*")


# find img tag with src attribute
def img_has_src(tag):
    return tag.name == "img" and tag.has_attr("src")


# Convert the contents of the src attribute to an accessible URL.
def to_full_url(url):
    if fullUrl.match(url):
        return url
    elif twoSlash.match(url):
        return tsHeader.match(urlText.get()).group() + url
    elif oneSlash.match(url):
        return osHeader.match(urlText.get()).group() + url
    elif noSlash.match(url):
        return urlText.get() + url if urlText.get()[-1] == '/' else urlText.get() + "/" + url
    else:
        return None


def start_crawling():
    # check empty string
    if not urlText.get():
        tkinter.messagebox.showerror("Crawling", "url is empty")
        return

    # check it is url
    try:
        res = requests.get(urlText.get())
    except requests.exceptions.MissingSchema:
        tkinter.messagebox.showerror("Crawling", urlText.get() + " is not url")
        return

    # check accessibility
    if res.status_code != 200:
        tkinter.messagebox.showerror("Crawling", "error : " + str(res.status_code) + "\n" + urlText.get())
        return

    # create save folder ([specified folder]\[current date time])
    save_folder = folderText.get() + "\\" + datetime.datetime.now().strftime("%y%m%d%H%M%S")
    os.makedirs(save_folder)

    img_idx = 1
    html = BeautifulSoup(res.content, "html.parser")  # get html object
    for imgTag in html.find_all(img_has_src):  # find img tag
        full_url = to_full_url(imgTag["src"])  # get image url
        if full_url:  # url is valid
            img_res = requests.get(full_url)
            if img_res.status_code == 200:  # url is accessible.
                urllib.request.urlretrieve(full_url, save_folder + "\\" + "%06d" % img_idx + ".jpg")  # download image
                print(full_url)
                img_idx += 1

    tkinter.messagebox.showinfo("Crawling", "OK")


# change download folder
def change_folder():
    tmp_dir = tkinter.filedialog.askdirectory()
    if tmp_dir:
        folderText.set(tmp_dir)


# ask exit
def check_exit():
    if tkinter.messagebox.askyesno("Crawling", "Exit?"):
        root.destroy()


# root window
root = Tk()
root.title("Crawling")
root.geometry("530x150+300+300")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", check_exit)

# root - url textbox title
urlTitleText = tkinter.Label(root, text="url")
urlTitleText.pack()
urlTitleText.place(x=20, y=5)

# root - url textbox
urlText = StringVar()
urlTextBox = tkinter.ttk.Entry(root, width=50, textvariable=urlText)
urlTextBox.place(x=20, y=30)

# root - start button
startButton = tkinter.ttk.Button(root, text="start", command=start_crawling)
startButton.place(x=400, y=30)

# root - folder textbox title
folderTitleText = tkinter.Label(root, text="folder")
folderTitleText.pack()
folderTitleText.place(x=20, y=60)

# root - folder textbox
folderText = StringVar()
folderTextBox = tkinter.ttk.Entry(root, width=50, textvariable=folderText)
folderTextBox.configure(state="disabled")
folderTextBox.place(x=20, y=85)
folderText.set(os.path.expanduser("~\\Documents\\Crawling"))

# root - change folder button
changeFolderButton = tkinter.ttk.Button(root, text="change", command=change_folder)
changeFolderButton.place(x=400, y=85)

# create default download folder
if not os.path.exists(folderText.get()):
    os.makedirs(folderText.get())

root.mainloop()
