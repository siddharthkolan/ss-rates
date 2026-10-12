.class public Lcom/shreess/rateboard/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

# Shree SS Jewellers - rate board app.
# Ek full-screen WebView jo assets/index.html (rate board) kholta hai.
# Screen hamesha on rehti hai (FLAG_KEEP_SCREEN_ON), status/navigation bar chhupe rehte hain.

.field private web:Landroid/webkit/WebView;

.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 4

    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    # title bar nahi chahiye (Window.FEATURE_NO_TITLE = 1)
    const/4 v0, 0x1
    invoke-virtual {p0, v0}, Landroid/app/Activity;->requestWindowFeature(I)Z

    # FLAG_KEEP_SCREEN_ON (0x80) | FLAG_FULLSCREEN (0x400)
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v0
    const/16 v1, 0x480
    invoke-virtual {v0, v1}, Landroid/view/Window;->addFlags(I)V

    # WebView
    new-instance v0, Landroid/webkit/WebView;
    invoke-direct {v0, p0}, Landroid/webkit/WebView;-><init>(Landroid/content/Context;)V
    iput-object v0, p0, Lcom/shreess/rateboard/MainActivity;->web:Landroid/webkit/WebView;

    # background cream (0xFFF6F2E9), taaki load hone se pehle safed/kala flash na ho
    const v1, -0x90d17
    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->setBackgroundColor(I)V

    invoke-virtual {v0}, Landroid/webkit/WebView;->getSettings()Landroid/webkit/WebSettings;
    move-result-object v1

    const/4 v2, 0x1
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setJavaScriptEnabled(Z)V
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setDomStorageEnabled(Z)V
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setAllowFileAccess(Z)V

    # local page se bullion server ka feed seedha padhne ke liye (CORS bypass, jaise Cordova apps)
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setAllowFileAccessFromFileURLs(Z)V
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setAllowUniversalAccessFromFileURLs(Z)V

    # awaaz (popup ke sound) bina touch ke bhi chal sake: setMediaPlaybackRequiresUserGesture(false)
    const/4 v3, 0x0
    invoke-virtual {v1, v3}, Landroid/webkit/WebSettings;->setMediaPlaybackRequiresUserGesture(Z)V

    # LOAD_NO_CACHE = 2 (rates kabhi purane cache se na aayein)
    const/4 v2, 0x2
    invoke-virtual {v1, v2}, Landroid/webkit/WebSettings;->setCacheMode(I)V

    new-instance v1, Lcom/shreess/rateboard/ExtClient;
    invoke-direct {v1, p0}, Lcom/shreess/rateboard/ExtClient;-><init>(Landroid/content/Context;)V
    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->setWebViewClient(Landroid/webkit/WebViewClient;)V

    invoke-virtual {p0, v0}, Landroid/app/Activity;->setContentView(Landroid/view/View;)V

    const-string v1, "file:///android_asset/index.html"
    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->loadUrl(Ljava/lang/String;)V

    return-void
.end method

# Focus wapas aate hi system bars dobara chhupa do (immersive sticky):
# LAYOUT_STABLE 0x100 | LAYOUT_HIDE_NAVIGATION 0x200 | LAYOUT_FULLSCREEN 0x400
# | HIDE_NAVIGATION 0x2 | FULLSCREEN 0x4 | IMMERSIVE_STICKY 0x1000  = 0x1706
.method public onWindowFocusChanged(Z)V
    .locals 2

    invoke-super {p0, p1}, Landroid/app/Activity;->onWindowFocusChanged(Z)V

    if-eqz p1, :cond_done

    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v0
    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;
    move-result-object v0
    const/16 v1, 0x1706
    invoke-virtual {v0, v1}, Landroid/view/View;->setSystemUiVisibility(I)V

    :cond_done
    return-void
.end method


# App recents me jaye to WebView ko pause, wapas aaye to resume
.method protected onPause()V
    .locals 1
    invoke-super {p0}, Landroid/app/Activity;->onPause()V
    iget-object v0, p0, Lcom/shreess/rateboard/MainActivity;->web:Landroid/webkit/WebView;
    if-eqz v0, :cond_p
    invoke-virtual {v0}, Landroid/webkit/WebView;->onPause()V
    :cond_p
    return-void
.end method

.method protected onResume()V
    .locals 1
    invoke-super {p0}, Landroid/app/Activity;->onResume()V
    iget-object v0, p0, Lcom/shreess/rateboard/MainActivity;->web:Landroid/webkit/WebView;
    if-eqz v0, :cond_r
    invoke-virtual {v0}, Landroid/webkit/WebView;->onResume()V
    :cond_r
    return-void
.end method
