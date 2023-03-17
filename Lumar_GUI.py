from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from tkcalendar import *
from ttkwidgets.autocomplete import *
import re
import csv


class AutocompleteCombobox(Combobox):

    def set_completion_list(self, completion_list):
        """Use our completion list as our drop down selection menu, arrows move through menu."""
        self._completion_list = sorted(
            completion_list, key=str.lower)  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):  # Match case insensitively
                _hits.append(element)
        if len(_hits) == 0:
            _hits = [self._completion_list[0]]
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0, END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(INSERT), END)
            self.position = self.index(END)
        if event.keysym == "Left":
            if self.position < self.index(END):  # delete the selection
                self.delete(self.position, END)
            else:
                self.position = self.position-1  # delete one character
                self.delete(self.position, END)
        if event.keysym == "Right":
            self.position = self.index(END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion


class App(Tk):

    def __init__(self, master):
        self.master = master

        ### Variables for controlled parameters ###
        self.userDict = {"Nicolas": 1, "Yann": 2,
                         "Ilham": 3, "Ivan": 4, "Dan": 5}
        self.Driver = ["OR42b", "OR47b", "OR59b", "OR22ab", "ORCO"]
        self.promotor = ["OR42b", "OR47b", "OR59b", "OR22ab", "ORCO"]
        self.replaced = ["Gal4","Boosted Gal4"]
        self.KIKO = ["Knockin", "Transgene", "other"]
        self.OR = ["DmOR%d" % id for id in range(1, 30)]
        self.reporter = ["GCaMP7f"]
        self.T2A = ["F", "TB", "TA"]
        self.sex = ["M", "F"]
        self.Age = list(range(1, 10))
        #self.odorList = ["odor1", "odor2", "odor3"]
        odors = self.load_csv("C:/Users/irlab/gh-repos/Lumar_GUI/Lumar_GUI/Corrected_odors.csv")
        self.odorList = list(odors.values())

        ### params for each conditions create ###
        self.frames = []
        self.entries = []
        self.count = 0

        self.framesOD = []
        self.entriesOD = []
        self.countOD = 0

        ### general parameters ###
        master.title("Test_GUI")
        master.geometry("1500x1000")
        master.resizable(True, True)
        #master.wm_iconbitmap("Fluo_fly.ico")

        ### Frames ###
        # Create the main frame within the canva that got the scrollbars

        self.frame = Frame(master)
        self.frame.pack(fill=BOTH, expand=1)

        self.canvas = Canvas(self.frame, bg="#FFFFFF")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

        self.vbar = Scrollbar(self.frame, orient=VERTICAL,
                              command=self.canvas.yview)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.vbar.set,)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))

        ##### Creating the scrollable frame where to put widgets #####
        self.ScrollFrame = Frame(self.canvas)
        self.canvas.create_window(
            (0, 0), window=self.ScrollFrame, anchor="nw")
        self.ScrollFrame.bind("<Configure>", self.reset_scrollregion)

        ### Widgets ###

        ##### User ID #####
        self.UserLabel = Label(self.ScrollFrame, text="User:").grid(
            column=0, row=1, padx=10, pady=10)

        self.id = StringVar()
        self.UserNumber = Combobox(
            self.ScrollFrame, width=12, textvariable=self.id, state="readonly")
        self.UserNumber['values'] = list(self.userDict.keys())
        self.UserNumber.grid(column=1, row=1)
        self.UserNumber.current(0)

        ##### Date #####
        self.UserLabel = Label(self.ScrollFrame, text="Date:").grid(
            column=0, row=2, padx=10, pady=10)

        self.date = StringVar()
        self.DateEntry = DateEntry(
            self.ScrollFrame, selectmode="day", textvariable=self.date, date_pattern='mm/dd/y')
        self.DateEntry.grid(column=1, row=2, padx=0)

        ##### Condition + validate #####
        self.ConditionLabel = Label(self.ScrollFrame, text="Condition:").grid(
            column=0, row=3, padx=10, pady=10)

        self.CondNum = StringVar()
        self.CondNumEntry = Combobox(
            self.ScrollFrame, width=12, textvariable=self.CondNum, state="readonly")
        self.CondNumEntry['values'] = list(range(0, 31))
        self.CondNumEntry.bind("<<ComboboxSelected>>", self.selected_cond_num)
        self.CondNumEntry.grid(column=1, row=3)
        self.CondNumEntry.current(0)

        ##### Antennas per conditions #####
        self.AntennasLabel = Label(self.ScrollFrame, text="Antennas per cond:")
        self.AntennasLabel.grid(column=0, row=4, padx=10, pady=10)

        self.AnttenasPerC = StringVar()
        self.AnttenasPerCEntry = Combobox(
            self.ScrollFrame, width=12, textvariable=self.AnttenasPerC, state="readonly")
        self.AnttenasPerCEntry["values"] = list(range(0, 31))
        self.AnttenasPerCEntry.grid(column=1, row=4)
        self.AnttenasPerCEntry.current(6)

        ##### Odorant trials Number #####
        self.OdorantsLabel = Label(self.ScrollFrame, text="Odorants:")
        self.OdorantsLabel.grid(column=0, row=5, padx=10, pady=10)

        self.OdorantNum = StringVar()
        self.OdorantEntry = Combobox(
            self.ScrollFrame, width=12, textvariable=self.OdorantNum, state="readonly")
        self.OdorantEntry["values"] = list(range(0, 100))
        self.OdorantEntry.bind("<<ComboboxSelected>>",
                               self.selected_odorant_num)
        self.OdorantEntry.grid(column=1, row=5)
        self.OdorantEntry.current(0)

        ##### odorant in between #####

        self.OdorantsIBLabel = Label(
            self.ScrollFrame, text="In-Between odorant:")
        self.OdorantsIBLabel.grid(column=2, row=5, padx=(120, 0), pady=10)

        self.OdorantIB = StringVar()
        self.OdorantIBEntry = Combobox(
            self.ScrollFrame, width=12, textvariable=self.OdorantIB, state="normal")
        self.OdorantIBEntry["values"] = ["water", "None"]
        self.OdorantIBEntry.grid(column=3, row=5)
        self.OdorantIBEntry.current(0)

        ##### Create CSV button #####
        self.CreateButton = Button(
            self.ScrollFrame, text="Create CSV", command=self.create_CSV)
        self.CreateButton.grid(column=8, row=100)

        # for widget in self.ScrollFrame.winfo_children():
        #     if isinstance(widget, Label):
        #         widget['font'] = ("Arial", 10)

    def create_CSV(self):
        
        # check if all is filled correctly
        if(int(self.OdorantNum.get()) == 0 | int(self.CondNum.get()) == 0):
            messagebox.showerror(
                "showerror", "Select at least one condition and one odorant !")
            return
        

        ##### Creation Conditions_info.csv #####
        ### Create the header ###
        self.header = ["Exp_id", "Condition_id", "OR","promotor","driver","transgene","reporter","T2A","sex", "age","Transgene_name", "remarks"]
        
        ### Create the data ###
        self.rows = []
        ### EXP_id ###
        exp_id = str(self.userDict[self.id.get()]) + "_" + \
            str(self.date.get()).replace("/", "")

        ### EachCond ##
        for i in range(1,(int(self.CondNum.get())+1)):
            self.row = []

            ### Exp_id ###
            self.row.append(exp_id)

            ### Condition_id ###
            cond_id = "cond_"+exp_id+"_"+str(i)
            self.row.append(cond_id)

            ### Transgene information ###
            transgene_name = ""
            for col in range(2, self.NumColCondFrame, 2):
                ### Transgene_name ###

                if col < int(self.NumColCondFrame-2):
                    transgene_name += globals()[
                        f"{self.widgetsName[(((i-1)*self.NumColCondFrame)+col)]}"].get()
                    if(col != (self.NumColCondFrame-3)):
                        transgene_name += "_"
                else:
                    ### special get for textinput ###
                    toappend = globals()[f"{self.widgetsName[(((i-1)*self.NumColCondFrame)+col)]}"].get("1.0", "end-1c")
                    self.row.append(str(toappend))
                    continue
                ### Others ###

                toappend = globals()[f"{self.widgetsName[(((i-1)*self.NumColCondFrame)+col)]}"].get()
                self.row.append(str(toappend))
            self.row.append(str(transgene_name))
            self.rows.append(self.row)

        ### write the Trials_info.csv file ###
        with open("C:/Users/irlab/gh-repos/Lumar_GUI/Lumar_GUI/Conditions_info.csv", "w", encoding='UTF8', newline='') as self.f:
            writer = csv.writer(self.f, dialect='excel', delimiter=',')
            writer.writerow(self.header)
            for i in self.rows:
                writer.writerow(i)

        ##### Creation Trials_info.csv #####
        ### Create the header ###
        self.header = ["Exp_id", "Trial_id", "odor","dilution"]
        
        ### create trials data ###

        ### EachTrial ###
        IBOD_name = ["%s %d" % (self.OdorantIB.get(), id)
                     for id in range(1, (int(self.OdorantNum.get())+1))]
        diff_odors = []
        id_repeat = dict()
        self.rows = []

        ### if no water in between odors ###
        if(self.OdorantIB.get() == "None"):

            for i in range(1,(int(self.OdorantNum.get())+2)):
                self.row = []
                
                ### exp_id ###
                self.row.append(exp_id)

                ### trial_id ###
                trial_id = "Trial_"+ exp_id +"_"+str(i)
                self.row.append(trial_id)
            
                ### Odor + dilution ###
                if(i==1):
                    # if we don't have in between selected we put first odor as water then nothing
                    self.row.append("Water 1")
                    self.row.append(0)
                else:
                    odor = str(globals()[f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+1)]}"].get())
                    dilution = str(globals()[f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+3)]}"].get())
                    if odor in diff_odors:
                        if odor not in id_repeat.keys():
                            id_repeat[odor] = 2
                        else:
                            id_repeat[odor] = id_repeat[odor]+1
                    else:
                        diff_odors.append(odor)
                    
                    odor = odor + "_" + str(id_repeat[odor])
                    
                    self.row.append(odor)
                    self.row.append(dilution)  
                self.rows.append(self.row)

        ### if water in between odors ###
        else:
            # if we do have an ib between odorant just intercal it between testing odors
            for i in range(1, ((int(self.OdorantNum.get())+1)*2)):
                self.row = []
                
                ### exp_id ###
                self.row.append(exp_id)

                ### trial_id ###
                trial_id = "Trial_"+exp_id+"_"+str(i)
                self.row.append(trial_id)
            
                ### Odor + dilution ###
                if i%2 == 0:
                    id = int(i/2)
                    odor = str(globals()[f"{self.widgetsNameOD[int(((id-1)*self.NumColODFrame)+1)]}"].get())
                    dilution = str(globals()[f"{self.widgetsNameOD[int(((id-1)*self.NumColODFrame)+3)]}"].get())
                    if odor in diff_odors:
                        if odor not in id_repeat.keys():
                            id_repeat[odor] = 2
                        else:
                            id_repeat[odor] = id_repeat[odor]+1
                        
                        odor = odor + "_" + str(id_repeat[odor])
                    else:
                        diff_odors.append(odor)
                    
                    self.row.append(odor)
                    self.row.append(dilution)
                else:
                    water_name = "Water "+ str((int(i/2)+1))
                    self.row.append(water_name)
                    self.row.append(0)
                
                self.rows.append(self.row)

        ### write the Trials_info.csv file ###
        with open("C:/Users/irlab/gh-repos/Lumar_GUI/Lumar_GUI/Trials_info.csv", "w", encoding='UTF8', newline='') as self.f:
            writer = csv.writer(self.f, dialect='excel', delimiter=',')
            writer.writerow(self.header)
            for i in self.rows:
                writer.writerow(i)


        ### Create the header ###
        self.header = ["Exp_id", "Conditions", "Condition 1", "Condition 2",
                       "Condition 3", "Condition4", "Antennas", "Odorant Trials"]

        if(self.OdorantIB.get() == "None"):
            for i in range(int(self.OdorantNum.get())+1):
                self.header.append(("Trial "+str((i+1))))
        else:
            for i in range(int(self.OdorantNum.get())*2):
                self.header.append(("Trial "+str((i+1))))

        for i in range(int(self.CondNum.get())):
            self.header.append("Remarks Cond "+str(i+1))

        ### Create the data ###
        self.row = []
        ### EXP_id ###
        exp_id = str(self.userDict[self.id.get()]) + "_" + \
            str(self.date.get()).replace("/", "")

        self.row.append(exp_id)

        ### CondNUM ###
        self.row.append(self.CondNum.get())

        ### EachCond ##
        for i in range(1, 5):
            if(i <= int(self.CondNum.get())):
                text = ""
                for col in range(2, (self.NumColCondFrame-2), 2):
                    text += globals()[
                        f"{self.widgetsName[(((i-1)*self.NumColCondFrame)+col)]}"].get()
                    if(col != (self.NumColCondFrame-3)):
                        text += "_"

                self.row.append(str(text))
            else:
                self.row.append("NA")

        ### Antennas ###
        self.row.append(self.AnttenasPerC.get())

        ### Odorants ###
        self.row.append(self.OdorantNum.get())

        ### EachTrial ###
        IBOD_name = ["%s %d" % (self.OdorantIB.get(), id)
                     for id in range(1, (int(self.OdorantNum.get())+1))]
        list_vials = []
        id_repeat = dict()

        if(self.OdorantIB.get() == "None"):
            # if we don't have in between selected we put first odor as water then nothing
            self.row.append("Water 1")
            for i in range(1, (int(self.OdorantNum.get())+1)):
                text = str(globals()[f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+1)]}"].get()) + "_e" + \
                    str(globals()[
                        f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+3)]}"].get())
                if text in self.row:
                    if text not in id_repeat.keys():
                        id_repeat[text] = 2
                    else:
                        id_repeat[text] = id_repeat[text]+1

                    text = text + "_" + str(id_repeat[text])
                self.row.append(text)
                vial_number = int(
                    globals()[f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+5)]}"].get())
                list_vials.append(vial_number)
        else:
            # if we do have an ib between odorant just intercal it between testing odors
            for i in range(1, (int(self.OdorantNum.get())+1)):
                self.row.append(IBOD_name[(i-1)])
                text = globals()[f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+1)]}"].get() + "_e" + \
                    str(globals()[
                        f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+3)]}"].get())

                if text in self.row:
                    if text not in id_repeat.keys():
                        id_repeat[text] = 2
                    else:
                        id_repeat[text] = id_repeat[text]+1

                    text = text + "_" + str(id_repeat[text])
                self.row.append(textASDAS) 
                vial_number = int(
                    globals()[f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+5)]}"].get())
                list_vials.append(vial_number)
                list_vials.append(1)

        ### Remarks ###
        for i in range(1, (int(self.CondNum.get())+1)):
            remark = globals()[
                f"{self.widgetsName[((i*self.NumColCondFrame)-1)]}"].get("1.0", "end-1c")
            self.row.append(remark)

        with open("C:/Users/irlab/gh-repos/Lumar_GUI/Lumar_GUI/Exp_info.csv", "w", encoding='UTF8', newline='') as self.f:
            writer = csv.writer(self.f, dialect='excel', delimiter=',')
            writer.writerow(self.header)
            writer.writerow(self.row)

        self.createTemplate(list_vials)

        self.close(self.master)

    def createTemplate(self, list_vials):
        # Function to create the template file for the sequencer
        with open("Template_184s.osf", "w") as f:
            f.write("220A Olfactometer Sequence File\n")
            f.write("Vial	Delivery (ms)	Delay (s)\n")
            f.write("1	35	1000\n")
            f.write("1	60	1000\n")
            f.write("1	60	1000\n")
            f.write("No Vial	30	1000\n")
            for vial in list_vials:
                for pulse in range(1, 4):
                    if pulse == 1:
                        f.write("%d	30	1000\n" % vial)
                    else:
                        f.write("%d	60	1000\n" % vial)
                f.write("No Vial	30	1000\n")

    def close(self, Newmaster):
        Newmaster.quit()

    def createNewOr(self, Newmaster):
        # Function that is trigerred when we create a new OR and we add it to the combobox

        # avoid to create a duplicated name
        if self.newOR.get() in list(globals()[f"{self.widgetsName[2]}"]["values"]):
            messagebox.showerror(
                "showerror", "Enter a name that does not already exist!")
            Newmaster.lift()

        # Test if the format correspond
        elif bool(re.search("\w\wOR\d", str(self.newOR.get()))) & str(self.newOR.get())[0].isupper() & str(self.newOR.get())[2:3].isupper():
            for i in self.widgetsName:

                if re.search("\d{1,9}_2", i):
                    # take the existing list of OR and add the new one
                    newlist = list(globals()[f"{i}"]["values"])
                    newlist.append(self.newOR.get())
                    globals()[f"{i}"]["values"] = newlist
                    # set the current selection to the new OR created
                    globals()[f"{i}"].current(
                        (len(globals()[f"{i}"]["values"])-1))
                    globals()[f"{i}"].set_completion_list(newlist)

            Newmaster.destroy()  # quit the new window
        else:
            messagebox.showerror(
                "showerror", "Enter a correct name that follow the rules!")
            Newmaster.lift()

    def createNewDriver(self, Newmaster):
        # Function that is trigerred when we create a new OR and we add it to the combobox

        # avoid to create a duplicated name
        if self.newOR.get() in list(globals()[f"{self.widgetsName[4]}"]["values"]):
            messagebox.showerror(
                "showerror", "Enter a name that does not already exist!")
            Newmaster.lift()
        # Test if the format correspond

        for i in self.widgetsName:
            if re.search("\d{1,9}_4", i):
                # take the existing list of OR and add the new one
                newlist = list(globals()[f"{i}"]["values"])
                newlist.append(self.newDriver.get())
                globals()[f"{i}"]["values"] = newlist
                # set the current selection to the new OR created
                globals()[f"{i}"].current((len(globals()[f"{i}"]["values"])-1))

        Newmaster.destroy()  # quit the new window

    def selected_cond_num(self, event):
        # Function that detects when number of conditions changes and adapt things
        ### hide previous frames ###
        for i in self.frames:
            i.grid_forget()

        ### Add create new variables buttons ###
        self.createNewVar()

        ### Show conditions frames with the functions below ###
        self.drawConditions()
        self.change_position()

    def selected_odorant_num(self, event):
        # Function that detects when number of odors changes and adapt things

        ### hide previous frames ###
        for i in self.framesOD:
            i.grid_forget()

        ### Show odors frames with the functions below ###
        self.drawOdorants()
        self.change_position()

    def createNewVar(self):
        self.newORButton = Button(
            self.ScrollFrame, text="Create a new OR", command=self.addnewVar)
        self.newORButton.grid(column=2, row=3, padx=(112, 30))
        self.newORButton = Button(
            self.ScrollFrame, text="Create a new Driver", command=self.addnewVarDriver)
        self.newORButton.grid(column=3, row=3, padx=0)

    def addnewVar(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.geometry("800x500")
        self.newWindow.title("Create a new OR")
        self.textBoxOr = Text(self.newWindow, height=20,
                              width=70, font=('Arial', 11, 'bold'))
        message = """In order to create a new OR you must use the followings rules:\n\n   - The format of the OR should be the species then OR and finally the number(DmOR12)\n\n   - The species name should be the latin initials corresponding to the Genus (capital letter) and the species => (Dm for drosophila melanogaster)\n\n   - None of special character should be used (- ,_ ,/ ,etc...)
        """
        self.textBoxOr.grid(row=0, column=0, columnspan=3, padx=50, pady=10)
        self.textBoxOr.insert('end', message)
        self.textBoxOr.config(state="disabled")

        Label(self.newWindow, text="Enter the new OR:").grid(row=1, column=0)
        self.newOR = StringVar()
        self.newOREntry = Entry(self.newWindow, textvariable=self.newOR)
        self.newOREntry.grid(row=1, column=1)
        Button(self.newWindow, text="Create new OR", command=lambda: self.createNewOr(
            self.newWindow)).grid(row=2, column=1)

    def addnewVarDriver(self):
        self.newWindowDriver = Toplevel(self.master)
        self.newWindowDriver.geometry("800x500")
        self.newWindowDriver.title("Create a new Driver")

        self.textBoxDriver = Text(
            self.newWindowDriver, height=20, width=70, font=('Arial', 11, 'bold'))
        message = """In order to create a new Driver you must use the followings rules:\n\n ???
        """
        self.textBoxDriver.grid(
            row=0, column=0, columnspan=3, padx=50, pady=10)
        self.textBoxDriver.insert('end', message)
        self.textBoxDriver.config(state="disabled")

        Label(self.newWindowDriver, text="Enter the new Driver:").grid(
            row=1, column=0)
        self.newDriver = StringVar()
        self.newDriverEntry = Entry(
            self.newWindowDriver, textvariable=self.newDriver)
        self.newDriverEntry.grid(row=1, column=1)
        Button(self.newWindowDriver, text="Create new OR", command=lambda: self.createNewDriver(
            self.newWindowDriver)).grid(row=2, column=1)

    def callback(self, event):
        # Function to autoFill the conditions comboboxs
        for i in self.widgetsName:
            # search for the first combobox which is the OR and fix it to the FirstOR selected
            if re.search("\d{1,9}_2", i):
                globals()[f"{i}"].set(str(self.FirstOR.get()))
            # search for the second combobox which is the Driver and fix it to the FirstDriver selected
            elif re.search("\d{1,9}_4", i):
                globals()[f"{i}"].set(str(self.FirstPromotor.get()))
            elif re.search("\d{1,9}_6", i):
                globals()[f"{i}"].set(str(self.FirstReplaced.get()))
            elif re.search("\d{1,9}_8", i):
                globals()[f"{i}"].set(str(self.FirstKIKO.get()))

    def reset_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def change_position(self):
        # Function to adapt the row of widgets depending on numbers of conditions
        self.AntennasLabel.grid(column=0, row=(self.count + 4))
        self.AnttenasPerCEntry.grid(column=1, row=(self.count + 4))

        self.OdorantsLabel.grid(column=0, row=(self.count + 5))
        self.OdorantEntry.grid(column=1, row=(self.count + 5))
        self.OdorantsIBLabel.grid(column=2, row=(self.count + 5))
        self.OdorantIBEntry.grid(column=3, row=(self.count + 5))

    def drawConditions(self):
        # Function to create the conditions frames which all informations for each
        # First condition frame contains callback to autofill others conditions

        self.NumColCondFrame = 19
        self.FirstOR = StringVar()
        self.FirstPromotor = StringVar()
        self.FirstReplaced = StringVar()
        self.FirstKIKO = StringVar()
        self.widgetsName = ["self.widget_%d_%d" % (x, j) for x in range(
            1, (int(self.CondNum.get())+1)) for j in range(self.NumColCondFrame)]

        for i in range(int(self.CondNum.get())):
            self.frames.append(
                Frame(self.ScrollFrame, borderwidth=1, relief="solid", height=300))

            self.frames[self.count].grid(
                row=(4+i), column=2, columnspan=15, pady=10)

            if i == 0:
                # if first conditions add the textvariables to autofill later and bind the function below
                widgetsList = [Label(self.frames[self.count], text=str("Condition " + str(i+1) + ":")),
                               Label(self.frames[self.count], text="OR:"),
                               AutocompleteCombobox(
                                   self.frames[self.count], width=12, values=self.OR, textvariable=self.FirstOR),
                               Label(self.frames[self.count],
                                     text="Promotor:"),
                               AutocompleteCombobox(self.frames[self.count], width=12,
                                                    values=self.promotor, textvariable=self.FirstPromotor),
                               Label(self.frames[self.count],
                                     text="Driver:"),
                               AutocompleteCombobox(self.frames[self.count], width=12,
                                                    values=self.replaced, textvariable=self.FirstReplaced),
                               Label(self.frames[self.count], text="Transgene:"),
                               AutocompleteCombobox(self.frames[self.count], width=12,
                                                    values=self.KIKO, textvariable=self.FirstKIKO),
                               Label(self.frames[self.count],
                                     text="Reporter:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.reporter),
                               Label(self.frames[self.count], text="T2A:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.T2A),
                               Label(self.frames[self.count], text="Sex:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.sex),
                               Label(self.frames[self.count], text="Age:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.Age),
                               Label(self.frames[self.count], text="Remarks:"),
                               Text(self.frames[self.count],
                                    width=12, height=3)
                               ]
            else:
                widgetsList = [Label(self.frames[self.count], text=str("Condition " + str(i+1) + ":")),
                               Label(self.frames[self.count], text="OR:"),
                               AutocompleteCombobox(
                                   self.frames[self.count], width=12, values=self.OR),
                               Label(self.frames[self.count],
                                     text="Promotor:"),
                               AutocompleteCombobox(self.frames[self.count], width=12,
                                                    values=self.promotor),
                               Label(self.frames[self.count],
                                     text="Driver:"),
                               AutocompleteCombobox(self.frames[self.count], width=12, state="readonly",
                                                    values=self.replaced),
                               Label(self.frames[self.count], text="Transgene:"),
                               AutocompleteCombobox(self.frames[self.count], width=12,
                                                    values=self.KIKO),
                               Label(self.frames[self.count],
                                     text="Reporter:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.reporter),
                               Label(self.frames[self.count], text="T2A:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.T2A),
                               Label(self.frames[self.count], text="Sex:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.sex),
                               Label(self.frames[self.count], text="Age:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.Age),
                               Label(self.frames[self.count], text="Remarks:"),
                               Text(self.frames[self.count],
                                    width=12, height=3)
                               ]

            id_widgets = 0
            listtoappend = []
            for x in self.widgetsName[(i*self.NumColCondFrame):((i+1)*self.NumColCondFrame)]:
                globals()[f"{x}"] = widgetsList[id_widgets]

                if re.search("combobox", str(globals()[f"{x}"])):
                    if re.search("!combobox4", str(globals()[f"{x}"])):
                        # select day of emergence as 3
                        globals()[f"{x}"].current(2)
                    elif (x == self.widgetsName[2]) | (x == self.widgetsName[4]) | (x == self.widgetsName[6]) | (x == self.widgetsName[8]):
                        # If first condition we add this function to autofill
                        globals()[f"{x}"].set_completion_list(
                            (globals()[f"{x}"]["values"]))
                        globals()[f"{x}"].focus_set()
                        globals()[f"{x}"].bind(
                            "<<ComboboxSelected>>", self.callback)
                        globals()[f"{x}"].current(0)
                    else:
                        globals()[f"{x}"].current(0)

                listtoappend.append(globals()[f"{x}"])
                id_widgets += 1

            self.entries.append(listtoappend)
            row_col_1 = 0
            row_col_2 = 1
            number = 0
            for j in self.entries[self.count]:
                if number < 9:
                    j.grid(row=(4+(i*2)), column=(row_col_1),
                           padx=(0, 20), pady=(5, 0))
                    row_col_1 += 1
                    number += 1
                elif number == (self.NumColCondFrame-2):
                    j.grid(row=(4+(i*2)), column=(row_col_1),
                           padx=(0, 20), pady=(5, 0))
                    row_col_1 += 1
                    number += 1
                else:
                    j.grid(row=(5+(i*2)), column=(row_col_2),
                           padx=(0, 20), pady=(0, 5))
                    row_col_2 += 1
                    number += 1

            self.count += 1

    # Load the CSV file for the odours
    def load_csv(self,filename):
        odour = dict()
        # Open file in read mode
        file = open(filename,"r")
        # Reading file
        csv_reader = csv.reader(file)
        first_line = True
        for row in csv_reader:
            if first_line:
                first_line=False
                continue
            odour[row[0]] = row[1]
        
        return odour
    
    
    def drawOdorants(self):
        # Function to create the trials frames which all informations for each

        self.NumColODFrame = 6
        id_vials = 1

        self.widgetsNameOD = ["widgetOD_%d_%d" % (x, j) for x in range(
            1, (int(self.OdorantNum.get())+1)) for j in range(self.NumColODFrame)]

        for i in range(int(self.OdorantNum.get())):
            self.framesOD.append(
                Frame(self.ScrollFrame, borderwidth=1, relief="solid", height=300))

            self.framesOD[self.countOD].grid(
                row=(self.count+6+i), column=1, columnspan=3, pady=10)

            widgetsListOD = [Label(self.framesOD[self.countOD], text=str("Trial: " + str(i+1) + ":")),
                             AutocompleteCombobox(self.framesOD[self.countOD], width=30, state="normal", values=self.odorList),
                             Label(self.framesOD[self.countOD], text=str(
                                 "Dilution: " + str(i+1) + ":")),
                             Combobox(self.framesOD[self.countOD], width=12, state="normal", values=list(
                                 range(1, 10))),
                             Label(self.framesOD[self.countOD],
                                   text=str("Vial number: ")),
                             Combobox(self.framesOD[self.countOD], width=12, state="normal", values=list(
                                 range(1, 20)))
                             ]

            id_widgets = 0
            listtoappend = []
            for x in self.widgetsNameOD[(i*self.NumColODFrame):((i+1)*self.NumColODFrame)]:
                globals()[f"{x}"] = widgetsListOD[id_widgets]

                if re.search("combobox", str(globals()[f"{x}"])):
                    if re.search("!combobox$", str(globals()[f"{x}"])):
                        globals()[f"{x}"].current(2)
                    elif re.search("!combobox2", str(globals()[f"{x}"])):
                        globals()[f"{x}"].current(id_vials)
                        id_vials += 1
                    else:
                        globals()[f"{x}"].set_completion_list(
                            (globals()[f"{x}"]["values"]))
                        globals()[f"{x}"].focus_set()
                        globals()[f"{x}"].current(0)

                listtoappend.append(globals()[f"{x}"])
                id_widgets += 1

            self.entriesOD.append(listtoappend)

            row_col = 0
            for j in self.entriesOD[self.countOD]:

                j.grid(row=(self.count+6+i), column=(row_col), padx=(0, 20))
                row_col += 1

            self.countOD += 1


root = Tk()
my_gui = App(root)
root.mainloop()
