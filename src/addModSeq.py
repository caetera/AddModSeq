# -*- coding: utf-8 -*-
"""
Created on Sat Sep 13 13:06:18 2014

Modified sequence 

@author: vgor
"""
import sys
import re
from openpyxl import load_workbook
from openpyxl.cell import get_column_letter
from os import path
from ttk import Frame, Label, Entry, Button 
from Tkinter import *
import tkFileDialog
import tkMessageBox


#constants
moddict = {}
modifications = {}
prsProb = 0.0

#regexes
daExpr = re.compile('N[^P][STC]')
flankExpr = re.compile(r"(\[.+\]\.)(\w+)(\.\[.+\])")
ptmRSExpr = re.compile(r"(\w+)\((\w+)\):(.+)")
phRSExpr = re.compile(r"(\w+)\((\d+)\)(?:x\d+)?:(.+)")

class ListBoxChoice(object):
    def __init__(self, master=None, title=None, message=None, data = []):
        self.master = master
        self.value = None
        self.data = data
        
        self.modalPane = Toplevel(self.master)

        self.modalPane.transient(self.master)
        self.modalPane.grab_set()

        self.modalPane.bind("<Return>", self._choose)
        self.modalPane.bind("<Escape>", self._cancel)
        
        self.modalPane.columnconfigure(0, pad = 5, weight = 1)
        
        self.modalPane.rowconfigure(0, pad = 5)
        self.modalPane.rowconfigure(1, pad = 5, weight = 1)
        self.modalPane.rowconfigure(2, pad = 5)

        if title:
            self.modalPane.title(title)

        if message:
            Label(self.modalPane, text=message).grid(row = 0, column = 0, padx = 10, sticky = W+E)

        listFrame = Frame(self.modalPane)
        listFrame.grid(row = 1, column = 0, sticky = W+E)
        
        scrollBar = Scrollbar(listFrame)
        scrollBar.pack(side=RIGHT, fill=Y)
        self.listBox = Listbox(listFrame, selectmode = SINGLE)
        self.listBox.pack(side = LEFT, fill = BOTH, expand = True)
        scrollBar.config(command = self.listBox.yview)
        self.listBox.config(yscrollcommand=scrollBar.set)
        for item in self.data:
            self.listBox.insert(END, item)

        buttonFrame = Frame(self.modalPane)
        buttonFrame.grid(row = 2, column = 0, sticky = W+E)

        chooseButton = Button(buttonFrame, text="Choose", command=self._choose)
        chooseButton.pack(padx=5, pady=5, side = LEFT)

        cancelButton = Button(buttonFrame, text="Cancel", command=self._cancel)
        cancelButton.pack(padx=5, pady=5, side=RIGHT)

    def _choose(self, event=None):
        try:
            firstIndex = self.listBox.curselection()[0]
            self.value = self.data[int(firstIndex)]
        except IndexError:
            self.value = None
        self.modalPane.destroy()

    def _cancel(self, event=None):
        self.modalPane.destroy()
        
    def returnValue(self):
        self.master.wait_window(self.modalPane)
        return self.value

class toolUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()        
        
    def initUI(self):
      
        self.parent.title("Sequence modification parser")          
        
        self.columnconfigure(0, pad=5)
        self.columnconfigure(1, pad=5, weight = 1)
        self.columnconfigure(2, pad=5)
        
        self.rowconfigure(0, pad=5, weight = 1)
        self.rowconfigure(1, pad=5, weight = 1)
        self.rowconfigure(2, pad=5, weight = 1)
        self.rowconfigure(3, pad=5, weight = 1)
        self.rowconfigure(4, pad=5, weight = 1)
        self.rowconfigure(5, pad=5, weight = 1)
        
        self.lInput = Label(self, text = "Input file")
        self.lInput.grid(row = 0, column = 0, sticky = W)
        self.lPRS = Label(self, text = "phospoRS Column Name")
        self.lPRS.grid(row = 1, column = 0, sticky = W)
        self.lScore = Label(self, text = "Min phosphoRS Score")
        self.lScore.grid(row = 2, column = 0, sticky = W)
        self.lDA = Label(self, text = "Check deamidation sites")
        self.lDA.grid(row = 3, column = 0, sticky = W)
        self.lLabFile = Label(self, text = "Label description file")
        self.lLabFile.grid(row = 4, column = 0, sticky = W)
        
        self.ifPathText = StringVar()
        self.prsScoreText = StringVar(value = '0')
        self.prsNameText = StringVar()
        self.doDAVar = IntVar()
        self.labFileText = StringVar(value = path.abspath('moddict.txt'))
        
        self.ifPath = Entry(self, textvariable = self.ifPathText)
        self.ifPath.grid(row = 0, column = 1, sticky = W+E)
        self.prsName = Entry(self, textvariable = self.prsNameText)
        self.prsName.grid(row = 1, column = 1, sticky = W+E)        
        self.prsScore = Entry(self, textvariable = self.prsScoreText, state = DISABLED)
        self.prsScore.grid(row = 2, column = 1, sticky = W+E)
        self.doDABox = Checkbutton(self, variable = self.doDAVar)
        self.doDABox.grid(row = 3, column = 1, sticky = W)
        self.labFile = Entry(self, textvariable = self.labFileText)
        self.labFile.grid(row = 4, column = 1, sticky = W+E)
        
        
        self.foButton = Button(self, text = "Select file", command = self.selectFileOpen)
        self.foButton.grid(row = 0, column = 2, sticky = E+W, padx = 3)
        self.prsButton = Button(self, text = "Select column", state = DISABLED, command = self.selectColumn)
        self.prsButton.grid(row = 1, column = 2, sticky = E+W, padx = 3)
        self.labFileButton = Button(self, text = "Select file", command = self.selectLabFileOpen)
        self.labFileButton.grid(row = 4, column = 2, sticky = E+W, padx = 3)
        self.startButton = Button(self, text = "Start", command = self.start, padx = 3, pady = 3)
        self.startButton.grid(row = 5, column = 1, sticky = E+W)
        
    
        self.pack(fill = BOTH, expand = True, padx = 5, pady = 5)
        
    def selectFileOpen(self):
        #Open file dialog
        dlg = tkFileDialog.Open(self, filetypes = [('Excel spreadsheet', '*.xlsx')])
        openName = dlg.show()
        if openName != "":
            self.ifPathText.set(openName)
            self.findPRS(openName)#find phosphRS column
    
    def selectLabFileOpen(self):
        #Open labels file dialog
        dlg = tkFileDialog.Open(self, filetypes = [('All files', '*.*')])
        openName = dlg.show()
        if openName != "":
            self.labFileText.set(openName)
    
    def findPRS(self, openName):
        #find phosphoRS column
        worksheet = load_workbook(openName).get_active_sheet() #open excel sheet
        
        self.headers = [unicode(worksheet.cell(get_column_letter(columnNr) + '1').value).lower()
            for columnNr in range(1, worksheet.get_highest_column() + 1)]
        
        self.prsButton.config(state = "normal")
        
        if 'phosphors site probabilities' in self.headers:
            self.prsNameText.set('phosphoRS Site Probabilities')
        elif 'phosphors: phospho_sty site probabilities' in self.headers:
            self.prsNameText.set('PhosphoRS: Phospho_STY Site Probabilities')
        elif 'phosphors: phospho site probabilities' in self.headers:
            self.prsNameText.set('PhosphoRS: Phospho Site Probabilities')
        else:
            self.prsNameText.set('PhosphoRS column not found')
            return
            
        self.prsScore.config(state = 'normal')
        if self.prsScoreText.get() == '0':
            self.prsScoreText.set('95')
    
    def selectColumn(self):
        column = ListBoxChoice(self.parent, "Select column",
                                    "Select the column that has phosphoRS data", self.headers).returnValue()
        
        if not column is None:
            self.prsNameText.set(column)
            self.prsScore.config(state = 'normal')
            if self.prsScoreText.get() == '0':
                self.prsScoreText.set('95')
    
    def start(self):
        if self.prsScoreText.get() == '':
            self.prsScoreText.set("0")
            
        process(self.ifPathText.get(), float(self.prsScoreText.get()), bool(self.doDAVar.get()),
                'PD', self.labFileText.get(), self.prsNameText.get())

