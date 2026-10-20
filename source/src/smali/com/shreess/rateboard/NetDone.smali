.class public Lcom/shreess/rateboard/NetDone;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;
.source "NetDone.java"

.field private web:Landroid/webkit/WebView;
.field private js:Ljava/lang/String;

.method public constructor <init>(Landroid/webkit/WebView;Ljava/lang/String;)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/shreess/rateboard/NetDone;->web:Landroid/webkit/WebView;
    iput-object p2, p0, Lcom/shreess/rateboard/NetDone;->js:Ljava/lang/String;
    return-void
.end method

.method public run()V
    .locals 3
    :try_start_0
    iget-object v0, p0, Lcom/shreess/rateboard/NetDone;->web:Landroid/webkit/WebView;
    iget-object v1, p0, Lcom/shreess/rateboard/NetDone;->js:Ljava/lang/String;
    const/4 v2, 0x0
    invoke-virtual {v0, v1, v2}, Landroid/webkit/WebView;->evaluateJavascript(Ljava/lang/String;Landroid/webkit/ValueCallback;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    return-void
.end method
