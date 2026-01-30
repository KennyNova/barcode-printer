1..254 | ForEach-Object {
  $ip = "10.200.185.$_"
  if (Test-Connection -ComputerName $ip -Count 1 -Quiet) {
    Write-Output $ip
  }
}