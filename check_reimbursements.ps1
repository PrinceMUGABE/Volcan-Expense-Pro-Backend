# check_reimbursements.ps1
$ErrorActionPreference = "Stop"

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/reimbursement/reimbursements-check/" -Method GET
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "Status: $($result.status)"
    Write-Host "Message: $($result.message)"
    Write-Host "Timestamp: $($result.timestamp)"
    
    # Log to file
    $logMessage = "$(Get-Date) - $($result.status): $($result.message)"
    Add-Content -Path "reimbursement_checks.log" -Value $logMessage
} catch {
    $errorMessage = "$(Get-Date) - ERROR: $_"
    Write-Host $errorMessage
    Add-Content -Path "reimbursement_checks.log" -Value $errorMessage
}