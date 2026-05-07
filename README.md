# Lancer le projet

Pour lancer le projet (voir aide, peut différer en fonction de l'OS) :
- Créer un environnement virtuel
- Activer l'environnement virtuel
- Installer les dépendances depuis le fichier "requirements.txt" (Veiller à bien sélectionner l'interpréteur de l'environnement virtuel)  
- Copier le fichier ".env.example" vers ".env" et remplir les identifiants avec un compte Membre Boursorama
- Finalement, lancer le fichier "main.py"

<br>

# Aide

## Python VENV & Packages

### Create python virtual environment

To create a python environment on Windows, execute the following command : 
`python -m venv <environment-name>`

To create a python environment on MaxOS/Linux, execute the following command : 
`python3 -m venv <environment-name>`

<br>

### Activate/Deactivate python virtual environment

To activate a python environment on Windows, do as such :  
`<environment-name>\Scripts\activate`

To activate a python environment on MacOS/Linux, do as such :  
`source <environment-name>/bin/activate`

To deactivate a python environment on all systems, execute : `deactivate`

<br>

### Python packages dependencies

To save your python venv's packages dependencies in a requirements text file. You can execute the following command :  
`pip freeze > requirements.txt`

To install packages from a requirements.txt file, do the following :  
`pip install -r requirements.txt` 

<br>

### Pipdeptree

This package displays the dependency tree of installed Python packages, helping you understand which packages depend on which others in your environment.

To install pipdeptree, run:
`pip install pipdeptree`

To display the full dependency tree, use:
`pipdeptree`

To display the dependency tree for a specific package, use:
`pipdeptree -p <package-name>`

To find possible conflicting dependencies, use:
`pipdeptree --warn fail`