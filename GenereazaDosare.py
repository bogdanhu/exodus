from flask import Flask

app = Flask(__name__)

from xml.dom import minidom
import os
import pathlib
from termcolor import colored
from itertools import groupby
import glob
import re

class Part():
    def __init__(self, nume):
        self.Nume = nume
        self.Material = ""
        self.AreGEO = False
        self.CaleGEO = None
        self.NrBuc = 0
        self.Grosime = 0

class Job():
    def __init__(self, nume):
        self.Nume = nume
        self.JobName = ""
        self.Dosar = 0
        self.Cale = ""
        self.LinuxPath = "/mnt/xLucru/" + nume
        self.LinuxOfertaPath = self.LinuxPath + "/OFERTA"
        self.LinuxOfertaPathConvert = pathlib.Path(self.LinuxOfertaPath)
        self.WindowsPath = "X:\\" + nume
        self.WindowsOfertaPath = self.WindowsPath + "\OFERTA"

        self.Tehnologie = ""
        self.Grosime = 0.2
        self.Set = f'{self.setTehnologie}'
        self.WindowsJobPath = f'{self.WindowsOfertaPath}\\{self.Dosar}_{self.Set}'

    def setGrosime(self, grosime):
        self.Grosime = grosime
        self.JobName = f'{self.Dosar}_{self.Tehnologie}'
        self.Set = self.setTehnologie + '_' + self.Grosime
        self.WindowsJobPath = f'{self.WindowsOfertaPath}\\{self.JobName}'

    def setTehnologie(self, teh):
        self.Tehnologie = teh
        self.JobName = f'{self.Dosar}_{self.Tehnologie}'
        self.WindowsJobPath = f'{self.WindowsOfertaPath}\\{self.JobName}'

    def setDosar(self, dosar):
        self.Dosar = dosar
        self.JobName = f'{self.Dosar}_{self.Tehnologie}'
        self.WindowsJobPath = f'{self.WindowsOfertaPath}\\{self.JobName}'

    def updateSet(self):
        self.Set = f'{self.Tehnologie}'

def AdaugaNodNumeValoareTip(nume, valoare, type, referinta, tip):
    temp = root.createElement(tip)
    temp.setAttribute('name', nume)
    temp.setAttribute('type', type)
    temp.setAttribute('value', valoare)
    referinta.appendChild(temp)

def AdaugaNodNumeValoare(nume, valoare, referinta, tip):
    temp = root.createElement(tip)
    temp.setAttribute('name', nume)
    temp.setAttribute('value', valoare)
    referinta.appendChild(temp)

def AdaugaNodNume(nume, referinta, tip):
    temp = root.createElement(tip)
    temp.setAttribute('name', nume)
    referinta.appendChild(temp)
    return temp

def AdaugaReferintaPiesa(numeReper, NestingPart):
    global secventaOiD
    RefPart = root.createElement('ref')
    RefPart.setAttribute('name', 'ComponentPart')
    NestingPart.appendChild(RefPart)
    ComponentPart = root.createElement('class')
    secventaOiD += 1
    ComponentPart.setAttribute('oid', f'{secventaOiD}')
    ComponentPart.setAttribute('type', 'ComponentPart')
    RefPart.appendChild(ComponentPart)
    # todo 2: aici trebuie sa pun tehnologia
    AdaugaNodNumeValoare('FilePath', NewJob.WindowsOfertaPath + '\\' + NewJob.Set, referinta=ComponentPart,
                         tip='UnicodeString')
    AdaugaNodNumeValoare('Name', numeReper, referinta=ComponentPart, tip='UnicodeString')
    AdaugaNodNumeValoare('ID', '0', referinta=ComponentPart, tip='long')
    return secventaOiD

def AdaugaClasa(type):
    global secventaOiD
    NestingPart = root.createElement('class')
    secventaOiD += 1
    NestingPart.setAttribute('oid', f'{secventaOiD}')
    NestingPart.setAttribute('type', type)
    return NestingPart

