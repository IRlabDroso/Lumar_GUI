from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from tkcalendar import *
from ttkwidgets.autocomplete import *
import re
import csv


class App(Tk):

    def __init__(self, master):
        self.master = master
        print("hello")

        ### Variables for controlled parameters ###
        self.userDict = {"Nicolas": 1, "Yann": 2,
                         "Ilham": 3, "Ivan": 4, "Dan": 5}
        self.Driver = ["OR42b", "OR47b", "OR59b", "OR22ab", "ORCO"]
        self.OR = ["DmOR%d" % id for id in range(1, 30)]
        self.reporter = ["GCaMP7f"]
        self.T2A = ["F", "TB", "TA"]
        self.sex = ["M", "F"]
        self.Age = list(range(1, 10))
        self.odorList = ["odor1", "odor2", "odor3"]

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

        combo = AutocompleteCombobox(self.ScrollFrame, width=20, completevalues=[
                                     "Water", "none", "test1", "test2"])
        combo.grid(column=4, row=5)

        ##### Create CSV button #####
        self.CreateButton = Button(
            self.ScrollFrame, text="Create CSV", command=self.create_CSV)
        self.CreateButton.grid(column=8, row=100)

        # for widget in self.ScrollFrame.winfo_children():
        #     if isinstance(widget, Label):
        #         widget['font'] = ("Arial", 10)

    def create_CSV(self):
        # function to create the header and the data of EXP_info.csv file

        if(int(self.OdorantNum.get()) == 0 | int(self.CondNum.get()) == 0):
            messagebox.showerror(
                "showerror", "Select at least one condition and one odorant !")
            return

        ### Create the header ###
        self.header = ["Exp_id", "Conditions", "Condition 1", "Condition 2",
                       "Condition 3", "Condition4", "Antennas", "Odorant Trials"]

        if(self.OdorantIB.get() == "None"):
            for i in range(int(self.OdorantNum.get())+1):
                self.header.append(("Trial "+str((i+1))))
        else:
            for i in range(int(self.OdorantNum.get())*2):
                self.header.append(("Trial "+str((i+1))))

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
                for col in range(2, self.NumColCondFrame, 2):
                    text += globals()[
                        f"{self.widgetsName[(((i-1)*self.NumColCondFrame)+col)]}"].get()
                    if(col != (self.NumColCondFrame-1)):
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
                self.row.append(text)
                vial_number = int(
                    globals()[f"{self.widgetsNameOD[int(((i-1)*self.NumColODFrame)+5)]}"].get())
                list_vials.append(vial_number)
                list_vials.append(1)

        with open("C:/Users/irlab/Desktop/Lumar_GUI/Exp_infos.csv", "w", encoding='UTF8', newline='') as self.f:
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

        # Test if the format correspond
        if bool(re.search("\w\wOR\d", str(self.newOR.get()))) & str(self.newOR.get())[0].isupper() & str(self.newOR.get())[2:3].isupper():
            for i in self.widgetsName:

                if re.search("\d{1,9}_2", i):
                    # take the existing list of OR and add the new one
                    newlist = list(globals()[f"{i}"]["values"])
                    newlist.append(self.newOR.get())
                    globals()[f"{i}"]["values"] = newlist
                    # set the current selection to the new OR created
                    globals()[f"{i}"].current(
                        (len(globals()[f"{i}"]["values"])-1))

            Newmaster.destroy()  # quit the new window
        else:
            messagebox.showerror(
                "showerror", "Enter a correct name that follow the rules !")
            Newmaster.lift()

    def createNewDriver(self, Newmaster):
        # Function that is trigerred when we create a new OR and we add it to the combobox

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
        print(self.FirstOR.get())
        for i in self.widgetsName:
            # search for the first combobox which is the OR and fix it to the FirstOR selected
            if re.search("\d{1,9}_2", i):
                globals()[f"{i}"].set(str(self.FirstOR.get()))
            # search for the second combobox which is the Driver and fix it to the FirstDriver selected
            if re.search("\d{1,9}_4", i):
                globals()[f"{i}"].set(str(self.FirstDriver.get()))

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

        self.NumColCondFrame = 13
        self.FirstOR = StringVar()
        self.FirstDriver = StringVar()
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
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.OR, textvariable=self.FirstOR),
                               Label(self.frames[self.count], text="Driver:"),
                               Combobox(self.frames[self.count], width=12, state="readonly",
                                        values=self.Driver, textvariable=self.FirstDriver),
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
                                   self.frames[self.count], width=12, state="readonly", values=self.Age)
                               ]
            else:
                widgetsList = [Label(self.frames[self.count], text=str("Condition " + str(i+1) + ":")),
                               Label(self.frames[self.count], text="OR:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.OR),
                               Label(self.frames[self.count], text="Driver:"),
                               Combobox(
                                   self.frames[self.count], width=12, state="readonly", values=self.Driver),
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
                                   self.frames[self.count], width=12, state="readonly", values=self.Age)
                               ]

            id_widgets = 0
            listtoappend = []
            for x in self.widgetsName[(i*self.NumColCondFrame):((i+1)*self.NumColCondFrame)]:
                globals()[f"{x}"] = widgetsList[id_widgets]

                if re.search("combobox", str(globals()[f"{x}"])):
                    if re.search("combobox6", str(globals()[f"{x}"])):
                        globals()[f"{x}"].current(2)
                    elif (x == self.widgetsName[2]) | (x == self.widgetsName[4]):
                        # If first condition we add this function to autofill
                        globals()[f"{x}"].bind(
                            "<<ComboboxSelected>>", self.callback)
                        globals()[f"{x}"].current(0)
                    else:
                        globals()[f"{x}"].current(0)

                listtoappend.append(globals()[f"{x}"])
                id_widgets += 1

            self.entries.append(listtoappend)
            row_col = 0
            for j in self.entries[self.count]:

                j.grid(row=(4+i), column=(row_col), padx=(0, 20))
                row_col += 1

            self.count += 1

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
                             Combobox(self.framesOD[self.countOD], width=12, state="normal", values=[
                                      "test1", "test2", "test3"]),
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
                    if re.search("combobox2", str(globals()[f"{x}"])):
                        globals()[f"{x}"].current(2)
                    elif re.search("combobox3", str(globals()[f"{x}"])):
                        globals()[f"{x}"].current(id_vials)
                        id_vials += 1
                    else:
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
