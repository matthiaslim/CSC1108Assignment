# CSC1108Assignment

# Flight Map Routing Project

# Description

The flight routing paths is designed to efficiently search for flight routes using two airport points.

# Prerequisites

- Python 3.10.4 or later
- Pip 24.0 or later

# Environmental Variables

- Python 3.10.4 or later
- Pip 24.0 or later

# Step 1 : Installation of Python and Pip

- Python : [https://www.python.org/downloads/]
- Guide to install Python : [https://kinsta.com/knowledgebase/install-python/]
- Pip For Windows : [https://www.geeksforgeeks.org/how-to-install-pip-on-windows/]
- Pip For Mac/Unix : [https://phoenixnap.com/kb/install-pip-mac]

- After installation,verify that the python version are installed by opening command prompt/terminal and type the following commands:
- To Check Python Version: (python --version or python3 --version)
- To check pip Version: (pip --version or pip3 --version)
- Ensure Python and pip is inside your PATH environment.

# Step 2 : Setting up a Python environment

# To create a virtual environment

python -m venv env

# Use this line to activate the virtual environment

For Windows :

- .\env\Scripts\activate

For Mac/Unix OS:

- source env/bin/activate

# Step 3 : Installing dependencies

pip install -r requirements.txt

# Version Dependencies for Mac/Windows for PyQt5:

For Windows:
PyQt5-Qt5==5.15.2
PyQtWebEngine-Qt5==5.15.2

For Mac:
PyQt5-Qt5==5.15.12
PyQtWebEngine-Qt5==5.15.12

# Final Step : Running the Program

- Run the program through python map.py

# Packages needs to be install.

basemap==1.4.1
basemap-data==1.3.2
branca==0.7.1
Cartopy==0.22.0
certifi==2024.2.2
charset-normalizer==3.3.2
click==8.1.7
contourpy==1.2.0
customtkinter==5.2.2
cycler==0.12.1
darkdetect==0.8.0
decorator==5.1.1
folium==0.16.0
fonttools==4.49.0
future==1.0.0
geocoder==1.38.1
idna==3.6
Jinja2==3.1.3
kaleido==0.2.1
kiwisolver==1.4.5
MarkupSafe==2.1.5
matplotlib==3.8.3
numpy==1.26.4
packaging==23.2
pandas==2.2.1
pillow==10.2.0
plotly==5.19.0
pyparsing==3.1.2
pyperclip==1.8.2
pyproj==3.6.1
PyQt5==5.15.10
PyQt5-Qt5==5.15.12
PyQt5-sip==12.13.0
PyQtWebEngine==5.15.6
PyQtWebEngine-Qt5==5.15.12
pyshp==2.3.1
python-dateutil==2.9.0.post0
pytz==2024.1
ratelim==0.1.6
requests==2.31.0
shapely==2.0.3
six==1.16.0
tenacity==8.2.3
tkintermapview==1.29
tzdata==2024.1
urllib3==2.2.1
xyzservices==2023.10.1
