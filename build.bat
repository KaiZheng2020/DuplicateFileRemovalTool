print('run \'pipenv shell\' first')

pyside6-rcc.exe -o ./src/tools/gui/qt/resources/res.py ./src/tools/gui/qt/resources/res.qrc 

pip install -r requirements.txt

pyinstaller ./src/main.py -i ./src/tools/gui/qt/resources/icon/logo.ico