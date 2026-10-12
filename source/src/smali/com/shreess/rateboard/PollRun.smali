.class public Lcom/shreess/rateboard/PollRun;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;
.source "PollRun.java"

.field private svc:Landroid/app/job/JobService;
.field private prm:Landroid/app/job/JobParameters;

.method public constructor <init>(Landroid/app/job/JobService;Landroid/app/job/JobParameters;)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/shreess/rateboard/PollRun;->svc:Landroid/app/job/JobService;
    iput-object p2, p0, Lcom/shreess/rateboard/PollRun;->prm:Landroid/app/job/JobParameters;
    return-void
.end method

.method public run()V
    .locals 3
    :try_start_0
    iget-object v0, p0, Lcom/shreess/rateboard/PollRun;->svc:Landroid/app/job/JobService;
    invoke-static {v0}, Lcom/shreess/rateboard/Notifier;->check(Landroid/content/Context;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    iget-object v0, p0, Lcom/shreess/rateboard/PollRun;->svc:Landroid/app/job/JobService;
    iget-object v1, p0, Lcom/shreess/rateboard/PollRun;->prm:Landroid/app/job/JobParameters;
    const/4 v2, 0x0
    invoke-virtual {v0, v1, v2}, Landroid/app/job/JobService;->jobFinished(Landroid/app/job/JobParameters;Z)V
    return-void
.end method
