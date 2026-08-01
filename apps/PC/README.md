Build to exe file

pyinstaller --onefile --windowed --add-data "E:\projects\Benefit Harm\apps;apps" --add-data "E:\projects\Benefit Harm\py_model;py_model" main.py