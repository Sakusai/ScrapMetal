## Python VENV & Packages



### Create python virtual environment

To create a python environment on Windows, execute the following command : 
`python -m venv <environment-name>`

To create a python environment on MaxOS/Linux, execute the following command : 
`python3 -m venv <environment-name>`



### Activate/Deactivate python virtual environment

To activate a python environment on Windows, do as such :  
`<environment-name>\Scripts\activate`

To activate a python environment on MacOS/Linux, do as such :  
`source <environment-name>/bin/activate`

To deactivate a python environment on all systems, execute : `deactivate`



### Python packages dependencies

To save your python venv's packages dependencies in a requirements text file. You can execute the following command :  
`pip freeze > requirements.txt`

To install packages from a requirements.txt file, do the following :  
`pip install -r requirements.txt` 



### Pip-autoremove

This package removes a specified package and its unused dependencies, helping to clean up your Python environment.

To install pip-autoremove, run:  
`pip install pip-autoremove`

To remove a package (or multiple) and its unused dependencies, use:  
`pip-autoremove <package_name1> <package_name2> ... -y`

To list unused dependencies without uninstalling them, use the -l flag:  
`pip-autoremove -l`