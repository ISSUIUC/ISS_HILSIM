$pwd = Get-Location
wt --window 0 -p "Windows Powershell" -d . powershell -noExit "python $pwd/scripts/run_api.py prod"
wt --window 0 -p "Windows Powershell" -d . powershell -noExit "python $pwd/scripts/run_nginx.py prod"
wt --window 0 -p "Windows Powershell" -d . powershell -noExit "python $pwd/scripts/build_webserver.py prod"