#functions
def parseCLInput(arguments):
    """
    Parse input from command line
    """
    if not path.isfile(arguments[1]):
            print "Can't find filename: {}".format(arguments[1])
            return False
            
    if len(arguments) == 2:
        print "Using default minimal phosphoRS site probability (95)\nUsing usual deamidation treatment\nUsing default inputMode (PD)\nUsing default labels (moddict.txt)"
        arguments = arguments[1:2] + ['95.0', 'N', 'PD', 'moddict.txt']
    elif len(arguments) == 3:
        print "Using usual deamidation treatment\nUsing default inputMode (PD)\nUsing default labels (moddict.txt)"
        arguments = arguments[1:3] + ['N', 'PD', 'moddict.txt']
    elif len(arguments) == 4:
        print "Using default inputMode (PD)\nUsing default labels (moddict.txt)"
        arguments = arguments[1:4] + ['PD', 'moddict.txt']
    elif len(arguments) == 5:
        print "Using default labels (moddict.txt)"
        arguments = arguments[1:5] + ['moddict.txt']
    elif len(arguments) >= 6:
        if not path.isfile(arguments[5]):
                print "Can't find filename: {}".format(arguments[5])
                return False
        arguments = arguments[1:6]
    
    arguments[1] = float(arguments[1])
    if arguments[2].upper() == 'Y':
        arguments[2] = True
    elif arguments[2].upper() == 'N':
        arguments[2] = False
    else:
        print "Can't parse deamidation treatment: {}".format(arguments[2])
        return False
    
    return arguments

def printUsage():
    """
    Print usage info
    """
    print 'Usage: {} excelInputFile [minPhosphoRS] [doDeamidation] [inputMode] [labels]\n\
    \tminPhosphoRS (optional) minimal phospoRS site probability to consider valid phospo site\n\
    \tdoDeamidation (optional) perform check for deamidation sites, can be Y(es) or N(o)\n\
    \tinputMode (optional) can be PD (Proteome Discoverer) or MQ (MaxQuant)\n\
    \tlabels (optional) should be path to file with label descriptions'.format(sys.argv[0])

def hitEnter():
    """
    Promt to hit enter
    """
    raw_input('\nHit ENTER to continue')

def runInteractive():
    """
    Interactive mode
    """
    print "Hi, I'm here to help you with modifications.\nUsually I'm happy to run with some command line arguments, here is the small summary"
    printUsage()
    print "Unfortunately you have not provided any arguments. Don't worry, I'll guide you through"
    
    inputFile = raw_input('Please, type the path of the excel file you want to process, ex. somefile.xlsx\nThis is the only manadatory parameter\n')
    while not path.isfile(inputFile):
        inputFile = raw_input('Sorry, I can not find this file. Please, try again\n')
    
    minPRS = raw_input('Please, type the minimal phosphoRS site probability to consider valid phospho site(0 - 100)\n\
    If the input file does not contain phospoRS information the value will be ignored\nThe default settings is 95, you happy with it just hit ENTER\n')
    if minPRS == '':
        minPRS = 95.0
    else:
        minPRS = float(minPRS)
        if minPRS < 0 or minPRS > 100:
            print 'WARNING! Minimal phospoRS site probability is expected to be from 0 to 100'
    
    doDA = raw_input('Please, select if you require validation of deamidation sites\n\tY for Yes and N for No\nThe dafault is No, if you happy with it just hit ENTER\n')
    while not doDA.upper() in ['Y', 'N', '']:
        doDA = raw_input('Sorry, I can not understand. Please, try again\n')
    if doDA == '':
        doDA = 'N'
    
    inputMode = raw_input('Please, type the file type\n\tPD for Proteome Discoverer and MQ for MaxQuant\nThe dafault is PD, if you happy with it just hit ENTER\n')
    while not inputMode.upper() in ['MQ', 'PD', '']:
        inputMode = raw_input('Sorry, I can not understand. Please, try again\n')
    if inputMode == '':
        inputMode = 'PD'
            
    modFile = raw_input('Please, type the path of the modifications file\nThe default is moddict.txt if you happy with this just hit ENTER\n')
    while not (path.isfile(modFile) or modFile == ''):
        modFile = raw_input('Sorry, I can not find this file. Please, try again\n')
    if modFile == '':
        if not path.isfile('moddict.txt'):
            raise Exception('Default file does not exist')
        modFile = 'moddict.txt'
    
    
    print 'Nice. Thank you.\nIf you want to run the same analysis in future you can use the following command in console:\n'
    print '{} {} {} {} {} {}'.format(sys.argv[0], inputFile, minPRS, doDA, inputMode, modFile)
    hitEnter()
    
    if doDA.upper() == 'Y':
        doDA = True
    else:
        doDA = False
    
    process(inputFile, minPRS, doDA, inputMode, modFile)

