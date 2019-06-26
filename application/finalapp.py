import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, Image, ImageTk
import requests
import base64
import json
import os
import time
import sys
import webbrowser

#create support directory
#find current directory
currentDir = os.getcwd()

supportDir = currentDir + '\support'

#check if directory has been created previously
exists = os.path.isdir(supportDir)
if not(exists):
    os.mkdir(supportDir)#create directory



#coords for screenshot
x1 = 0
y1 = 0
x2 = 0
y2 = 0

hasmedia = False
isScreenshot = False
isSnippingTool = False

image = 0 #will become the image

def screenshot():
    global isScreenshot, hasmedia
    root.geometry('')
    root.withdraw()
    root.quit()
    isScreenshot = True
    #hasmedia = True
    

def picselect():
   root.geometry('')
   snipbutton.destroy()
   screenshotbutton.destroy()
   quitbutton.destroy()
   browsebutton.destroy()
   text.pack()
   #text.config(text = ' After clicking this button, click on the screen two\n more times to create box to capture the desired area.')
   snipbutton2.pack() 
   quitbutton2.pack()

def snip():
   snipbutton.destroy()
   snipbutton2.destroy()
   quitbutton2.destroy()
   text.destroy()
   root.attributes('-alpha', 0.2)
   #root.setWindowOpacity(0.3)
   w = root.winfo_screenwidth()
   h = root.winfo_screenheight()
   root.geometry('%dx%d+0+0' % (w,h)) #sets ui window to cover entire screen
   #root.setGeometry(0,0,w,h)
   root.overrideredirect(True)
   getcoords1()

def getcoords1():
   root.bind('<Button 1>', click1)

def click1(eventorigin): #gets first click
   global x1, y1
   x1 = eventorigin.x
   y1 = eventorigin.y
   #print(x1,y1)
   root.unbind('<Button 1>')
   getcoords2()

def getcoords2():
   root.bind('<Button 1>', click2)

def click2(eventorigin): #gets second click
   global x2, y2, chosepic, isSnippingTool
   x2 = eventorigin.x
   y2 = eventorigin.y
   #print(x2,y2)
   root.unbind('<Button 1>')
   root.attributes('-alpha', 0)
   root.withdraw()
   root.quit() #closes ui
   isSnippingTool = True

def takepic():
    global image, isScreenshot, isSnippingTool, hasmedia, x1, x2, y1, y2
    if(isScreenshot):
        time.sleep(1)
        image = ImageGrab.grab()
        hasmedia = True
        
    if(isSnippingTool):
        #revert window to normal settings
        root.attributes('-alpha', 1)
        root.geometry('')
        root.overrideredirect(False)

        #if the coordinates where taken out of order, swap them
        if(x1 > x2):
            tempint = x1
            x1 = x2
            x2 = tempint
        if(y1 > y2):
            tempint = y1
            y1 = y2
            y2 = tempint
        image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        hasmedia = True

def copy(string):
    root.clipboard_clear()
    root.clipboard_append(string)
    root.update()
    
