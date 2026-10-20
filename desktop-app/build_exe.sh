#!/bin/sh
# Windows exe banata hai: ./build_exe.sh   (Go chahiye; icon ke liye: npm install resedit)
set -e
cd "$(dirname "$0")"
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-H=windowsgui -s -w" -o SSRateBoard-basic.exe .
node brand.js SSRateBoard-basic.exe icon.ico SSRateBoard.exe
echo done
