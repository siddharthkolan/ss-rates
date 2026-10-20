# ss-rates

Shree SS Jewellers ka live rate board app ("Shree SS Jew.").

- `SS-Rates.apk` : latest app
- `version.json` : app isse naya APK version check karta hai (popup aata hai)
- `config.json`  : bina update ke badalne wali settings (sirf data: text, banner, links, rates, rang)
- `source/`      : app ka source (signing key yahan nahi hai)

## Laptop / TV board (desktop/)
`desktop/rate_board.html` = app jaisa design (glass, 3D shimmer naam, running line, funny popup) laptop ke liye.
C:\RateBoard me purani `rate_board.html` ki jagah ye file rakho (serve.py aur start_board.bat wahi rahenge). config.json se text/rates yahan bhi badalte hain.

## Windows .exe (desktop-app/)
`desktop-app/SSRateBoard.exe` = ek hi file. Double-click karo: rates leta hai, board app window (Edge/Chrome) me kholta hai. Logo/icon exe me hai. Agar SSRateBoard.exe na khule to SSRateBoard-basic.exe (bina icon) try karo.
Board ke neeche-right ke 3 dot (⋮) menu me "PC ke saath auto start" on/off. Band karne ke liye Alt+F4. Log: %LocalAppData%\SSRateBoard\log.txt
Source: main.go (Go, bina kisi library ke). Build: `GOOS=windows GOARCH=amd64 go build -trimpath -ldflags "-H=windowsgui -s -w" -o SSRateBoard.exe .`
