$pwd = Get-Location
wt --window 0 -p "Windows Powershell" -d . powershell -noExit "python $pwd/scripts/run_api.py dev"
wt --window 0 -p "Windows Powershell" -d . powershell -noExit "python $pwd/scripts/run_nginx.py dev"
wt --window 0 -p "Windows Powershell" -d . powershell -noExit "python $pwd/scripts/run_webserver.py dev"