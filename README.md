# ss-rates

Shree SS Jewellers ka live rate board app ("Shree SS Jew.").

- `SS-Rates.apk` : latest app
- `version.json` : app isse naya APK version check karta hai (popup aata hai)
- `config.json`  : bina update ke badalne wali settings (sirf data: text, banner, links, rates, rang)
- `source/`      : app ka source (signing key yahan nahi hai)

## Laptop / TV board (desktop/)
`desktop/rate_board.html` = app jaisa design (glass, 3D shimmer naam, running line, funny popup) laptop ke liye.
C:\RateBoard me purani `rate_board.html` ki jagah ye file rakho (serve.py aur start_board.bat wahi rahenge). config.json se text/rates yahan bhi badalte hain.
