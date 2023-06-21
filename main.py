# coding: utf-8

from Classes.hyperplanning import HyperPlanningClient, Etudiant
from Classes.Reader import Reader
from Classes.Screen import Screen
from datetime import date, datetime
import time
import threading

def inactivityProcess():
    lcd.clear()
    lcd.disableScreen()
    print('Inactivité détectée')

timerActivity = threading.Timer(60, inactivityProcess)

hp = HyperPlanningClient()
nfc = Reader()
lcd = Screen()
id = None

print('Connecté à ' + hp.getVersion())

lcd.write("1. Faire l'appel", 0)
lcd.write("2. Nouveau badge", 1)
choice = input("1. Faire l'appel :\n2. Enregistrer un nouveau badge\n\nChoix : ")
while choice != '1' and choice != '2':
    choice = input("1. Faire l'appel :\n2. Enregistrer un nouveau badge\n\nChoix : ")

if choice == '1':
    choice = 0
    lcd.clear()
    lcd.write("1.Par salle", 0)
    lcd.write("2.Par enseignant", 1)
    choice = input('Recherche cours par :\n1. Salle\n2. Enseignant\n\nChoix : ')
    while choice != '1' and choice != '2':
        choice = input('Recherche cours par :\n1. Salle\n2. Enseignant\n\nChoix : ')

    if choice == '1':
        lcd.clear()
        lcd.write("Entrez salle :")
        nSalle = input("Salle : ")
        cleSalle = hp.getSalleByName(nSalle)

        if cleSalle == None:
            lcd.clear()
            lcd.write("Salle inconnue")
            print('Salle inconnue')
            exit()

        lcd.clear()
        lcd.write("Salle trouvee", 0)
        lcd.write("Recherche cours", 1)
        lCours = hp.getCoursSalleOfDayByKey(cleSalle, date.today())
        print("Cours récupérés")
        print(f"Affichage des cours : {len(lCours)}, {lCours}")

        timeDifference = 999999999999
        for coursData in lCours:
            if (min(coursData.getTimeDifference(), timeDifference) != timeDifference) :
                currentCourse = coursData
            timeDifference = min(coursData.getTimeDifference(), timeDifference)
            lcd.write(coursData.debut.strftime("%H:%M") + ' - ' + coursData.fin.strftime("%H:%M") + ' : ' + coursData.getLibelleMatiere())
        
        if (currentCourse == None) :
            exit()
        timerActivity.start()
        startTimeMinuts = datetime.now().strftime("%M")
        print(startTimeMinuts)
        while(int(datetime.now().strftime("%M") < int(currentCourse.debut.strftime("%M")))) :
            id = nfc.read()
            while (id == None) :
                id = nfc.read()
            for etudiant in currentCourse.etudiants :
                if (etudiant.id == id) :
                    etudiant.presence = 1 
        while((int(datetime.now().strftime("%M") - int(currentCourse.debut.strftime("%M")))) <= 5) :
            id = nfc.read()
            while (id == None) :
                id = nfc.read()
            for etudiant in currentCourse.etudiants :
                if (etudiant.id == id) :
                    etudiant.presence = 2 
        for etudiant in currentCourse.etudiants :
            if (etudiant.presence == 0) :
                etudiant.hp.absentStudent(etudiant.cleEtudiant, currentCourse.debut, currentCourse.fin)
            if (etudiant.presence == 2) :
                etudiant.hp.lateStudent(etudiant.cleEtudiant, currentCourse.debut, currentCourse.fin)
 



    elif choice == '2':
        lcd.clear()
        lcd.write("Entrez nom", 0)
        lcd.write("enseignant :", 1)
        nEnseignant = input("Enseignant : ")
        cleEnseignant = hp.getEnseignantByName(nEnseignant)

        if cleEnseignant == None:
            lcd.clear()
            lcd.write("Enseignant", 0)
            lcd.write("inconnu", 1)
            print('Enseignant inconnu')
            exit()

        lcd.clear()
        lcd.write("Enseignant trouve", 0)
        lcd.write("Recherche cours", 1)

        lCours = hp.getCoursEnseignantOfDayByKey(cleEnseignant, date.today())
        print("Cours récupérés")
        print(f"Affichage des cours : {len(lCours)}, {lCours}")
        timeDifference = 999999999999
        for coursData in lCours:
            if (min(coursData.getTimeDifference(), timeDifference) != timeDifference) :
                currentCourse = coursData
            timeDifference = min(coursData.getTimeDifference(), timeDifference)
            lcd.write(coursData.debut.strftime("%H:%M") + ' - ' + coursData.fin.strftime("%H:%M") + ' : ' + coursData.getLibelleMatiere())
        

        if (currentCourse == None) :
            exit()
        timerActivity.start()
        startTimeMinuts = datetime.now().strftime("%M")
        print(startTimeMinuts)
        while(int(datetime.now().strftime("%M") < int(currentCourse.debut.strftime("%M")))) :
            id = nfc.read()
            while (id == None) :
                id = nfc.read()
            for etudiant in currentCourse.etudiants :
                if (etudiant.id == id) :
                    etudiant.presence = 1 
        while((int(datetime.now().strftime("%M") - int(currentCourse.debut.strftime("%M")))) <= 5) :
            id = nfc.read()
            while (id == None) :
                id = nfc.read()
            for etudiant in currentCourse.etudiants :
                if (etudiant.id == id) :
                    etudiant.presence = 2 
        for etudiant in currentCourse.etudiants :
            if (etudiant.presence == 0) :
                etudiant.hp.absentStudent(etudiant.cleEtudiant, currentCourse.debut, currentCourse.fin)
            if (etudiant.presence == 2) :
                etudiant.hp.lateStudent(etudiant.cleEtudiant, currentCourse.debut, currentCourse.fin)
 

    

elif choice == '2':
    lcd.clear()
    lcd.write("Entrez nom et   prenom etudiant")
    nom = input("Veuillez entrer le nom et prénom de l'étudiant : ")
    lcd.clear()
    lcd.write("Recherche de    l'etudiant...")
    student = hp.getEtudiantByName(nom)

    if student != None :
        lcd.clear()
        lcd.write("Etudiant trouve Scannez badge")
        nfc.__init__()
        print("Veuillez scanner le badge :")
        id = str(nfc.read())
        print(student.cleEtudiant, student.nom, student.prenom, '-->', id)
        hp.changeStudentID(student.cleEtudiant, id)
        lcd.clear()
        lcd.write(student.nom + " " + student.prenom, 0)
        lcd.write(id, 1)
        time.sleep(10)
    else :
        lcd.clear()
        lcd.write("Etudiant inconnu")
