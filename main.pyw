import tkinter as tk
from tkinter import HORIZONTAL, ttk
import serial
import serial.tools.list_ports
import json
import time
import os

from ptzcamera import Camera

class MainWindow(tk.Frame):
    def __init__(self, parent, app, camera):
        tk.Frame.__init__(self, parent)
        self.grid()
        self.app = app
        self.portsraw = serial.tools.list_ports.comports()
        self.camera = camera
        ports = []
        for x in self.portsraw:
            ports.append(x.name)
        self.selected = tk.StringVar(self)
        index = 0
        c = 0
        if "port" in self.app.config:
            for x in self.portsraw:
                if x.name == self.app.config["port"]:
                    index = c
                    break
                else:
                    c += 1
        self.selected.set(ports[index])
        self.topPanel = tk.Frame(self)
        self.topPanel.grid(column=0, row=0)
        self.select = tk.OptionMenu(self.topPanel, self.selected, *ports, command=lambda evt: self.optioncb(evt))
        self.select.configure(width=8)
        self.select.grid(column=0, row=0)
        self.connectButton = tk.Button(self.topPanel, text="Connect", width=16, command= lambda: self.connectCB(self))
        self.connectButton.grid(column=1, row=0)
        
        self.joystickPanel = JoystickPanel(self, self.camera)
        self.joystickPanel.grid(column=0, row=1)

        self.zoomFrame = tk.Frame(self)
        self.zoomFrame.grid(column=0, row=2)
        self.zoominIcon = tk.PhotoImage(file="icons/outline_zoom_in_black_24dp.png")
        self.zoomoutIcon = tk.PhotoImage(file="icons/outline_zoom_out_black_24dp.png")
        self.zoomOut = tk.Label(self.zoomFrame, image=self.zoomoutIcon)
        self.zoomOut.grid(column=0, row=0)
        self.zoomIn = tk.Label(self.zoomFrame, image=self.zoominIcon)
        self.zoomIn.grid(column=2, row=0)
        self.slider = tk.Scale(self.zoomFrame, from_=0, to=0x40, orient=HORIZONTAL, command=lambda v: self.zoomCB(v))
        self.slider.grid(column=1, row=0)

        self.presets = PresetFrame(self, self.camera)
        self.presets.grid(column=0, row=3)
    def zoomCB(self, value):
        self.camera.zoom(int(value) * 0x100)
        return

    def getDescription(self):
        desc = ""
        for x in self.portsraw:
            if x.name == self.selected.get():
                desc = x.description
        return desc
    def optioncb(self, evt):
        self.app.config["port"] = self.selected.get()
        self.app.saveConfig()
        return
    def connectCB(self,evt):
        self.camera.connect(self.selected.get())
        ret = self.camera.test()        
        if(ret == True):
            self.connectButton.config(bg='#00FF00', text="Connected")
        return


class JoystickPanel(tk.Frame):
    def __init__(self, parent, camera, highlightbackground="black",highlightthickness=1):
        tk.Frame.__init__(self, parent)
        self.camera = camera
        self.leftArrow = tk.PhotoImage(file="icons/outline_west_black_24dp.png")
        self.leftButton = ttk.Button(self, image=self.leftArrow)
        self.leftButton.grid(column=0, row=1)
        self.leftButton.bind("<ButtonRelease>", lambda e: self.camera.stop())
        self.leftButton.bind("<ButtonPress>", lambda e: self.camera.move(-1,0))
        self.rightArrow = tk.PhotoImage(file="icons/outline_east_black_24dp.png")
        self.rightButton = ttk.Button(self, image=self.rightArrow)
        self.rightButton.grid(column=2, row=1)
        self.rightButton.bind("<ButtonRelease>", lambda e: self.camera.stop())
        self.rightButton.bind("<ButtonPress>", lambda e: self.camera.move(1,0))
        self.upArrow = tk.PhotoImage(file="icons/outline_north_black_24dp.png")
        self.upButton = ttk.Button(self, image=self.upArrow)
        self.upButton.grid(column=1, row=0)
        self.upButton.bind("<ButtonRelease>", lambda e: self.camera.stop())
        self.upButton.bind("<ButtonPress>", lambda e: self.camera.move(0,1))
        self.downArrow = tk.PhotoImage(file="icons/outline_south_black_24dp.png")
        self.downButton = ttk.Button(self, image=self.downArrow)
        self.downButton.grid(column=1, row=2)
        self.downButton.bind("<ButtonRelease>", lambda e: self.camera.stop())
        self.downButton.bind("<ButtonPress>", lambda e: self.camera.move(0,-1))
        self.homeImage = tk.PhotoImage(file="icons/outline_filter_tilt_shift_black_24dp.png")
        ttk.Button(self, image=self.homeImage, command=lambda: self.camera.home()).grid(column=1, row=1)
        self.stopImage = tk.PhotoImage(file="icons/outline_stop_circle_black_24dp.png")
        ttk.Button(self, image=self.stopImage, command=lambda: self.camera.stop()).grid(column=0, row=0)
        self.powerImage = tk.PhotoImage(file="icons/bolt_FILL0_wght400_GRAD0_opsz48.png")
        ttk.Button(self, image=self.powerImage, command=lambda: self.camera.togglePower()).grid(column=2, row=0)
        return

