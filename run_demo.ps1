# One-click demo start. Right-click > Run with PowerShell, or in the VS Code terminal:  .\run_demo.ps1
$env:DEMO_MODE = "1"
$env:DEMO_PASSWORD = "CareFlow-Demo-2026!"
$py = ".\.venv\Scripts\python.exe"
& $py -m flask --app app db upgrade
& $py -m flask --app app seed-demo 2>$null          # skipped automatically if demo data already exists
& $py -m flask --app app reset-demo-passwords        # every demo login = CareFlow-Demo-2026!
Write-Host ""
Write-Host "Open http://127.0.0.1:5000/login  -  demo password: CareFlow-Demo-2026!" -ForegroundColor Green
& $py -m flask --app app run
