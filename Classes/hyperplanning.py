from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from configparser import ConfigParser
from enum import Enum
from datetime import datetime, timedelta, date

# Lecture du fichier de configuration
config = ConfigParser()
config.read('./config.ini', encoding='utf-8')

# Enumération des interfaces utilisées
class Interface(Enum):
    Absence = 'IHpSvcWAbsences'
    Appariteurs = 'IHpSvcWAppariteurs'
    Communication = 'IHpSvcWCommunication'
    Cours = 'IHpSvcWCours'
    CoursAnnules = 'IHpSvcWCoursAnnules'
    CoutsHoraires = 'IHpSvcWCoutsHoraires'
    Decharges = 'IHpSvcWDecharges'
    Dispenses = 'IHpSvcWDispenses'
    Enseignants = 'IHpSvcWEnseignants'
    Etudiants = 'IHpSvcWEtudiants'
    Familles = 'IHpSvcWFamilles'
    Matieres = 'IHpSvcWMatieres'
    ModulesCursus = 'IHpSvcWModulesCursus'
    Notation = 'IHpSvcWNotation'
    Parents = 'IHpSvcWParents'
    Promotion = 'IHpSvcWPromotions'
    Regroupements = 'IHpSvcWRegroupements'
    Salles = 'IHpSvcWSalles'
    Stages = 'IHpSvcWStages'
    TDOptions = 'IHpSvcWTDOptions'
    Utilisateurs = 'IHpSvcWUtilisateurs'
    Admin = 'IHpSvcWAdmin'

class Etudiant():

    def __init__(self, cleEtudiant: str, nom: str, prenom: str, id: str = "-1") -> None:
        self.cleEtudiant = cleEtudiant
        self.nom = nom
        self.prenom = prenom
        self.presence = 0 # 0 absent, 1 présent, 2 retard
        self.id = id

    def activePresence(self) -> None:
        self.presence = True

# Classe qui représente un cours
class Cours():

    # Fonction d'initialisation de la classe
    def __init__(self, cleCours: str, cleMatiere: str, debut: date, fin: date) -> None:
        self.cleCours = cleCours
        self.cleMatiere = cleMatiere
        self.debut = debut
        self.fin = fin
        self.etudiants = self.getEtudiants()

    # Fonction qui retourne le libellé de la matière
    def getLibelleMatiere(self) -> str:
        matiere = HyperPlanningClient().getDataByInterface(Interface.Matieres)
        return matiere.LibelleMatiere(self.cleMatiere)

    def     getEtudiants(self) -> list:
        cours = HyperPlanningClient().getDataByInterface(Interface.Cours)

        lEtudiant = []

        for cleEtudiant in cours.EtudiantsDuCours(self.cleCours):
            lEtudiant.append(HyperPlanningClient().getEtudiantByKey(cleEtudiant))
            
        return sorted(lEtudiant, key=lambda etudiant: etudiant.nom + etudiant.prenom)
    
    def getTimeDifference(self) -> float:
        return (datetime.now() - self.debut).total_seconds()

