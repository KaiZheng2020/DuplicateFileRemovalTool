echo 'run "pipenv shell" first'

pyside6-rcc.exe -o ./src/tools/gui/resources/resource.py ./src/tools/gui/resources/resource.qrc 

pip install -r requirements.txt

pyinstaller ./src/main.py -i ./src/tools/gui/resources/icon/logo.ico