.class public Lcom/shreess/rateboard/Net;
.super Ljava/lang/Object;
.source "Net.java"

# JS bridge "SSNet": WebView ke XHR/fetch rok diye jayein (kuch TV boxes) to feed seedha Android se laata hai.
# Sirf https:// links, background thread par; jawab window.ssNet(status, text) se wapas.

.field private web:Landroid/webkit/WebView;

.method public constructor <init>(Landroid/webkit/WebView;)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/shreess/rateboard/Net;->web:Landroid/webkit/WebView;
    return-void
.end method

.method public get(Ljava/lang/String;)V
    .locals 3
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    if-eqz p1, :cond_end
    const-string v0, "https://"
    invoke-virtual {p1, v0}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_end

    new-instance v0, Lcom/shreess/rateboard/NetRun;
    iget-object v1, p0, Lcom/shreess/rateboard/Net;->web:Landroid/webkit/WebView;
    invoke-direct {v0, v1, p1}, Lcom/shreess/rateboard/NetRun;-><init>(Landroid/webkit/WebView;Ljava/lang/String;)V
    new-instance v2, Ljava/lang/Thread;
    invoke-direct {v2, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    invoke-virtual {v2}, Ljava/lang/Thread;->start()V

    :cond_end
    return-void
.end method
