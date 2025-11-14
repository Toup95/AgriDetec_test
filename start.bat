@echo off
cd /d E:\Projet_Test2\AgriDetec_test
call venv\Scripts\activate
set AGRIDETECT_MODEL_PATH=E:\Projet_Test2\AgriDetec_test\models\agridetect_model_20251107_042206
python main.py
pause