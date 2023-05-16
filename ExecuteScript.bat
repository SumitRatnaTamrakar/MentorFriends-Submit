@echo off
python -m venv .myVenv
call .myVenv\Scripts\activate
echo Installing dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_md
echo Running python script
python script.py
echo Complete
echo Press any key to close
timeout /t -1