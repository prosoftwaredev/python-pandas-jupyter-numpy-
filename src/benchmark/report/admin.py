from django.contrib import admin

from benchmark.report.models import ReportUpload, ReportRelease, ReportPeriod


@admin.register(ReportUpload)
class ReportUploadAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'created',
    )
    list_display = (
        'id',
        'name',
        'description',
        'period',
        'file',
        'created'
    )
    readonly_fields = (
        'id',
    )


@admin.register(ReportRelease)
class ReportReleaseAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'created',
    )
    list_display = (
        'id',
        'report',
        'created'
    )
    readonly_fields = (
        'id',
    )
    list_select_related = (
        'report',
    )


@admin.register(ReportPeriod)
class ReportPeriodAdmin(admin.ModelAdmin):
    ist_display = (
        'id',
        'name',
        'start',
        'end'
    )
