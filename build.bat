print('run \'pipenv shell\' first')

pip install -r requirements.txt

pyinstaller ./src/main.py -i ./src/tools/resouces/icon/logo.ico