# Classe qui représente l'api Hyperplanning
class HyperPlanningClient:

    students = {}

    # Fonction d'initialisation de la classe
    def __init__(self) -> None:
        self.session = Session()
        self.session.auth = HTTPBasicAuth(config['HYPERPLANNING']['username'], config['HYPERPLANNING']['password'])
        self.prefixeWsdl = config['HYPERPLANNING']['url']

    # Fonction qui retourne un objet de type Client avec les données demandées par l'interface
    def getDataByInterface(self, interface: Interface) -> Client:
        return Client(self.prefixeWsdl + interface.value, transport=Transport(session=self.session)).service
    
    # Fonctions qui retourne la clé d'une salle ou d'un enseignant à partir de son nom
    def getSalleByName(self, name) -> str | None:
        salles = self.getDataByInterface(Interface.Salles)

        lCles = salles.TrierTableauDeSallesParNomEtCode({'THpSvcWCleSalle' : salles.ToutesLesSalles()})
        lCodes = salles.CodesTableauDeSalles({'THpSvcWCleSalle' : lCles})

        for i in range(len(lCles)):
            if lCodes[i] == name:
                return lCles[i]

        return None
              
    def getEnseignantByName(self, name: str, __retry: bool = True) -> str | None:
        enseignants = self.getDataByInterface(Interface.Enseignants)

        lCles = enseignants.TrierTableauDEnseignantsParNomPrenomEtCode({'THpSvcWCleEnseignant': enseignants.TousLesEnseignants()})

        for i in range(len(lCles)):
            nomPrenomEnseignant = str(str(enseignants.NomEnseignant(lCles[i])) + ' ' + str(enseignants.PrenomEnseignant(lCles[i]))).lower().replace("-", " ")
            prenomNomEnseignant = str(str(enseignants.PrenomEnseignant(lCles[i])) + ' ' + str(enseignants.NomEnseignant(lCles[i]))).lower().replace("-", " ")
            if (nomPrenomEnseignant == name.lower() or prenomNomEnseignant == name.lower()):
                return lCles[i]

        return None
    
    def getEtudiantByName(self, name: str, __retry: bool = True) -> Etudiant | None:
        etudiants = self.getDataByInterface(Interface.Etudiants)

        lCles = etudiants.TousLesEtudiants()

        print('Recherche de l\'étudiant...')
        for i in range(len(lCles)):
            nomPrenomEtudiant = str(str(etudiants.NomEtudiant(lCles[i])) + ' ' + str(etudiants.PrenomEtudiant(lCles[i]))).lower().replace("-", " ")
            prenomNomEtudiant = str(str(etudiants.PrenomEtudiant(lCles[i])) + ' ' + str(etudiants.NomEtudiant(lCles[i]))).lower().replace("-", " ")
            if (nomPrenomEtudiant == name.lower() or prenomNomEtudiant == name.lower()):
                print('Etudiant trouvé.')
                return Etudiant(lCles[i], str(etudiants.NomEtudiant(lCles[i])), str(etudiants.PrenomEtudiant(lCles[i])))
            
        print('Etudiant non trouvé.')
        return None

    def getEtudiantByKey(self, key: str) -> Etudiant | None:
        etudiants = self.getDataByInterface(Interface.Etudiants)

        lCles = etudiants.TrierTableauDEtudiantsParNomPrenomEtDateDeNaissance({'THpSvcWCleEtudiant': etudiants.TousLesEtudiants()})

        for i in range(len(lCles)):
            self.students[lCles[i]] = Etudiant(lCles[i], str(etudiants.NomEtudiant(lCles[i])), str(etudiants.PrenomEtudiant(lCles[i])), str(etudiants.NumeroSecuriteSocialeEtudiant(lCles[i])))
            if (lCles[i] == str(key)):
                return self.students[lCles[i]]
            
        return None

    # Fonctions qui retourne la liste des cours d'une salle ou d'un enseignant à une date donnée
    def getCoursSalleOfDayByKey(self, cleSalle: str, date: date) -> list[Cours]:
        admin = self.getDataByInterface(Interface.Admin)
        salles = self.getDataByInterface(Interface.Salles)
        cours = self.getDataByInterface(Interface.Cours)

        lCours = []

        for cleCours in salles.CoursSalleEntre2Dates(cleSalle, date, date):
            cleMatiere = cours.MatiereCours(cleCours)

            infoHoraire = admin.HpSvcWDureeEnHeureMinute(cours.PlaceCours(cleCours))
            debut = datetime.now().replace(hour=infoHoraire['AHeure'] % 24, minute=infoHoraire['AMinute'])

            infoDuree = admin.HpSvcWDureeEnHeureMinute(cours.DureeCours(cleCours))
            fin = debut + timedelta(0, 0, 0, 0, infoDuree['AMinute'], infoDuree['AHeure'])
            lCours.append(Cours(cleCours, cleMatiere, debut, fin))

        return sorted(lCours, key=lambda cours: cours.debut)

    def getCoursEnseignantOfDayByKey(self, cleEnseignant: str, date: date) -> list[Cours]:
        admin = self.getDataByInterface(Interface.Admin)
        enseignants = self.getDataByInterface(Interface.Enseignants)
        cours = self.getDataByInterface(Interface.Cours)

        lCours = []

        for cleCours in enseignants.CoursEnseignantEntre2Dates(cleEnseignant, date, date):
            cleMatiere = cours.MatiereCours(cleCours)

            infoHoraire = admin.HpSvcWDureeEnHeureMinute(cours.PlaceCours(cleCours))
            debut = datetime.now().replace(hour=infoHoraire['AHeure'] % 24, minute=infoHoraire['AMinute'])

            infoDuree = admin.HpSvcWDureeEnHeureMinute(cours.DureeCours(cleCours))
            fin = debut + timedelta(0, 0, 0, 0, infoDuree['AMinute'], infoDuree['AHeure'])
            lCours.append(Cours(cleCours, cleMatiere, debut, fin))

        return sorted(lCours, key=lambda cours: cours.debut)

    def getVersion(self) -> str:
        admin = self.getDataByInterface(Interface.Admin)
        return admin.Version()    

    def changeStudentID(self, key: str, studentID: str) -> bool:
        print('Ecriture dans l\'api...')
        etudiants = self.getDataByInterface(Interface.Etudiants)
        secu = etudiants.NumeroSecuriteSocialeEtudiant(key)
        print(f"Ancien numéro de sécu : {secu}")
        etudiants.ModifierNumeroSecuriteSocialeEtudiant(key, studentID)
        secu = etudiants.NumeroSecuriteSocialeEtudiant(key)
        print(f"Nouveau numéro de sécu : {secu}")
        if (secu == studentID):
            return True
        return False
    
    def absentStudent(self, key: str, start: str, end:str, reason: bool = False) :
        absence = self.getDataByInterface(Interface.Absence)
        absences = absence.AbsencesEtudiantEntre2Dates(key, start, end)
        for keyAbsence in absences :
            if (absence.AbsenceEtudiantEstJustifiee(keyAbsence)):
                reason = True
        absence.AjouterAbsenceEtudiant(key, start, end, reason)

    def lateStudent(self, key: str, start: str, end:str, reason: bool = False) :
        absence = self.getDataByInterface(Interface.Absence)
        lateness = absence.RetardsEtudiantEntre2Dates(key, start, end)
        for keyLateness in lateness :
            if (absence.AbsenceEtudiantEstJustifiee(keyLateness)):
                reason = True
        absence.CreerRetardEtudiant(key, start, end, reason)

    def addFakeCourse (self, subject : str = "3778" , lenght : str = "0,083", prof : str = "574", groupe : str = "22", promo : str = "174", option : str = "0", salle : str = "111", domaine : str = "1") -> str:
        cours : self.getDataByInterface(Interface.Cours)

        courseKey = cours.CreerCoursFixe("")
        return courseKey

    def get(self, key :str = "x") -> str:
        a = self.getDataByInterface(Interface.Cours)

        ar = a.TousLesCours ()
        #arb = a.PromotionEtudiant(key)
        #print(arb)
        for x in ar :
            if (a.EnseignantsDuCours (x) == "574") :
                print(x, "->", a.EnseignantsDuCours (x), "->", a.MatiereCours(x))