def runGUI():
    """
    Run with GUI
    """
    try:
        root = Tk()
        ex = toolUI(root)
        root.geometry("500x250+200+200")
        root.mainloop()
    
    except Exception as ex:
        tkMessageBox.showerror('Error', ex.message)
        
def writeRow(worksheet, ColNr, rowNr, iterable):
    """
    Write row of values to the worksheet
    Parameters
    worksheet - openpyxl worksheet
    Colnr - starting column to write into
    rowNr - the number of row to write into
    iterable - any iterable of values
    Return
    None
    """
    for index in range(len(iterable)):
        worksheet.cell(get_column_letter(ColNr + index) + str(rowNr)).value = iterable[index]
        
def parseModDict(moddictInput):
    """
    Reads text file and updates dictionary of modifications
    Parameters
    moddictInput - path or filelike object to read dictionary from
    Return
    None
    """
    with open(moddictInput) as fin:
        for line in fin:
            if line.startswith('#') or line.strip() == '': #comments
                continue
            else: 
                parts = line.strip().split('\t')
                try:
                    if parts[1] == 'NONE':
                        parts[1] = ''
                    modifications[parts[0]] = map(lambda s: s.strip(), parts[2].split(','))#all possible representaton of a modification
                    for r in modifications[parts[0]]:
                        moddict[r] = parts[1]
                except:
                    raise Exception('Error parsing modifications on the following line:\n{}'.format(line))

def parsePTMRS(modstring, minProb):
    """
    Parse ptmRS site probabilities, retaining only positions with probability higher, than *minProb*
    Return the positions and types
    """
    raise Exception("UnderConstruction!")
    result = []
    sumProb = 0#total probability ~ number of phospho sites
    for chunk in modstring.split(';'):#split possible positions
        aaPos, prob = chunk.strip().split(':')#split probability
        prob = float(prob)
        sumProb += prob
        if prob > minProb:#add valid positions
            result.append((aaPos[0], int(aaPos[2:-1])))
    
    return result, int(round(sumProb/100, 0))

def parsePRS(modstring, minProb):
    """
    Parse phospoRS site probabilities, retaining only positions with probability higher, than *minProb*
    Return the positions
    """
    result = []
    sumProb = 0#total probability ~ number of phospho sites
    for chunk in modstring.strip().split(';'):#split possible positions
        try: #trying to deduce format
            aa, pos, prob = phRSExpr.match(chunk.strip()).groups()
            pos = int(pos)
        
        except AttributeError: #wrong format should result in Attribute error, since matchObject is None
            try:
                aaPos, mod, prob = ptmRSExpr.match(chunk.strip()).groups()
                if mod in modifications['Phosphorylation']:
                    aa = aaPos[0]
                    pos = int(aaPos[1:])
                else:
                    continue
            except AttributeError:
                if chunk.strip() == "":
                    raise ValueError("Empty site probabilities string")
                else:
                    raise Exception("Can't deduce site probabilities format from '{}'".format(chunk.strip()))
        
        try: #parsing probability
            prob = float(prob)
        except ValueError:
            try:
                prob = float(prob.replace(",", "."))
            except ValueError:
                raise Exception("Can't parse site probability: {}".format(prob))
        
        sumProb += prob#collecting total site probability
        
        if prob > minProb:#add valid positions
            result.append((aa, pos))
    
    return result, int(round(sumProb/100, 0))

def findDAsites(sequence):
    """
    Find conservative deamidation sites: N[X!=P][STC]
    """
    result = []
    for x in daExpr.finditer(sequence):
        result.append(x.start() + 1)
    
    return result

def hasFlankingResidues(sequence):
    """
    Check if the sequence has flanking residues and strip them out
    Return  False if no flanking residues
            and tuple (flankingUp, sequence, flankingDown) otherwise
    """
    
    m = flankExpr.match(sequence)
    
    if not m is None:
        return m.groups()
    else:
        return False