def AdaugaReper(numeReper, cantitateReper):
    global secventaOiD,RefColNestingPartList
    NestingPart = AdaugaClasa(type="NestingPart")
    RefColNestingPartList.appendChild(NestingPart)
    CANTITATE_MIN_P1 = 15
    MemberOfJob = root.createElement('bool')
    MemberOfJob.setAttribute('name', 'MemberOfJob')
    MemberOfJob.setAttribute('value', 'true')
    NestingPart.appendChild(MemberOfJob)
    AdaugaNodNumeValoare('TotalNumberOfPartsMax', f'{cantitateReper}', referinta=NestingPart, tip='long')
    AdaugaNodNumeValoare('TotalNumberOfPartsMin', f'{cantitateReper}', referinta=NestingPart, tip='long')
    ## ref
    secventaOiD = AdaugaReferintaPiesa(numeReper, NestingPart=NestingPart)
    AdaugaNodNumeValoare('ID', '0', referinta=NestingPart, tip='long')

def XMLSetup():
    global root,secventaOiD
    xml = root.createElement('class')
    xml.setAttribute('oid', f'{secventaOiD}')
    xml.setAttribute('file-format-version', '1')
    xml.setAttribute('type', 'NestingJob')
    root.appendChild(xml)
    return xml

def AdaugaInfoNesting():
    # todo aici trebuie sa mai adaug un id
    global ClassNestingResult
    AdaugaNodNumeValoare('OverallNumberOfSheets', '0', referinta=ClassNestingResult, tip='long')
    AdaugaNodNumeValoare('OverallWaste', '100', referinta=ClassNestingResult, tip='double')
    AdaugaNodNumeValoare('NestingTime', '0', referinta=ClassNestingResult, tip='double')
    AdaugaNodNumeValoare('HasProblems', 'false', referinta=ClassNestingResult, tip='bool')
    AdaugaNodNumeValoareTip('State', type='JobState', valoare='Initial', referinta=ClassNestingResult, tip='enum')

def AdaugaInformatiiGenerale():
    # todo Material nu e cel mai indicat nume
    AdaugaNodNumeValoare('MaterialDesignation', NewJob.Material, referinta=xml, tip='UnicodeString')
    AdaugaNodNumeValoare('SheetPath', NewJob.WindowsOfertaPath+"\\"+NewJob.JobName, referinta=xml, tip='UnicodeString')
    AdaugaNodNumeValoare('BaseSheetName', NewJob.JobName, referinta=xml, tip='UnicodeString')

def AdaugaInformatiiDespreFoi():
    global secventaOiD

    RawSheet = AdaugaClasa('RawSheet')
    RefColRawSheetList.appendChild(RawSheet)
    AdaugaNodNumeValoare('Active', 'true', referinta=RawSheet, tip='bool')

    # TODO - set data pentru X,Y,Z si material !
    print(NewJob.Grosime)
    AdaugaNodNumeValoare('DimensionZ', str(NewJob.Grosime), referinta=RawSheet, tip='double')
    AdaugaNodNumeValoare('DimensionY', '1000', referinta=RawSheet, tip='double')
    AdaugaNodNumeValoare('DimensionX', '2000', referinta=RawSheet, tip='double')
    AdaugaNodNumeValoare('Number', '100', referinta=RawSheet, tip='long')
    AdaugaNodNumeValoare('Material', 'St37-60', referinta=RawSheet, tip='UnicodeString')
    AdaugaNodNumeValoare('ID', '2206297', referinta=RawSheet, tip='long')

def setMaterialTehnology():
    global NewJob
    valoareGrosime = int(NewJob.Grosime * 10)
    if ("OL" in NewJob.Tehnologie.upper() or '1.0038' in NewJob.Tehnologie.upper()):
        NewJob.Material = f'St37-{valoareGrosime}'
        print(colored('OTEL!!', 'magenta'))
    elif ("AL" in NewJob.Tehnologie.upper()):
        NewJob.Material = f'AlMg3-{valoareGrosime}'
        print(colored("ALUMINIU!!", 'blue'))
    elif ("AUS" in NewJob.Tehnologie.upper() or "FER" in NewJob.Tehnologie.upper()):
        NewJob.Material = f'1.4301-{valoareGrosime}'
        print(colored("INOX", 'green'))
    elif ("ZN" in NewJob.Tehnologie.upper()):
        NewJob.Material = f'1.4301-{valoareGrosime}'
        print(colored("ZN", 'magenta'))  # termcolor.COLORS
    else:
        NewJob.Material = f'1.4301-{valoareGrosime}'
        print(colored(f"Warning - no material data identified for {NewJob.Tehnologie}", 'yellow', 'on_red',
                      attrs=["bold", "blink"]))
    print(f'Material tehnologic setat: {NewJob.Material}')