def browse():
    global supportDir
    thumbnames = []#holds variable part of file name
    thumbnails = []#holds file paths to thumbnails
    thumbtimes = []#holds time in seconds since created
    thumbdates = []#holds creation time as a date
    itr = 0
    dirs = os.listdir(supportDir)
    for file in dirs:
        thumbnames.insert(itr, file.split(".")[0])
        #print(thumbnames[itr])
        thumbnails.insert(itr,(supportDir + '/' + file))
        thumbtimes.insert(itr,(os.path.getctime(supportDir + '/' + file)))
        thumbdates.insert(itr,time.ctime(os.path.getctime(supportDir + '/' + file)))
        itr = itr + 1  


    #sort lists by date
    n = len(thumbtimes)
    for i in range(n):
        for j in range(0,n - i - 1):
            if (thumbtimes[j] < thumbtimes[j+1]):
                thumbnames[j], thumbnames[j+1] = thumbnames[j+1], thumbnames[j]
                thumbnails[j], thumbnails[j+1] = thumbnails[j+1], thumbnails[j]
                thumbtimes[j], thumbtimes[j+1] = thumbtimes[j+1], thumbtimes[j]
                thumbdates[j], thumbdates[j+1] = thumbdates[j+1], thumbdates[j]

    #print(thumbdates)


    global top
    top = tk.Toplevel()
    top.title('Browse')
    root.withdraw()
    
    #outerframe to hold canvas
    outerframe = tk.Frame(top)
    outerframe.grid(row=0, column=0, sticky='nw')

    #canvas to hold innerframe and enable scrolling
    canvas = tk.Canvas(outerframe)
    canvas.grid(row=0, column=0, sticky="news")
 
    #scrollbar
    scroll=tk.Scrollbar(outerframe, orient="vertical", command=canvas.yview)
    scroll.grid(row=0, column=1, sticky='ns')
    canvas.configure(yscrollcommand=scroll.set)

    #innerframe to hold labels and buttons
    innerframe = tk.Frame(canvas)

    canvas.create_window((0, 0), window=innerframe, anchor='nw')

    #back button at top
    backbutton = tk.Button(innerframe, text='Back',command=back)
    backbutton.grid(row=0, column=1)

    copyvar = tk.StringVar()
    copyvar.set('A URL was never selected')

    #another copy wooo
    copybutton = tk.Button(innerframe, text='Copy to clipboard', command= lambda: copy(copyvar.get()))
    copybutton.grid(row=0, column=2)

    r = 0
    row = 1
    urls = []
    if(len(thumbnails) == 0):
        emptylabel = tk.Label(innerframe, text="There are no previous images")
        emptylabel.grid(row=0)
    else:    
        for infile in thumbnails:
            im = Image.open(infile)
            tkimage = ImageTk.PhotoImage(im)
            label1=tk.Label(innerframe,image = tkimage)
            label1.image = tkimage
            label1.grid(row=row,column=0)
            
            #copyvar.set("http://127.0.0.1:5000/picture/" + thumbnames[r])
            #copybutton = tk.Button(innerframe, text='Copy to clipboard', command= lambda: copy(copyvar.get()))
            #copybutton.grid(row=row, column=2)
            #label2=tk.Label(innerframe,textvariable="http://127.0.0.1:5000/picture/" + thumbnames[r])
            #label2.grid(row=row, column=1)

            urls.insert(r, "http://127.0.0.1:5000/picture/" + thumbnames[r])
            label1.bind("<Button-1>", lambda event, arg= urls[r]: open_url(event, arg))
            
            r = r + 1
            row = row + 1

        for i in range(len(urls)):
            rb = tk.Radiobutton(innerframe, text= "http://127.0.0.1:5000/picture/" + thumbnames[i], variable = copyvar, value=urls[i])
            rb.grid(row=i+1, column=1)


    #back button on bottom
    backbutton2 = tk.Button(innerframe, text='Back',command=back)
    backbutton2.grid(row=row, column=1)

    #copy button next to back button
    copybutton = tk.Button(innerframe, text='Copy to clipboard', command= lambda: copy(copyvar.get()))
    copybutton.grid(row=row, column=2)
    
    innerframe.update_idletasks()
    #config window size
    canvas.config(width=800, height=400)

    canvas.config(scrollregion=canvas.bbox("all"))

def back():
    root.deiconify()
    top.destroy()

def back2():
    root.deiconify()
    renameTop.destroy()

def open_url(event, arg):
    #open url in browser
    webbrowser.open_new(arg)
    #print(arg)

def renameWindow():
    global renameTop, entry
    renameTop = tk.Toplevel()
    root.withdraw()

    label = tk.Label(renameTop, text='Input new name')
    label.grid(row=0)
    entry = tk.Entry(renameTop)
    entry.grid(row=0, column=1)
    submitbutton = tk.Button(renameTop, text='Submit', command=submit)
    submitbutton.grid(row=1, column=1)
    back2button = tk.Button(renameTop, text='back', command=back2)
    back2button.grid(row=1, column=0)