def applyModsPD(sequence, modline, PRSstring = None, prsProb = 95.0, parseDeamidation = False):
    """
    Provided unmodified sequence and modification string in format of PD
    Return: sequence with modifications in modX format
    Global dictionary moddict contains conversion rules
    """
    if modline == None or modline.strip() == "":
        return sequence
        
    letters = [c for c in sequence] # translate string to char array
    nterm = ""
    cterm = ""
    mods = modline.split(";")
    
    nDeamidation = 0 #number of invalid deamidated positions
    dSites = None #valid deamidation positions
    
    for m in mods:
        openbrace = m.find("(")
        closebrace = m.rfind(")")
        position = m[:openbrace].strip()
        modtype = m[openbrace+1:closebrace]
        
        if not moddict.has_key(modtype) and position[0] != "X": #check the modification is known
            raise Exception("Unknown modification: {}".format(modtype))
        
        if position.lower() == "c-term":
            letters[-1] = moddict[modtype] #change last AA
        elif position.lower() == "n-term":
            #letters[0] = moddict[modtype] #change first AA
            nterm += moddict[modtype]
        elif position[0] == "X" and len(modtype) == 1: #joker AA
            letters[int(position[1:])-1] = letters[int(position[1:])-1][:-1] + modtype #update last position (X in modX)
        elif position[0] == "B" and len(modtype) == 1: #Asp vs Asn
            assert modtype in ["D", "N"]
            letters[int(position[1:])-1] = letters[int(position[1:])-1][:-1] + modtype #update last position
        elif position[0] == "Z" and len(modtype) == 1: #Glu vs Gln
            assert modtype in ["Q", "E"]
            letters[int(position[1:])-1] = letters[int(position[1:])-1][:-1] + modtype #update last position
        elif position[0] == "J" and len(modtype) == 1: #Leu vs Ile
            assert modtype in ["I", "L"]
            letters[int(position[1:])-1] = letters[int(position[1:])-1][:-1] + modtype #update last position
        else:
            assert position[0] == letters[int(position[1:])-1][-1] or position[0] in ["X", "B", "Z", "J"]
            
            if not PRSstring is None and modtype in modifications['Phosphorylation']:
                pass#don't parse phosphorylations if phospoRS mode is on
            elif parseDeamidation and modtype in modifications['Deamidation']: #special deamidation mode is on
                if dSites is None: #find valid positions if necessary
                    dSites = findDAsites(sequence)
                
                if int(position[1:]) in dSites: #site is valid
                    letters[int(position[1:])-1] = moddict[modtype] + letters[int(position[1:])-1] #add modification
                else:
                    nDeamidation += 1
            else:
                letters[int(position[1:])-1] = moddict[modtype] + letters[int(position[1:])-1] #add modification
            
    
    if not PRSstring is None:#add phosphorylations from phosphoRS
        try:
            prsSites, numPhos = parsePRS(PRSstring, prsProb)
            for aa, position in prsSites:
                assert aa == letters[position-1][-1] or aa in ["X", "B", "Z", "J"]
                letters[position-1] = moddict[modifications['Phosphorylation'][0]] + letters[position-1] #add modification
        
            nterm += '({})'.format(moddict[modifications['Phosphorylation'][0]]) * (numPhos - len(prsSites))#unassigned phospo sites
            
        except ValueError:
            nterm += '[cannotassignP]'
        
    if parseDeamidation and nDeamidation > 0:#special parse of deamidation
        nterm += '({})'.format(moddict[modifications['Deamidation'][0]]) * (nDeamidation)#deamidation without valid site
        
    return nterm + "".join(letters) + cterm
    
def applyModsMQ(sequence):
    """
    Parse modified sequence in MaxQuant format to modX format
    Global dictionary moddict contains conversion rules
    """
    openbrace = sequence.find('(')
    closebrace = sequence.find(')')
    
    if openbrace == -1 and closebrace == -1:#no more mods
        return sequence[1:-1]#remove first and last underscores on return
        
    elif openbrace != -1 and closebrace != -1:#complete mod
        mod = sequence[openbrace + 1 : closebrace]
        res = sequence[:openbrace -1] + moddict[mod] + sequence[openbrace - 1] + sequence[closebrace + 1:]
        return applyModsMQ(res)
    
    else: #incomplete mod
        raise Exception('Invalid input sequence: {}'.format(sequence))

