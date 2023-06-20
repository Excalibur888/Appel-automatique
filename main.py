coding: utf-8

from Classes.hyperplanning import HyperPlanningClient, Etudiant
from datetime import date, datetime
import time
import threading
from Classes.Reader import Reader

def inactivityProcess():
    lcd.clear()
    lcd.disableScreen()
    print('Inactivité détectée')

timerActivity = threading.Timer(60, inactivityProcess)

hp = HyperPlanningClient()
nfc = Reader()
id = None

print('Connecté à ' + hp.getVersion())

choice = input("1. Faire l'appel :\n2. Enregistrer un nouveau badge\n\nChoix : ")
while choice != '1' and choice != '2':
    choice = input("1. Faire l'appel :\n2. Enregistrer un nouveau badge\n\nChoix : ")

if choice == '1':
    choice = 0
    choice = input('Recherche cours par :\n1. Salle\n2. Enseignant\n\nChoix : ')
    while choice != '1' and choice != '2':
        choice = input('Recherche cours par :\n1. Salle\n2. Enseignant\n\nChoix : ')

    if choice == '1':
        nSalle = input("Salle : ")
        cleSalle = hp.getSalleByName(nSalle)

        if cleSalle == None:
            print('Salle inconnue')
            exit()

        lCours = hp.getCoursSalleOfDayByKey(cleSalle, date.today())
        for coursData in lCours:
            print(f"{coursData.debut.strftime('%H:%M')} - {coursData.fin.strftime('%H:%M')} : {coursData.getLibelleMatiere()}")
            print(coursData.getTimeDifference())
            lcd.write(coursData.debut.strftime("%H:%M") + ' - ' + coursData.fin.strftime("%H:%M") + ' : ' + coursData.getLibelleMatiere())
        
        timerActivity.start()
        startTimeMinuts = datetime.now().strftime("%M")
        print(startTimeMinuts)
        while(int(datetime.now().strftime("%M") < int(lCours.debut.strftime("%M")))) :
            id = nfc.read()
            while (id == None) :
                id = nfc.read()
            for etudiant in lCours.etudiants :
                if (etudiant.id == id) :
                    etudiant.presence = 1 
        while((int(datetime.now().strftime("%M") - int(lCours.debut.strftime("%M")))) <= 5) :
            id = nfc.read()
            while (id == None) :
                id = nfc.read()
            for etudiant in lCours.etudiants :
                if (etudiant.id == id) :
                    etudiant.presence = 2 
        for etudiant in lCours.etudiants :
            if (etudiant.presence == 0) :
                etudiant.hp.absentStudent(etudiant.cleEtudiant, lCours.debut, lCours.fin)
            if (etudiant.presence == 2) :
                etudiant.hp.lateStudent(etudiant.cleEtudiant, lCours.debut, lCours.fin)
 



    elif choice == '2':
        nEnseignant = input("Enseignant : ")
        cleEnseignant = hp.getEnseignantByName(nEnseignant)

        if cleEnseignant == None:
            print('Enseignant inconnu')
            exit()
        print(f"Clé enseignant {cleEnseignant}")

        lCours = hp.getCoursEnseignantOfDayByKey(cleEnseignant, date.today())
        print("Cours récupérés")
        print(f"Affichage des cours : {len(lCours)}, {lCours}")
        for coursData in lCours:
            print(f"{coursData.debut.strftime('%H:%M')} - {coursData.fin.strftime('%H:%M')} : {coursData.getLibelleMatiere()}")
            print(coursData.getTimeDifference())
            lcd.write(coursData.debut.strftime("%H:%M") + ' - ' + coursData.fin.strftime("%H:%M") + ' : ' + coursData.getLibelleMatiere())
        timerActivity.start()

    

elif choice == '2':
    nom = input("Veuillez entrer le nom et prénom de l'étudiant : ")
    student = hp.getEtudiantByName(nom)
    if student != None :
        print("Veuillez scanner le badge :")
        id = nfc.read()
        while (id == None) :
            id = nfc.read()
        print(student.cleEtudiant, student.nom, student.prenom, '-->', id)
        hp.changeStudentID(student.cleEtudiant, id)
    
