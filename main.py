import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, PhotoImage, ttk
import time
from face_detector import main_app  
from classifier import train_classifer
from dataset import start_capture
from AGEprediction import emotion, ageAndgender

names = set()

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1, font=("helvetica", 10, "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class MainUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        global names
        with open("nameslist.txt", "r") as f:
            x = f.read()
            z = x.rstrip().split(" ")
            for i in z:
                names.add(i)
        self.title_font = tkfont.Font(family='Helvetica', size=16, weight="bold")
        self.title("Face Recognizer")
        self.resizable(False, False)
        self.geometry("600x300")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.active_name = None
        container = tk.Frame(self)
        container.grid(sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, SignUpPage, DataCapturePage, FaceRecognition, AGEDetection, HelpPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.status = tk.StringVar()
        self.status.set("Welcome to Face Recognizer")
        status_bar = tk.Label(self, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(sticky="ew", row=1, column=0)
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def update_status(self, message):
        self.status.set(message)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure?"):
            global names
            f = open("nameslist.txt", "a+")
            for i in names:
                f.write(i + " ")
            self.destroy()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        render = PhotoImage(file='homepagepic.png')
        img = tk.Label(self, image=render)
        img.image = render
        img.grid(row=0, column=1, rowspan=5, sticky="nsew", padx=20, pady=20)
        label = tk.Label(self, text="        Home Page        ", font=self.controller.title_font, fg="#263942")
        label.grid(row=0, sticky="ew", padx=10, pady=10)
        button1 = self.create_button("   Face Recognition System  ", lambda: self.controller.show_frame("SignUpPage"))
        button2 = self.create_button("   Age, Gender and Emotion Detection  ", lambda: self.controller.show_frame("AGEDetection"))
        button3 = self.create_button("Quit", self.on_closing, bg="#ffffff", fg="#263942")
        button4 = self.create_button("Help", lambda: self.controller.show_frame("HelpPage"), bg="#41B06E")
        button1.grid(row=1, column=0, ipady=3, ipadx=7, padx=10, pady=5)
        button2.grid(row=2, column=0, ipady=3, ipadx=2, padx=10, pady=5)
        button4.grid(row=3, column=0, ipady=3, ipadx=32, padx=10, pady=5)
        button3.grid(row=4, column=0, ipady=3, ipadx=32, padx=10, pady=5)

    def create_button(self, text, command, bg="#41B06E", fg="#ffffff"):
        button = tk.Button(self, text=text, fg=fg, bg=bg, command=command)
        button.bind("<Enter>", lambda e: button.config(bg="#345"))
        button.bind("<Leave>", lambda e: button.config(bg=bg))
        return button

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure?"):
            global names
            with open("nameslist.txt", "w") as f:
                for i in names:
                    f.write(i + " ")
            self.controller.destroy()


class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="Enter the name", fg="#263942", font='Helvetica 12 bold').grid(row=0, column=0, pady=10, padx=5)
        self.user_name = tk.Entry(self, borderwidth=3, bg="lightgrey", font='Helvetica 11')
        self.user_name.grid(row=0, column=1, pady=10, padx=10)
        self.buttoncanc = self.create_button("Cancel", lambda: controller.show_frame("StartPage"))
        self.buttonext = self.create_button("Next", self.start_training)
        self.buttonclear = self.create_button("Clear", self.clear)
        self.buttoncanc.grid(row=1, column=0, pady=10, ipadx=5, ipady=4)
        self.buttonext.grid(row=1, column=1, pady=10, ipadx=5, ipady=4)
        self.buttonclear.grid(row=1, ipadx=5, ipady=4, column=2, pady=10)
        Tooltip(self.user_name, "Enter the user's name")

    def create_button(self, text, command, bg="#41B06E", fg="#ffffff"):
        button = tk.Button(self, text=text, fg=fg, bg=bg, command=command)
        button.bind("<Enter>", lambda e: button.config(bg="#345"))
        button.bind("<Leave>", lambda e: button.config(bg=bg))
        return button

    def start_training(self):
        global names
        if self.user_name.get() == "None":
            messagebox.showerror("Error", "Name cannot be 'None'")
            return
        elif self.user_name.get() in names:
            messagebox.showerror("Error", "User already exists!")
            return
        elif len(self.user_name.get()) == 0:
            messagebox.showerror("Error", "Name cannot be empty!")
            return
        name = self.user_name.get()
        names.add(name)
        self.controller.active_name = name
        self.controller.frames["AGEDetection"].refresh_names()
        self.controller.show_frame("DataCapturePage")

    def clear(self):
        self.user_name.delete(0, 'end')


class DataCapturePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.numimglabel = tk.Label(self, text="Number of images captured = 0", font='Helvetica 12 bold', fg="#263942")
        self.numimglabel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        self.capturebutton = self.create_button("Capture Data Set", self.capimg)
        self.trainbutton = self.create_button("Train The Model", self.trainmodel)
        self.capturebutton.grid(row=1, column=0, ipadx=5, ipady=4, padx=10, pady=20)
        self.trainbutton.grid(row=1, column=1, ipadx=5, ipady=4, padx=10, pady=20)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=2, column=0, columnspan=2, pady=10)

    def create_button(self, text, command, bg="#41B06E", fg="#ffffff"):
        button = tk.Button(self, text=text, fg=fg, bg=bg, command=command)
        button.bind("<Enter>", lambda e: button.config(bg="#345"))
        button.bind("<Leave>", lambda e: button.config(bg=bg))
        return button

    def capimg(self):
        self.controller.update_status("Capturing images...")
        self.numimglabel.config(text=str("Captured Images = 0 "))
        messagebox.showinfo("INSTRUCTIONS", "We will Capture 300 pics of your Face.")
        x = start_capture(self.controller.active_name)
        self.controller.num_of_images = x
        self.numimglabel.config(text=str("Number of images captured = " + str(x)))
        self.controller.update_status("Image capture complete.")

    def trainmodel(self):
        if self.controller.num_of_images < 300:
            messagebox.showerror("ERROR", "Not enough Data, Capture at least 300 images!")
            return
        self.controller.update_status("Training the model...")
        self.progress.start(10)
        self.after(100, self._train_model)

    def _train_model(self):
        train_classifer(self.controller.active_name)
        self.progress.stop()
        messagebox.showinfo("SUCCESS", "The model has been successfully trained!")
        self.controller.update_status("Model training complete.")
        self.controller.show_frame("FaceRecognition")


class FaceRecognition(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Face Recognition", font='Helvetica 16 bold')
        label.grid(row=0, column=0, sticky="ew", pady=10)
        button1 = self.create_button("Face Recognition", self.openwebcam)
        button2 = self.create_button("Go to Home Page", lambda: self.controller.show_frame("StartPage"), bg="#ffffff", fg="#263942")
        button1.grid(row=1, column=0, sticky="ew", ipadx=5, ipady=4, padx=10, pady=10)
        button2.grid(row=2, column=0, sticky="ew", ipadx=5, ipady=4, padx=10, pady=10)

    def create_button(self, text, command, bg="#41B06E", fg="#ffffff"):
        button = tk.Button(self, text=text, fg=fg, bg=bg, command=command)
        button.bind("<Enter>", lambda e: button.config(bg="#345"))
        button.bind("<Leave>", lambda e: button.config(bg=bg))
        return button

    def openwebcam(self):
        self.controller.update_status("Opening webcam...")
        main_app(self.controller.active_name)
        self.controller.update_status("Webcam closed.")


class AGEDetection(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="User Options", font='Helvetica 16 bold')
        label.grid(row=0, column=0, sticky="ew", pady=10)
        button2 = self.create_button("Emotion Detection", self.emot)
        button3 = self.create_button("Gender and Age Prediction", self.gender_age_pred)
        button4 = self.create_button("Go to Home Page", lambda: self.controller.show_frame("StartPage"), bg="#ffffff", fg="#263942")
        button2.grid(row=1, column=0, sticky="ew", ipadx=5, ipady=4, padx=10, pady=10)
        button3.grid(row=1, column=1, sticky="ew", ipadx=5, ipady=4, padx=10, pady=10)
        button4.grid(row=2, column=0, sticky="ew", ipadx=5, ipady=4, padx=10, pady=10, columnspan=2)

    def create_button(self, text, command, bg="#41B06E", fg="#ffffff"):
        button = tk.Button(self, text=text, fg=fg, bg=bg, command=command)
        button.bind("<Enter>", lambda e: button.config(bg="#345"))
        button.bind("<Leave>", lambda e: button.config(bg=bg))
        return button

    def gender_age_pred(self):
        ageAndgender()

    def emot(self):
        emotion()

    def refresh_names(self):
        global names
        pass


class HelpPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Help Page", font=self.controller.title_font)
        label.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
        help_text = (
            "Steps to use the features in this app:\n\n"
            "1. Face Recognition System:\n"
            "   - Go to 'Face Recognition System' from the Home Page.\n"
            "   - Enter your name and click 'Next'.\n"
            "   - Capture your face images and train the model.\n"
            "   - Start face recognition.\n\n"
            "2. Age, Gender and Emotion Detection:\n"
            "   - Go to 'Age, Gender and Emotion Detection' from the Home Page.\n"
            "   - Select either 'Emotion Detection' or 'Gender and Age Prediction'.\n"
            "   - Follow the instructions to detect emotion or predict age and gender."
        )
        help_label = tk.Label(self, text=help_text, justify="left", padx=10, pady=10)
        help_label.grid(row=1, column=0, sticky="w", padx=10)
        button = self.create_button("Back to Home Page", lambda: self.controller.show_frame("StartPage"))
        button.grid(row=2, column=0, pady=10)

    def create_button(self, text, command, bg="#41B06E", fg="#ffffff"):
        button = tk.Button(self, text=text, fg=fg, bg=bg, command=command)
        button.bind("<Enter>", lambda e: button.config(bg="#345"))
        button.bind("<Leave>", lambda e: button.config(bg=bg))
        return button


app = MainUI()
app.iconphoto(True, tk.PhotoImage(file='icon.ico'))
app.mainloop()
