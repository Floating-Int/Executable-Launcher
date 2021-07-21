import tkinter as tk
import os, subprocess
import json
from types import MethodType
from typing import Any


class TkCommand:
    """
    Similar to a lambda function calling a function with 1 argument \n
    Creates a unique instance
    """
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
    
    def __call__(self):
        self.func(self.arg)



class InputField(tk.Entry):
    def __init__(self, master: Any=None, placeholder: str="", on_enter_pressed: MethodType=lambda text: (), autoreset: bool=True, autoclear: bool = True, ignore_placeholder: bool = True, cnf={}, **kw):
        self.placeholder = placeholder
        self.on_enter_pressed = on_enter_pressed
        self.autoreset = autoreset
        self.autoclear = autoclear
        self.ignore_placeholder = ignore_placeholder
        self._clicked = False
        super().__init__(master=master, cnf=cnf, **kw)
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        # bind events
        self.bind("<Button-1>", lambda _event: self._on_clicked())
        self.bind("<Return>", lambda _event: self._on_enter_pressed())

    def _on_clicked(self):
        if self._clicked:
            return
        self._clicked = True
        if self.autoclear:
            self.delete(0, tk.END)
            self.insert(0, "")
    
    def _on_enter_pressed(self): # local
        if not self._clicked:
            return
        text = self.get()
        self.on_enter_pressed(text) # call attribute
        if self.autoreset:
            self.delete(0, tk.END)
            self.insert(0, "")
    
    def reset(self):
        """Resets placeholder"""
        self._clicked = False
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
    
    def is_empty(self):
        if self.get() == "":
            return True
        elif not self.ignore_placeholder:
            return False
        elif self.get() == self.placeholder:
            return True
        return False






class App(tk.Tk):

    def __init__(self, title, favicon=None, width=400, height=600):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        if favicon != None:
            self.iconbitmap(favicon)
        # bind events
        self.bind("<Button-3>", lambda _event: self.hide_all())
        
        # get data
        # NOTE: var 'data' is a key:value pair containg app name and path
        try:
            file = open("data.json", "r")
            self.data = json.load(file)

        except FileNotFoundError: # save default data if the file is not found
            file = open("data.json", "w")
            self.data = {}
            json.dump(self.data, file)
        
        finally:
            file.close()
        
        # background color
        self.config(bg="#252525")

        # -- menus --
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        # app menu
        self.app_menu = tk.Menu(self.menubar, tearoff=0)
        for app, path in self.data.items():
            exist = os.path.exists(path) and path.endswith(".exe")
            cmd = TkCommand(self.launch, path)
            self.app_menu.add_command(label=("" if exist else "x ") + app, command=cmd)
        self.menubar.add_cascade(label="Apps", menu=self.app_menu)

        # add menu
        def submit(_text): # 'on_enter_pressed' command
            if not self.input_field_name.is_empty() and not self.input_field_path.is_empty(): # name and path
                name = self.input_field_name.get()
                path = self.input_field_path.get()
                self.data[name] = path.replace("\\", "/") # store data
                # add app to app menu
                exist = os.path.exists(path) and path.endswith(".exe")
                app_cmd = TkCommand(self.launch, path)
                config_cmd = TkCommand(self.edit, (name, path)) # pack (app, path) tuple
                self.app_menu.add_command(label=("" if exist else "x ") + name, command=app_cmd)
                self.config_menu.add_command(label=("" if exist else "x ") + name, command=config_cmd)
                self.save_data() # save data to .json
                # reset for next time
                self.input_field_name.reset()
                self.input_field_path.reset()
                # hide
                self.input_field_name.pack_forget(),
                self.input_field_path.pack_forget()
        # init input fields
        self.input_field_name = InputField(self, "Enter name:", submit, False) # name field
        self.input_field_path = InputField(self, "Enter path:", submit, False) # path field
        self.menubar.add_command(label="Add", command=lambda: ( # multiple function calls with lambda
            self.input_field_name.pack(),
            self.input_field_path.pack(),
            # reset placeholders
            self.input_field_name.reset(),
            self.input_field_path.reset(),
            # hide other
            self.input_name_edit.pack_forget(),
            self.input_path_edit.pack_forget()
        ))
        
        # config meny
        def submit_config(_text): # 'on_enter_pressed' command
            if not self.input_name_edit.is_empty() and not self.input_path_edit.is_empty(): # name and path
                name = self.input_name_edit.get()
                path = self.input_path_edit.get()
                self.data[name] = path.replace("\\", "/") # fix path
                # add app to app menu
                exist = os.path.exists(path) and path.endswith(".exe")
                app_cmd = TkCommand(self.launch, path)
                config_cmd = TkCommand(self.edit, (name, path)) # pack (app, path) tuple
                self.app_menu.add_command(label=("" if exist else "x ") + name, command=app_cmd)
                self.config_menu.add_command(label=("" if exist else "x ") + name, command=config_cmd)
                # remove old one
                index = list(self.data.keys()).index(self.edit_name)
                self.app_menu.delete(index)
                self.config_menu.delete(index)
                # change data
                del self.data[self.edit_name] # deletes key:value of old name:path
                self.save_data() # save data to .json
                # set placeholders
                self.input_name_edit.placeholder = name
                self.input_path_edit.placeholder = path
                # reset for next time
                self.input_name_edit.reset()
                self.input_path_edit.reset()
                # hide
                self.input_name_edit.pack_forget()
                self.input_path_edit.pack_forget()
        # init sub menu
        self.config_menu = tk.Menu(self.menubar, tearoff=0)
        for app, path in self.data.items():
            exist = os.path.exists(path) and path.endswith(".exe")
            cmd = TkCommand(self.edit, (app, path)) # pack (app, path) tuple
            self.config_menu.add_command(label=("" if exist else "x ") + app, command=cmd)
        # init input fields
        self.input_name_edit = InputField(self, "Enter name:", submit_config, False, False, False) # name field
        self.input_path_edit = InputField(self, "Enter path:", submit_config, False, False, False) # path field
        self.menubar.add_cascade(label="Config", menu=self.config_menu)

        # hide command
        self.menubar.add_command(label="  x  ", command=self.hide_all)



    def launch(self, program_path): # launch a .exe file
        print("Launched")
        self.hide_all() # hides all input fields
        if not os.path.exists(program_path):
            return
        self.withdraw() # hide
        #subprocess.Popen([program_path])
        subprocess.call([program_path])
        self.deiconify() # show after app is closed
    
    
    def save_data(self):
        file = open("data.json", "w")
        json.dump(self.data, file)
    

    def edit(self, tuple): # used in config menu
        name, path = tuple # unpack
        # show input fields
        self.input_name_edit.pack()
        self.input_path_edit.pack()
        # hide other
        self.input_field_name.pack_forget()
        self.input_field_path.pack_forget()
        # set placeholders
        self.input_name_edit.placeholder = name
        self.input_path_edit.placeholder = path
        # activate placeholders
        self.input_name_edit.reset()
        self.input_path_edit.reset()
        # store last app and path
        self.edit_name = name
        self.edit_path = path
    

    def hide_all(self): # hides all input fields
        self.input_field_name.pack_forget(),
        self.input_field_path.pack_forget(),
        self.input_name_edit.pack_forget(),
        self.input_path_edit.pack_forget()
        self.focus() # take focus of input fields


    def __call__(self) -> None:
        self.mainloop()


app = App("Launcher", "./icon.ico")
app() # run