def submit():
    url = 'http://127.0.0.1:5000/picture/namechange'
    
    userinput = entry.get()#gets text from form
    uuid = filename
    #prepare json
    data = {'uuid': uuid, 'userinput': userinput}
    #print(data)
    res = requests.post(url, data=data)
    if res.ok:
        response = res.text
        if (response == 'good'):
            oldfilepath = 'support/' + filename + '.jpg'
            newfilepath = 'support/' + userinput + '.jpg'
            os.rename(oldfilepath, newfilepath)
            resurl = 'http://127.0.0.1:5000/picture/' + userinput
            var.set(resurl)
            tk.messagebox.showinfo('Nice', 'The name has been succesfully changed')
            root.update()
            back2()
        else:
            tk.messagebox.showerror('Failed', 'The name you chose is unavailable, please try another one.')
            #error
    else:
        tk.messagebox.showerror('Error', 'The request to the server failed')
    
def restart():
    os.execv(sys.executable, ['python'] + sys.argv)




root = tk.Tk()
root.geometry('210x160')
snipbutton2 = tk.Button(root, text='Snip!', width=17, command = snip) #button not shown yet
quitbutton2 = tk.Button(root, text='Quit', fg="red", command=root.quit) #button not shown yet
snipbutton = tk.Button(root, text = 'Snipping Tool', width=21, command = picselect)
snipbutton.pack()
screenshotbutton = tk.Button(root, text = 'Screenshot', width=21, command = screenshot)
screenshotbutton.pack()
browsebutton = tk.Button(root, text='Browse previous pictures', width=21, command=browse)
browsebutton.pack()
quitbutton = tk.Button(root, text='Quit', fg="red", command=root.quit)
quitbutton.pack()
text = tk.Label(root, text='After clicking this button, click on the screen two\n more times to create box to capture the desired area.'  , justify=tk.LEFT, padx=20, pady=5)
root.mainloop()

#anything after this will only run if the root is quit

takepic()

if not(hasmedia):
    #print(hasmedia)
    sys.exit(0)

resurl = 'resurl' #becomes the url from the response



if(hasmedia):
    image.save('tmp.jpg')
    url = 'http://127.0.0.1:5000/picture/post'
    with open('tmp.jpg', 'rb') as image:
        imagestr = base64.b64encode(image.read())

    res = requests.post(url, data=imagestr)
    if res.ok:
        response = res.json()
        resurl = response['url']
        #print(resurl)
        
    else:
        tk.messagebox.showerror('Error', 'The request to the server failed')
        resurl = 'bad response'

#create thumbnail of image for browsing
global filename
if not(resurl == 'bad response'):
    filename = resurl.split('/')[4]

image = Image.open('tmp.jpg')
thumbnail = image.resize((100, 100))
thumbnail.save(supportDir + '/' + filename + '.jpg')


#rebuild GUI
#clear window of all buttons and such
for widget in root.winfo_children():
    widget.destroy()

#make some new buttons
global var
var = tk.StringVar()
var.set(resurl)
text2 = tk.Label(root, textvariable=var, pady=5)
copybutton = tk.Button(root, text='Copy to clipboard', command= lambda: copy(var))
quitbutton3 = tk.Button(root, text='Quit', fg='red', command= root.quit)
browsebutton2 = tk.Button(root, text='Browse previous pictures', command=browse)
renamebutton = tk.Button(root, text='Rename URL', command=renameWindow)
restartbutton = tk.Button(root, text='Restart', command=restart)


#make those new buttons appear
text2.pack()
copybutton.pack()
renamebutton.pack()
restartbutton.pack()
browsebutton2.pack()
quitbutton3.pack()


root.deiconify()

root.mainloop()
    