// Shree SS Jewellers - Rate Board (Windows .exe)
// Ek hi file: andar rates leta hai (har 1 sec), board page deta hai, aur Edge/Chrome ko app window me kholta hai.
package main

import (
	_ "embed"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

//go:embed rate_board.html
var pageHTML []byte

//go:embed logo.png
var logoPNG []byte

//go:embed favicon.png
var faviconPNG []byte

const defaultUpstream = "https://bcast.bhavyalaxmibullion.com:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/bhavyalaxmi"
const runKey = `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
const runName = "SSRateBoard"

type feedState struct {
	Text       string  `json:"text"`
	FetchedAt  float64 `json:"fetched_at"`
	OK         bool    `json:"ok"`
	Error      string  `json:"error"`
	ServerTime float64 `json:"server_time"`
}

var (
	mu      sync.Mutex
	state   = feedState{Error: "starting"}
	dataDir string
)

func nowSec() float64 { return float64(time.Now().UnixNano()) / 1e9 }

func logf(format string, a ...interface{}) {
	if dataDir == "" {
		return
	}
	f, err := os.OpenFile(filepath.Join(dataDir, "log.txt"), os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return
	}
	defer f.Close()
	fmt.Fprintf(f, "%s  %s\n", time.Now().Format("2006-01-02 15:04:05"), fmt.Sprintf(format, a...))
}

func poller(upstream string) {
	client := &http.Client{Timeout: 5 * time.Second}
	lastErr := ""
	for {
		req, _ := http.NewRequest("GET", upstream, nil)
		req.Header.Set("User-Agent", "ShopRateBoard/1.0")
		resp, err := client.Do(req)
		if err == nil {
			body, rerr := io.ReadAll(io.LimitReader(resp.Body, 4<<20))
			resp.Body.Close()
			if rerr == nil && resp.StatusCode == 200 && len(body) > 20 {
				mu.Lock()
				state = feedState{Text: string(body), FetchedAt: nowSec(), OK: true}
				mu.Unlock()
				lastErr = ""
				time.Sleep(time.Second)
				continue
			}
			if rerr != nil {
				err = rerr
			} else {
				err = fmt.Errorf("status %d", resp.StatusCode)
			}
		}
		mu.Lock()
		state.OK = false
		state.Error = err.Error()
		mu.Unlock()
		if err.Error() != lastErr { // log me baar-baar ek hi error nahi
			logf("feed error: %v", err)
			lastErr = err.Error()
		}
		time.Sleep(time.Second)
	}
}

// sirf isi PC ka board page (localhost) auto start badal sakta hai, koi dusri website ya device nahi
func localOnly(r *http.Request) bool {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil || !net.ParseIP(host).IsLoopback() {
		return false
	}
	h := r.Host
	if i := strings.LastIndex(h, ":"); i >= 0 {
		h = h[:i]
	}
	if h != "localhost" && h != "127.0.0.1" || r.Header.Get("X-SS-Board") != "1" {
		return false
	}
	if o := r.Header.Get("Origin"); o != "" { // page apna hi ho (localhost), kisi aur site ka nahi
		u, err := url.Parse(o)
		if err != nil || (u.Hostname() != "localhost" && u.Hostname() != "127.0.0.1") {
			return false
		}
	}
	return true
}

func newMux() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/api/startup", func(w http.ResponseWriter, r *http.Request) {
		if !localOnly(r) {
			http.Error(w, "forbidden", http.StatusForbidden)
			return
		}
		if r.Method == http.MethodPost {
			var body struct {
				On bool `json:"on"`
			}
			if json.NewDecoder(io.LimitReader(r.Body, 1024)).Decode(&body) != nil {
				http.Error(w, "bad request", http.StatusBadRequest)
				return
			}
			setStartup(body.On)
		}
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Cache-Control", "no-store")
		json.NewEncoder(w).Encode(map[string]bool{"on": startupEnabled()})
	})
	mux.HandleFunc("/feed", func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		s := state
		mu.Unlock()
		s.ServerTime = nowSec()
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		json.NewEncoder(w).Encode(s)
	})
	mux.HandleFunc("/favicon.png", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "image/png")
		w.Write(faviconPNG)
	})
	mux.HandleFunc("/logo.png", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "image/png")
		w.Write(logoPNG)
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" && r.URL.Path != "/index.html" {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		w.Write(pageHTML)
	})
	return mux
}

// pehle se chal raha apna server mile to wahi use karo (do baar double-click par dusra server nahi banta)
func existingPort() int {
	c := &http.Client{Timeout: 700 * time.Millisecond}
	for p := 8000; p <= 8010; p++ {
		resp, err := c.Get(fmt.Sprintf("http://127.0.0.1:%d/feed", p))
		if err != nil {
			continue
		}
		var s feedState
		ok := json.NewDecoder(resp.Body).Decode(&s) == nil && s.ServerTime > 0
		resp.Body.Close()
		if ok {
			return p
		}
	}
	return 0
}

func existsFile(p string) bool { st, err := os.Stat(p); return err == nil && !st.IsDir() }

func findBrowser() (path, kind string) {
	pf, pf86, la := os.Getenv("ProgramFiles"), os.Getenv("ProgramFiles(x86)"), os.Getenv("LocalAppData")
	for _, c := range []string{
		filepath.Join(pf86, `Microsoft\Edge\Application\msedge.exe`),
		filepath.Join(pf, `Microsoft\Edge\Application\msedge.exe`),
	} {
		if existsFile(c) {
			return c, "edge"
		}
	}
	for _, c := range []string{
		filepath.Join(pf, `Google\Chrome\Application\chrome.exe`),
		filepath.Join(pf86, `Google\Chrome\Application\chrome.exe`),
		filepath.Join(la, `Google\Chrome\Application\chrome.exe`),
	} {
		if existsFile(c) {
			return c, "chrome"
		}
	}
	for _, c := range []string{
		filepath.Join(pf, `Mozilla Firefox\firefox.exe`),
		filepath.Join(pf86, `Mozilla Firefox\firefox.exe`),
	} {
		if existsFile(c) {
			return c, "firefox"
		}
	}
	return "", ""
}

func runHidden(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	hideWindow(cmd)
	return cmd.Run()
}

func openBrowser(url string) {
	path, kind := findBrowser()
	if path == "" {
		logf("koi supported browser nahi mila, default browser se khol raha hu")
		runHidden("rundll32", "url.dll,FileProtocolHandler", url)
		select {} // server chalta rahe
	}
	var args []string
	switch kind {
	case "firefox":
		args = []string{"-new-window", url}
	default:
		// app window: address bar/tabs nahi, par normal (full screen nahi) window. F dabane par full screen.
		profile := filepath.Join(dataDir, "browser-profile")
		args = []string{"--app=" + url, "--window-size=1280,800", "--user-data-dir=" + profile, "--no-first-run", "--no-default-browser-check",
			"--disable-infobars", "--noerrdialogs", "--autoplay-policy=no-user-gesture-required",
			"--overscroll-history-navigation=0", "--disable-features=Translate,TranslateUI"}
	}
	logf("browser: %s (%s) %s", path, kind, url)
	cmd := exec.Command(path, args...)
	start := time.Now()
	if err := cmd.Start(); err != nil {
		logf("browser start error: %v", err)
		select {}
	}
	cmd.Wait()
	if time.Since(start) < 8*time.Second {
		logf("browser jaldi band hua (%v) - server chalta rahega", time.Since(start))
		select {}
	}
	logf("browser band kiya gaya, exit")
}

func exePath() string { p, _ := os.Executable(); return p }

// reg query se pata karo ki auto start abhi on hai ya nahi (aur ye usi exe ke liye hai)
func startupEnabled() bool {
	if runtime.GOOS != "windows" {
		b, _ := os.ReadFile(filepath.Join(dataDir, "startup_state"))
		return string(b) == "on"
	}
	cmd := exec.Command("reg", "query", runKey, "/v", runName)
	hideWindow(cmd)
	out, err := cmd.Output()
	return err == nil && strings.Contains(strings.ToLower(string(out)), strings.ToLower(exePath()))
}

func setStartup(on bool) {
	if runtime.GOOS != "windows" {
		v := "off"
		if on {
			v = "on"
		}
		os.WriteFile(filepath.Join(dataDir, "startup_state"), []byte(v), 0o644)
		return
	}
	if on {
		err := runHidden("reg", "add", runKey, "/v", runName, "/t", "REG_SZ", "/d", `"`+exePath()+`"`, "/f")
		logf("startup on: err=%v", err)
	} else {
		err := runHidden("reg", "delete", runKey, "/v", runName, "/f")
		logf("startup off: err=%v", err)
	}
	os.WriteFile(filepath.Join(dataDir, "startup_decided"), []byte("1"), 0o644)
}

func main() {
	lan := flag.Bool("lan", false, "same WiFi ke dusre device (TV browser) bhi board khol sake")
	noBrowser := flag.Bool("no-browser", false, "browser mat kholo (test)")
	startupOn := flag.Bool("startup-on", false, "PC chalu hone par apne aap shuru ho")
	startupOff := flag.Bool("startup-off", false, "apne aap shuru hona band karo")
	flag.Parse()

	base := os.Getenv("LocalAppData")
	if base == "" {
		base, _ = os.UserCacheDir()
	}
	if base == "" {
		base = os.TempDir()
	}
	dataDir = filepath.Join(base, "SSRateBoard")
	os.MkdirAll(dataDir, 0o755)

	if *startupOn || *startupOff {
		setStartup(*startupOn)
		return
	}
	// pehli baar: PC ke saath apne aap shuru hone ka option on (band karne ke liye: --startup-off)
	if runtime.GOOS == "windows" && !existsFile(filepath.Join(dataDir, "startup_decided")) {
		setStartup(true)
	}

	if p := existingPort(); p != 0 {
		logf("pehle se chal raha server mila: port %d", p)
		if !*noBrowser {
			openBrowser(fmt.Sprintf("http://localhost:%d", p))
		}
		return
	}

	upstream := os.Getenv("RATE_UPSTREAM")
	if upstream == "" {
		upstream = defaultUpstream
	}
	go poller(upstream)

	host := "127.0.0.1"
	if *lan {
		host = "0.0.0.0"
	}
	var ln net.Listener
	var err error
	port := 0
	for p := 8000; p <= 8010; p++ {
		ln, err = net.Listen("tcp", fmt.Sprintf("%s:%d", host, p))
		if err == nil {
			port = p
			break
		}
	}
	if ln == nil {
		logf("koi port khali nahi mila: %v", err)
		os.Exit(1)
	}
	logf("server shuru: %s:%d (upstream %s)", host, port, strings.Split(upstream, "?")[0])
	go http.Serve(ln, newMux())

	if *noBrowser {
		fmt.Printf("port %d\n", port)
		select {}
	}
	openBrowser(fmt.Sprintf("http://localhost:%d", port))
}