def ScrieFisierulJob():
    global save_path_file
    xml_str = root.toprettyxml(indent="\t")
    print(save_path_file)
    if os.path.exists(f'{NewJob.LinuxOfertaPath}/{NewJob.JobName}'):
        print(f'PATH: {NewJob.LinuxPath}//{NewJob.JobName} OK')
    else:
        os.mkdir(f'{NewJob.LinuxOfertaPath}/{NewJob.JobName}')
        print(f'{NewJob.LinuxOfertaPath}/{NewJob.JobName} -  PATH NOT OK')
    with open(save_path_file, "w") as f:
        try:
            f.write(xml_str)
        except e as Exception:
            print(e)
    print("OK")

def CreazaJobDupaInputDosar(dosar):
    global Folder
    try:
        dosar = int(dosar)
    except:
        exit("Nu am putut identificat corect dosarul / calea")

    if (dosar < 23000):
        exit("Nu am putut identificat corect dosarul / calea")
    ## CAUTA FOLDERUL
    print(f'Caut calea pentru {dosar}')
    listaRezultate = list(pathlib.Path("/mnt/xLucru/").glob(str(dosar) + '*'))
    if len(listaRezultate) == 1:
        print(f"Am gasit pe {listaRezultate[0]}")
        CaleFolder = pathlib.Path(listaRezultate[0])
        if (CaleFolder.is_dir()):
            Folder = CaleFolder.name
            NewJob = Job(nume=Folder)
            print(f'Folder: {Folder}')
            return NewJob
        else:
            print("Calea tot nu e ok. Ies")
            exit(0)

    else:
        print("Nu am gasit calea corecta.Ies")
        exit(0)

def AlocareNrBuc():
    global NewPart,fisierConvert
    if ("Qnt" in fisierConvert.stem):
        indexQnt = fisierConvert.stem.index('Qnt')
        indexNextBatch = fisierConvert.stem.find('-', indexQnt)
        if indexNextBatch < 0:
            indexNextBatch = None
        NewPart.NrBuc = fisierConvert.stem[indexQnt + 3:(indexNextBatch)]
        try:
            NewPart.NrBuc = int(NewPart.NrBuc)
        except:
            NewPart.NrBuc = 1
    if ("buc" in fisierConvert.stem):
        indexBuc = fisierConvert.stem.index('buc')
        indexpreviousBatch = fisierConvert.stem.find('_', 1)
        NewPart.NrBuc = fisierConvert.stem[indexpreviousBatch + 1:indexBuc]
        try:
            NewPart.NrBuc = int(NewPart.NrBuc)
        except:
            NewPart.NrBuc = 1

def AlocareGrosime():
    global NewPart
    if "_" in NewPart.Material:
        indexpreviousBatch = NewPart.Material.find('_', 1)
        NewPart.Grosime = NewPart.Material[indexpreviousBatch + 1:]
        try:
            NewPart.Grosime = float(NewPart.Grosime)
        except:
            NewPart.Grosime = 0
    if "mm" in NewPart.Material:
        indexMM = NewPart.Material.index('mm')
        indexpreviousBatch = NewPart.Material.find('_', 1)
        NewPart.Grosime = NewPart.Material[indexpreviousBatch + 1:indexMM]
        # print(NewPart.Grosime)
        try:
            NewPart.Grosime = float(NewPart.Grosime)
        except:
            NewPart.Grosime = 0

