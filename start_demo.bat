@echo off
echo ========================================
echo    DEMARRAGE AGRIDETECT AI
echo ========================================

cd /d E:\Projet_Test2\AgriDetec_test

echo.
echo [1/2] Demarrage du Backend...
start "Backend" cmd /k "call venv\Scripts\activate && set AGRIDETECT_MODEL_PATH=E:\Projet_Test2\AgriDetec_test\models\agridetect_model_20251107_042206 && python main.py"

timeout /t 10

echo.
echo [2/2] Demarrage de l'application mobile...
cd mobile
start "Mobile" cmd /k "npx expo start"

echo.
echo ========================================
echo   PRET POUR LA DEMO !
echo ========================================
pause