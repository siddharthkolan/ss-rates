.class public Lcom/shreess/rateboard/Tv;
.super Ljava/lang/Object;
.source "Tv.java"

# TV / TV box / stick hai ya nahi: leanback, television, touchscreen nahi, ya screen chaudi (width > height)

.method public static isTv(Landroid/content/Context;)Z
    .locals 6

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
    if-nez v2, :cond_yes
    const-string v1, "android.hardware.touchscreen"
    invoke-virtual {v0, v1}, Landroid/content/pm/PackageManager;->hasSystemFeature(Ljava/lang/String;)Z
    move-result v2
    if-eqz v2, :cond_yes_notouch

    # touchscreen hai: real display size check (x > y => chaudi screen)
    const-string v1, "window"
    invoke-virtual {p0, v1}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v3
    check-cast v3, Landroid/view/WindowManager;
    invoke-interface {v3}, Landroid/view/WindowManager;->getDefaultDisplay()Landroid/view/Display;
    move-result-object v3
    new-instance v4, Landroid/graphics/Point;
    invoke-direct {v4}, Landroid/graphics/Point;-><init>()V
    invoke-virtual {v3, v4}, Landroid/view/Display;->getRealSize(Landroid/graphics/Point;)V
    iget v1, v4, Landroid/graphics/Point;->x:I
    iget v5, v4, Landroid/graphics/Point;->y:I
    # 7 inch+ tablet portrait me bhi tall hota hai; sirf x > y*1.3 ko TV mano
    mul-int/lit8 v5, v5, 0x4
    mul-int/lit8 v1, v1, 0x3
    if-le v1, v5, :cond_no
    const/4 v2, 0x1
    return v2

    :cond_no
    const/4 v2, 0x0
    return v2

    :cond_yes_notouch
    const/4 v2, 0x1
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :cond_yes
    return v2

    :catch_0
    const/4 v2, 0x0
    return v2
.end method
