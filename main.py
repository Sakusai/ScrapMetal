# from playwright.sync_api import sync_playwright
# import re
# import pandas as pd
# from pathlib import Path

# with sync_playwright() as pw:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()

#     page.goto("http://boursorama.com/bourse/actions/cotations/")

from db.database import Base, engine, SessionLocal
from models.cours import Cours

# Créer les tables
def create_tables():
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

# Ajouter des cours
def add_cours():
    session = SessionLocal()
    try:
        cours1 = Cours(name="ACCOR")
        session.add_all([cours1])
        session.commit()
        print("Cours ajoutés avec succès !")
    finally:
        session.close()

# Lire tous les cours
def get_cours():
    session = SessionLocal()
    try:
        cours = session.query(Cours).all()
        for c in cours:
            print(f"ID: {c.id_cours}, Name: {c.name}")
    finally:
        session.close()

# Mettre à jour un cours
def update_cours(cours_id, new_name):
    session = SessionLocal()
    try:
        cours = session.query(Cours).filter(Cours.id_cours == cours_id).first()
        if cours:
            cours.name = new_name
            session.commit()
            print(f"Cours {cours_id} mis à jour avec succès !")
        else:
            print(f"Aucun cours trouvé avec l'ID {cours_id}")
    finally:
        session.close()

# Supprimer un cours
def delete_cours(cours_id):
    session = SessionLocal()
    try:
        cours = session.query(Cours).filter(Cours.id_cours == cours_id).first()
        if cours:
            session.delete(cours)
            session.commit()
            print(f"Cours {cours_id} supprimé avec succès !")
        else:
            print(f"Aucun cours trouvé avec l'ID {cours_id}")
    finally:
        session.close()

# Menu principal
if __name__ == "__main__":
    print("Options disponibles :")
    print("1 : Créer les tables")
    print("2 : Ajouter des cours")
    print("3 : Lire les cours")
    print("4 : Mettre à jour un cours")
    print("5 : Supprimer un cours")

    choice = input("Entrez le numéro de l'opération : ")

    if choice == "1":
        create_tables()
    elif choice == "2":
        add_cours()
    elif choice == "3":
        get_cours()
    elif choice == "4":
        cours_id = int(input("ID du cours à mettre à jour : "))
        new_name = input("Nouveau nom : ")
        update_cours(cours_id, new_name)
    elif choice == "5":
        cours_id = int(input("ID du cours à supprimer : "))
        delete_cours(cours_id)
    else:
        print("Choix invalide.")