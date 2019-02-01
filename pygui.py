import time, datetime, os, shutil, serial

try:
    import tkinter as tk                # python 3
    from tkinter import font  as tkfont # python 3
    from PIL import Image, ImageTk
except Exception:
    pass


#Serial for Arduino, if not plugged in then no problems
try:
    ser = serial.Serial('/dev/ttyACM0', 9600)
except Exception:
    pass

def showlights():
    try:
        ser.write(bytes('255', 'UTF-8'))
        ser.write(bytes("\n", 'UTF-8'))
    except Exception:
        pass

def offlights():
    try:
        ser.write(bytes('100', 'UTF-8'))
        ser.write(bytes("\n", 'UTF-8'))
    except Exception:
        pass
    
    

    
class ShumstagramApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        self.var = tk.IntVar()
        
        self.wm_title("Shum's Photo Booth")
        self.geometry('800x480')
        self.config(background='black')
        self.attributes("-fullscreen", True)

        self.var.set(16)
        
        
        
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True,)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, PageError):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        frame.update()
    
    def take_photos(self, page_name, template):
        self.show_frame(page_name)
        self.frames['PageTwo'].getPhotoTakingImage()
        for noOfScreen in range(1,5):
            showlights()
            self.frames['PageTwo'].setInstructionScreen(str(noOfScreen))
            time.sleep(10.2)
            self.frames['PageTwo'].getReadyImage()
            time.sleep(3.024)
            self.frames['PageTwo'].getPhotoTakingImage()
            photoCmd = "raspistill -o temp/image" + str(5 - noOfScreen) + ".jpg -t 3000"
            os.system(photoCmd)
            offlights()
            time.sleep(1.5)


        imtemplate = Image.open(template + ".jpg")
        im_1 = Image.open("temp/image1.jpg")
        im_2 = Image.open("temp/image2.jpg")
        im_3 = Image.open("temp/image3.jpg")
        im_4 = Image.open("temp/image4.jpg")
        im_1.thumbnail((825,619))
        im_2.thumbnail((484,363))
        im_3.thumbnail((484,363))
        im_4.thumbnail((484,363))

        new_im = Image.new('RGB', (1748,1181))

        new_im.paste(imtemplate, (0,0))
        new_im.paste(im_1, (825,75))
        new_im.paste(im_2, (98,743))
        new_im.paste(im_3, (632,743))
        new_im.paste(im_4, (1166,743))

        new_im.save("temp/output.jpg")
        time.sleep(0.1)


        #Copy the output file to folder and rename to current time.
        st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H.%M.%S')
        shutil.copy2('temp/output.jpg', 'photos/' + st + '.jpg')

        self.show_frame('PageThree')
        self.frames['PageThree'].updateImage()
    
    def resetStartScreen(self):
        print('Resetting photocount to 16')
        self.var.set(16)
        self.show_frame("StartPage")
    
    def printPhoto(self, page_name):
        oldPrintsLeft = self.var.get()
        self.var.set(oldPrintsLeft - 1)
        self.show_frame(page_name)
        print('Printing... The amount of paper left...')
        print(oldPrintsLeft)
        os.system("lp -d CanonCP1200 temp/output.jpg")
        time.sleep(30)
        if oldPrintsLeft == 0:
            self.show_frame("PageError")
        else:
            self.show_frame("StartPage")



