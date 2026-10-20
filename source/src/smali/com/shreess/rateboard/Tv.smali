.class public Lcom/shreess/rateboard/Tv;
.super Ljava/lang/Object;
.source "Tv.java"

# TV (Android TV / Fire TV / TV box) hai ya nahi: leanback ya television feature.

.method public static isTv(Landroid/content/Context;)Z
    .locals 3

    :try_start_0
    invoke-virtual {p0}, Landroid/content/Context;->getPackageManager()Landroid/content/pm/PackageManager;
    move-result-object v0
    const-string v1, "android.software.leanback"
    invoke-virtual {v0, v1}, Landroid/content/pm/PackageManager;->hasSystemFeature(Ljava/lang/String;)Z
    move-result v2
    if-nez v2, :cond_yes
    const-string v1, "android.hardware.type.television"
    invoke-virtual {v0, v1}, Landroid/content/pm/PackageManager;->hasSystemFeature(Ljava/lang/String;)Z
    move-result v2
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :cond_yes
    return v2

    :catch_0
    const/4 v2, 0x0
    return v2
.end method