def process(excelInput, minPRS, doDA, inputMode, moddictInput, prsColumnName = None):
    """
    Reads Excel sheet and add modifiedSequence column in the end
    Parameters:
    excelInput - search results exported to Excel file, as provided by PD or MQ
        string with path or file-like object
    minPRS - minimal phospoRS site probability
        float
    inputMode - input format of excel file PD for Proteome Discoverer or MQ for MaxQuant
        string
    moddictInput - path to the textfile with modification labels
        string
    doDA - special deamidation treatment switch
        bool
    Return:
    None
    """
    doPRS = False
    selectedColumns = {}
    
    parseModDict(moddictInput)
    
    print 'Opening excel file...'
        
    workbook = load_workbook(excelInput)#open worksheet to save result
    worksheet = workbook.get_active_sheet()
    lastColNr = worksheet.get_highest_column() + 1 #number of the first free column in the worksheet
    lastRowNr = worksheet.get_highest_row()
    
    for columnNr in range(1, worksheet.get_highest_column() + 1): #read column headers
        selectedColumns[unicode(worksheet.cell(get_column_letter(columnNr) + '1').value).lower()] = columnNr
    
    headers = ['Modified Sequence']
    
    if prsColumnName is None:
        prsColumnName = u'phosphors site probabilities'
    else:
        prsColumnName = prsColumnName.lower()
    
    if selectedColumns.has_key(prsColumnName): #check for phospoRS input
        print '\tphospoRS results was found\n\tphosopho sites will be assigned correspondingly'
        doPRS = True
        headers[0] += ' (PRS)'
    else:
        print '\tphospoRS results was NOT found\n\tphosopho sites will be assigned by modification column'
        
    if doDA:
        print '\tdeamidation sites will be checked'
        headers[0] += ' (DA)'
        
        
    writeRow(worksheet, lastColNr, 1, headers) #write headers
        
    writeCount = 0 #count number of lines written
    
    print 'Start processing excel file...'
    
    for rowNr in range(2, lastRowNr + 1):#read all except headers
        try:
            if inputMode.upper() == 'PD':
                #parse PD style
                if doPRS:#PRS present
                    PRSstring = worksheet.cell(get_column_letter(selectedColumns[prsColumnName]) + str(rowNr)).value
                    if PRSstring is None:#empty cells
                        PRSstring = ''
                else:
                    PRSstring = None
                    
                if worksheet.cell(get_column_letter(selectedColumns[u'sequence']) + str(rowNr)).value != None:
                    rawSequence = worksheet.cell(get_column_letter(selectedColumns[u'sequence']) + str(rowNr)).value
                    flanking = hasFlankingResidues(rawSequence) #check for flanking residues
                    if not flanking:
                        sequence = applyModsPD(rawSequence.upper(),\
                            worksheet.cell(get_column_letter(selectedColumns[u'modifications']) + str(rowNr)).value, PRSstring, minPRS, doDA)
                    else:
                        sequence = applyModsPD(flanking[1].upper(),\
                            worksheet.cell(get_column_letter(selectedColumns[u'modifications']) + str(rowNr)).value, PRSstring, minPRS, doDA)
                        
                        sequence = flanking[0] + sequence + flanking[2]
                        
                else:
                    sequence = None
                
            elif inputMode.upper() == 'MQ':
                #parse MQ style
                sequence = applyModsMQ(worksheet.cell(get_column_letter(selectedColumns[u'modified sequence']) + str(rowNr)).value)
                
            else:
                #wrong input
                raise ValueError('Unknown input mode: {}\nUse PD for Proteome Discoverer, or MQ for MaxQuant'.format(inputMode)) 
            
        except KeyError as ex:
            raise Exception("Missing column in the input file: {}".format(ex.message))
        
        writeRow(worksheet, lastColNr, rowNr, [sequence])
        writeCount += 1
        
        if writeCount % 1000 == 0:
            print '\r{} of {} lines ready.'.format(writeCount, lastRowNr - 1),
        
    print '\r\n{} of {} lines ready.\nSaving excel file...'.format(writeCount, lastRowNr - 1) 
        
    workbook.save(excelInput)
    
    print 'Done. It was pleasure to work for you.'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print 'Sequence modification parser'
        parameters = parseCLInput(sys.argv)
        if parameters:
            process(*parameters)
        else:
            printUsage()
            hitEnter()

    else:
        runGUI()
        #runInteractive()
