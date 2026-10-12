.class public Lcom/shreess/rateboard/PollJob;
.super Landroid/app/job/JobService;
.source "PollJob.java"

# Har ~15 minute me background me chalta hai, config.json me nayi notification dekhta hai.

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Landroid/app/job/JobService;-><init>()V
    return-void
.end method

.method public onStartJob(Landroid/app/job/JobParameters;)Z
    .locals 2
    new-instance v0, Lcom/shreess/rateboard/PollRun;
    invoke-direct {v0, p0, p1}, Lcom/shreess/rateboard/PollRun;-><init>(Landroid/app/job/JobService;Landroid/app/job/JobParameters;)V
    new-instance v1, Ljava/lang/Thread;
    invoke-direct {v1, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V
    const/4 v0, 0x1
    return v0
.end method

.method public onStopJob(Landroid/app/job/JobParameters;)Z
    .locals 1
    const/4 v0, 0x0
    return v0
.end method
