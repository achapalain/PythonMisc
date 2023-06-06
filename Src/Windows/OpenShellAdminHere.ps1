param([String]$scriptToExec="")
$scriptPath = $MyInvocation.MyCommand.Path
$dir = Split-Path $scriptPath
if ($scriptToExec -eq "")
{
	Start-Process powershell -Verb runAs -ArgumentList "-NoExit", "-Command cd $dir"
}
else
{
	Start-Process powershell -Verb runAs -ArgumentList "-Command cd $dir ; Set-ExecutionPolicy RemoteSigned ; .\$scriptToExec"
}