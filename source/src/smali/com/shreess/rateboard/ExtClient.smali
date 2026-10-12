.class public Lcom/shreess/rateboard/ExtClient;
.super Landroid/webkit/WebViewClient;
.source "ExtClient.java"

# Local page (file:) WebView me hi khulta hai. Baaki har link (WhatsApp, Instagram, Maps)
# phone ki apni app me khulta hai (Intent.ACTION_VIEW).

.field private ctx:Landroid/content/Context;

.method public constructor <init>(Landroid/content/Context;)V
    .locals 0
    invoke-direct {p0}, Landroid/webkit/WebViewClient;-><init>()V
    iput-object p1, p0, Lcom/shreess/rateboard/ExtClient;->ctx:Landroid/content/Context;
    return-void
.end method

.method public shouldOverrideUrlLoading(Landroid/webkit/WebView;Ljava/lang/String;)Z
    .locals 3

    const-string v0, "file:"
    invoke-virtual {p2, v0}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :cond_ext
    const/4 v0, 0x0
    return v0

    :cond_ext
    :try_start_0
    invoke-static {p2}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;
    move-result-object v2
    new-instance v0, Landroid/content/Intent;
    const-string v1, "android.intent.action.VIEW"
    invoke-direct {v0, v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V
    const/high16 v1, 0x10000000
    invoke-virtual {v0, v1}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;
    iget-object v1, p0, Lcom/shreess/rateboard/ExtClient;->ctx:Landroid/content/Context;
    invoke-virtual {v1, v0}, Landroid/content/Context;->startActivity(Landroid/content/Intent;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    const/4 v0, 0x1
    return v0
.end method
