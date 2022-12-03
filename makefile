# Create a single executable file for the python application main.py
# The executable file will be named Downloader.exe
# The executable file will be created in the dist folder
# The executable file will be created for the Windows operating system

create_executable:
	pyinstaller --onefile --windowed --icon=download.ico main.py --name Downloader
	cp ./download.png ./dist/download.png
	cp ./download.ico ./dist/download.ico

create_icon_from_png:
	convert -background transparent "download.png" -define icon:auto-resize=16,24,32,48,64,72,96,128,256 "download.ico"
