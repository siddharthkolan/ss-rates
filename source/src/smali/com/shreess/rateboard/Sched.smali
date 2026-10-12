.class public Lcom/shreess/rateboard/Sched;
.super Ljava/lang/Object;
.source "Sched.java"

# App khulte hi: background check job schedule karo (agar pehle se nahi hai) aur
# Android 13+ par notification ki permission maango. Koi bhi galti app ko crash nahi karti.

.method public static go(Landroid/app/Activity;)V
    .locals 8

    :try_start_0
    const-string v0, "jobscheduler"
    invoke-virtual {p0, v0}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/app/job/JobScheduler;
    const/16 v1, 0x3e9
    invoke-virtual {v0, v1}, Landroid/app/job/JobScheduler;->getPendingJob(I)Landroid/app/job/JobInfo;
    move-result-object v2
    if-nez v2, :cond_perm
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :try_start_1
    new-instance v2, Landroid/content/ComponentName;
    const-class v3, Lcom/shreess/rateboard/PollJob;
    invoke-direct {v2, p0, v3}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    new-instance v3, Landroid/app/job/JobInfo$Builder;
    invoke-direct {v3, v1, v2}, Landroid/app/job/JobInfo$Builder;-><init>(ILandroid/content/ComponentName;)V
    const-wide/32 v4, 0xdbba0
    invoke-virtual {v3, v4, v5}, Landroid/app/job/JobInfo$Builder;->setPeriodic(J)Landroid/app/job/JobInfo$Builder;
    const/4 v4, 0x1
    invoke-virtual {v3, v4}, Landroid/app/job/JobInfo$Builder;->setPersisted(Z)Landroid/app/job/JobInfo$Builder;
    invoke-virtual {v3, v4}, Landroid/app/job/JobInfo$Builder;->setRequiredNetworkType(I)Landroid/app/job/JobInfo$Builder;
    invoke-virtual {v3}, Landroid/app/job/JobInfo$Builder;->build()Landroid/app/job/JobInfo;
    move-result-object v3
    invoke-virtual {v0, v3}, Landroid/app/job/JobScheduler;->schedule(Landroid/app/job/JobInfo;)I
    :try_end_1
    .catch Ljava/lang/Throwable; {:try_start_1 .. :try_end_1} :catch_0

    :cond_perm
    :try_start_2
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I
    const/16 v1, 0x21
    if-lt v0, v1, :cond_done
    const/4 v1, 0x1
    new-array v2, v1, [Ljava/lang/String;
    const/4 v3, 0x0
    const-string v4, "android.permission.POST_NOTIFICATIONS"
    aput-object v4, v2, v3
    invoke-virtual {p0, v2, v1}, Landroid/app/Activity;->requestPermissions([Ljava/lang/String;I)V
    :try_end_2
    .catch Ljava/lang/Throwable; {:try_start_2 .. :try_end_2} :catch_0

    :cond_done
    :catch_0
    return-void
.end method