class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config(background='#ffffff')

        self.igm = ImageTk.PhotoImage(file='screens/StartScreen.jpg')
        button2 = tk.Button(self, image=self.igm, borderwidth=0,
                        command=lambda: controller.show_frame("PageOne"))
        button2.pack()



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        image_pil = Image.open("template1.jpg").resize((400, 240), Image.ANTIALIAS) 
        self.igm1 = ImageTk.PhotoImage(image_pil)
        image_pil = Image.open("template2.jpg").resize((400, 240), Image.ANTIALIAS) 
        self.igm2 = ImageTk.PhotoImage(image_pil)
        image_pil = Image.open("template3.jpg").resize((400, 240), Image.ANTIALIAS) 
        self.igm3 = ImageTk.PhotoImage(image_pil)
        image_pil = Image.open("template4.jpg").resize((400, 240), Image.ANTIALIAS) 
        self.igm4 = ImageTk.PhotoImage(image_pil)
        
        button1 = tk.Button(self, image=self.igm1, borderwidth=0, height = 240, width = 400,
                            command=lambda: controller.take_photos("PageTwo",'template1'))
        button2 = tk.Button(self, image=self.igm2, borderwidth=0, height = 240, width = 400,
                            command=lambda: controller.take_photos("PageTwo",'template2'))
        button3 = tk.Button(self, image=self.igm3, borderwidth=0, height = 240, width = 400,
                            command=lambda: controller.take_photos("PageTwo",'template3'))
        button4 = tk.Button(self, image=self.igm4, borderwidth=0, height = 240, width = 400,
                            command=lambda: controller.take_photos("PageTwo",'template4'))

        button1.place(x=0,y=0)
        button2.place(x=400,y=0)
        button3.place(x=0,y=240)
        button4.place(x=400,y=240)
        w = tk.Label(self, text="Select a style")
        w.config(font=("Courier", 44))
        w.place(x=220,y=220)
        

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config(background='#ffffff')
        
        self.img = ImageTk.PhotoImage(Image.open('screens/InstructionScreen1.jpg'))
        self.panel = tk.Label(self, image = self.img)
        self.panel.place(x=0,y=0)
    
    def setInstructionScreen(self,photonumber):
    	print ('Setting Instruction screen '+ photonumber)
    	self.img = ImageTk.PhotoImage(Image.open('screens/InstructionScreen' + photonumber + '.jpg').resize((800, 480), Image.ANTIALIAS))
    	self.panel.configure(image=self.img)
    	self.update()
    
    def getReadyImage(self):
    	print('Setting Ready Image	')
    	self.img = ImageTk.PhotoImage(Image.open('screens/CameraScreen.jpg').resize((800, 480), Image.ANTIALIAS))
    	self.panel.configure(image=self.img)
    	self.update()
    
    def getPhotoTakingImage(self):
    	print('Setting Photo Taking Image	')
    	self.img = ImageTk.PhotoImage(Image.open('screens/CameraScreen2.jpg').resize((800, 480), Image.ANTIALIAS))
    	self.panel.configure(image=self.img)
    	self.update()


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config(background='#ffffff')
        
        self.img = ImageTk.PhotoImage(Image.open('temp/output.jpg').resize((800, 480), Image.ANTIALIAS))
        self.panel = tk.Label(self, image = self.img)
        self.panel.place(x=0,y=0)
        
        
        label = tk.Label(self, text="Happy???", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="No - Start Again", font=controller.title_font,
                           command=lambda: controller.show_frame("StartPage"))
        button.pack(pady=[20,20])
        button2 = tk.Button(self, text="Yes - Print", font=controller.title_font,
                           command=lambda: controller.printPhoto("PageFour"))
        button2.pack(pady=[20,20])
    
    def updateImage(self):
    	self.img = ImageTk.PhotoImage(Image.open('temp/output.jpg').resize((800, 480), Image.ANTIALIAS))
    	self.panel.configure(image=self.img)

class PageFour(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config(background='#ffffff')
        self.img = ImageTk.PhotoImage(Image.open('screens/PrintingScreen.jpg'))
        self.panel = tk.Label(self, image = self.img)
        self.panel.place(x=0,y=0)

class PageError(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.igm = ImageTk.PhotoImage(file='screens/error.jpg')
        button1 = tk.Button(self, image=self.igm, borderwidth=0,
                        command=lambda: controller.resetStartScreen())
        button1.pack()

        

if __name__ == "__main__":
    app = ShumstagramApp()
    app.mainloop()


