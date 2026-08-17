# Setup Windows Task Scheduler for AI Agent
# ==============================================================================

$PythonPath = "python" # Assumes python is in PATH
$ScriptPath = "C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\core\ai_agent.py"
$WorkingDirectory = "C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development"

$Days = @("Monday", "Wednesday", "Friday")
$Hours = @(9, 17)

foreach ($Day in $Days) {
    foreach ($Hour in $Hours) {
        $TaskName = "AI_Agent_$($Day)_$($Hour)"
        $TriggerTime = "$Hour:00"

        Write-Host "Creating task $TaskName for $Day at $TriggerTime..."

        # Create the scheduled task using schtasks.exe
        $Action = "$PythonPath $ScriptPath"
        $Schedule = "WEEKLY"
        # Day of week for schtasks: MON, TUE, WED, THU, FRI, SAT, SUN
        $DayShort = $Day.Substring(0,3).ToUpper()

        schtasks /create /tn "$TaskName" /tr "$Action" /sc $Schedule /d $DayShort /st $TriggerTime /f
    }
}

Write-Host "All tasks created successfully."