class PresetFrame(tk.Frame):
    def __init__(self, parent, cam):
        tk.Frame.__init__(self, parent)
        self.camera = cam

        self.mode = 0 #0 recall, 1 set, 2 delete

        self.one = tk.Button(self, text="1", height=2, width=4, command=lambda: self.numbutton(1))
        self.one.grid(column=0, row=0)
        self.two = tk.Button(self, text="2", height=2, width=4, command=lambda: self.numbutton(2))
        self.two.grid(column=1, row=0)
        self.three = tk.Button(self, text="3", height=2, width=4, command=lambda: self.numbutton(3))
        self.three.grid(column=2, row=0)
        self.four = tk.Button(self, text="4", height=2, width=4, command=lambda: self.numbutton(4))
        self.four.grid(column=0, row=1)
        self.five = tk.Button(self, text="5", height=2, width=4, command=lambda: self.numbutton(5))
        self.five.grid(column=1, row=1)
        self.six = tk.Button(self, text="6", height=2, width=4, command=lambda: self.numbutton(6))
        self.six.grid(column=2, row=1)
        self.seven = tk.Button(self, text="7", height=2, width=4, command=lambda: self.numbutton(7))
        self.seven.grid(column=0, row=2)
        self.eight = tk.Button(self, text="8", height=2, width=4, command=lambda: self.numbutton(8))
        self.eight.grid(column=1, row=2)
        self.nine = tk.Button(self, text="9", height=2, width=4, command=lambda: self.numbutton(9))
        self.nine.grid(column=2, row=2)
        self.zero = tk.Button(self, text="0", height=2, width=4, command=lambda: self.numbutton(0))
        self.zero.grid(column=1, row=3)

        self.set = tk.Button(self, text="Set", height=2, width=4, command=lambda: self.modebuttons(1))
        self.set.grid(column=0, row=3)
        self.del_ = tk.Button(self, text="Del", height=2, width=4, command=lambda: self.modebuttons(2))
        self.del_.grid(column=2, row=3)
    def modebuttons(self, button):
        self.mode = button
        if button == 1:
            self.set.config(bg="#00FF00")
            self.del_.config(bg="#F0F0F0")
        if button == 2:
            self.set.config(bg="#F0F0F0")
            self.del_.config(bg="#00FF00")
        return

    def numbutton(self, number):
        if self.mode == 0:
            self.camera.recallPreset(number)
        elif self.mode == 1:
            self.camera.setPreset(number)
        elif self.mode == 2:
            self.camera.delPreset(number)

        self.mode = 0
        self.set.config(bg="#F0F0F0")
        self.del_.config(bg="#F0F0F0")
        return


class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PTZ")
        self.config = {}
        self.port = "COM1"
        self.loadConfig()
        self.camera = Camera()
        self.main = MainWindow(self.root, self, self.camera)
        self.root.attributes("-topmost", True)
        self.root.resizable(0,0)
        self.root.mainloop()
    def loadConfig(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as jsonfile:
                self.config = json.load(jsonfile)
                jsonfile.close()
    def saveConfig(self):
        with open("config.json", "w") as jsonfile:
            outjson = json.dump(self.config, jsonfile)
            jsonfile.close()

app = MainApplication()