param (
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Urls
)

yt-dlp `
  -o "%(playlist_index)02d-%(title)s [%(id)s].%(ext)s" `
  --progress `
  --remux-video mp4 `
  --embed-subs `
  --embed-thumbnail `
  --embed-info-json `
  --no-warnings `
  $Urls


Write-Host "All tasks completed!"

$player = New-Object System.Media.SoundPlayer "C:\Windows\Media\Windows Notify System Generic.wav"
$player.PlaySync()