def InchidereJob():
    global secventaOiD,ClassNestingResult,RefColRawSheetList,xml
    NestingVariantList = AdaugaNodNume('NestingVariantList', xml, tip='refcol')
    NestingVariant = AdaugaClasa('NestingVariant')
    NestingVariantList.appendChild(NestingVariant)
    RefNestingResult = AdaugaNodNume('NestingResult', NestingVariant, 'ref')
    ClassNestingResult = AdaugaClasa('NestingResult')
    NestingResult = root.createElement('class')
    secventaOiD += 1
    NestingResult.setAttribute('oid', f'{secventaOiD}')
    ClassNestingResult.appendChild(NestingResult)
    # aici alta clasa
    RefNestingResult.appendChild(ClassNestingResult)
    AdaugaInfoNesting()
    RefColRawSheetList = AdaugaNodNume('RawSheetList', NestingVariant, tip='refcol')
    AdaugaInformatiiDespreFoi()
    AdaugaInformatiiGenerale()
    if (not NewJob.LinuxOfertaPathConvert.exists()):
        print(f'creez folderul {NewJob.LinuxOfertaPathConvert}')
        os.mkdir(NewJob.LinuxOfertaPathConvert)
    if (not NewJob.LinuxOfertaPathConvert.exists()):
        exit("Eroare la crearea folderului. Nu exista folderul?")
    ScrieFisierulJob()

@app.route('/dosar/<int:dosarID>')
def runMe(dosarID):
    global NewPart,fisierConvert,NewJob,root,secventaOiD,RefColNestingPartList,xml,save_path_file
    dosar = dosarID
    NewJob = CreazaJobDupaInputDosar(dosar)
    listaRezultate2 = glob.iglob(NewJob.LinuxOfertaPath + '/*[!old]/*.geo', recursive=True)
    listaPart = []
    for fisier in listaRezultate2:
        fisierConvert = pathlib.Path(fisier)
        print(f'Fisier: {fisierConvert.name}')
        NewPart = Part(fisierConvert.name)
        NewPart.Material = fisierConvert.parent.name
        AlocareGrosime()
        AlocareNrBuc()

        if "geo" in fisierConvert.suffix.lower():
            NewPart.AreGEO = True
            NewPart.CaleGEO = fisierConvert
        # print(f'Fisier: {fisierConvert.stem} cu Material: {NewPart.Material}')
        listaPart.append(NewPart)
    listaPart.sort(key=lambda x: x.Material, reverse=False)
    lastMaterial = ""
    listaJob = []
    for Reper in listaPart:
        if Reper.Material != lastMaterial:
            if lastMaterial != "":
                InchidereJob()
            print("CREEZ NOU JOB")
            lastMaterial = Reper.Material
            print(f'Material Reper {lastMaterial}')

            NewJob = Job(nume=Folder)
            NewJob.setTehnologie(Reper.Material)
            NewJob.Grosime = Reper.Grosime
            NewJob.setDosar(dosar)
            NewJob.updateSet()  # teoretic asta il iau la parsare
            setMaterialTehnology()
            print(f'folder Retea Windows:{NewJob.WindowsJobPath}')
            save_path_file = f'{NewJob.LinuxOfertaPath}/{NewJob.JobName}/{NewJob.JobName}.job'
            root = minidom.Document()
            secventaOiD = 10000

            ### GOGOGO
            xml = XMLSetup()
            AdaugaNodNumeValoare('OriginalFileName', NewJob.WindowsJobPath + "\\" + NewJob.JobName + ".job", xml,
                                 'UnicodeString')
            RefColNestingPartList = AdaugaNodNume('NestingPartList', xml, 'refcol')
            AdaugaReper(numeReper=Reper.Nume, cantitateReper=Reper.NrBuc)

        else:
            AdaugaReper(numeReper=Reper.Nume, cantitateReper=Reper.NrBuc)
            print("ADAUG LA JOBUL VECHI")
    if lastMaterial != "":
        InchidereJob()
    return f'Success!<br/>GO to <a href="file://{NewJob.WindowsOfertaPath}">{NewJob.WindowsOfertaPath}</a>'


if __name__ == "__main__":
    app.debug = True
    app.run (threaded=True,host='0.0.0.0',port=5050)

