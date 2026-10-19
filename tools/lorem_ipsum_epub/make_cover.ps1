param([string]$Out = "$PSScriptRoot\cover.jpg")

Add-Type -AssemblyName System.Drawing

$w = 1200; $h = 1800
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
$g.TextRenderingHint = 'AntiAliasGridFit'

$bg = [System.Drawing.ColorTranslator]::FromHtml('#1F3A4D')
$ink = [System.Drawing.ColorTranslator]::FromHtml('#F3EAD7')
$accent = [System.Drawing.ColorTranslator]::FromHtml('#C9A45C')

$g.Clear($bg)

$pen = New-Object System.Drawing.Pen $accent, 6
$g.DrawRectangle($pen, 60, 60, $w - 120, $h - 120)
$thin = New-Object System.Drawing.Pen $accent, 2
$g.DrawRectangle($thin, 84, 84, $w - 168, $h - 168)

$center = New-Object System.Drawing.StringFormat
$center.Alignment = 'Center'
$center.LineAlignment = 'Center'

$inkBrush = New-Object System.Drawing.SolidBrush $ink
$accentBrush = New-Object System.Drawing.SolidBrush $accent

$titleFont = New-Object System.Drawing.Font 'Georgia', 150, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
$subFont = New-Object System.Drawing.Font 'Georgia', 64, ([System.Drawing.FontStyle]::Italic), ([System.Drawing.GraphicsUnit]::Pixel)
$volFont = New-Object System.Drawing.Font 'Georgia', 72, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
$footFont = New-Object System.Drawing.Font 'Georgia', 40, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)

$g.DrawString('LOREM', $titleFont, $inkBrush, (New-Object System.Drawing.RectangleF 0, 520, $w, 190), $center)
$g.DrawString('IPSUM', $titleFont, $inkBrush, (New-Object System.Drawing.RectangleF 0, 700, $w, 190), $center)

$g.DrawLine($pen, 400, 940, 800, 940)
$g.DrawString('dolor sit amet', $subFont, $accentBrush, (New-Object System.Drawing.RectangleF 0, 990, $w, 100), $center)

$g.DrawString('Volume 1', $volFont, $inkBrush, (New-Object System.Drawing.RectangleF 0, 1400, $w, 110), $center)
$g.DrawString('A test book', $footFont, $accentBrush, (New-Object System.Drawing.RectangleF 0, 1560, $w, 70), $center)

$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$params = New-Object System.Drawing.Imaging.EncoderParameters 1
$params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 90L
$bmp.Save($Out, $codec, $params)

$g.Dispose(); $bmp.Dispose()
Get-Item $Out | Select-Object FullName, Length
