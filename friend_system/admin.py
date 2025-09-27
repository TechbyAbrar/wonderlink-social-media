from django.contrib import admin
from .models import Report, Block

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'reported_user', 'reason', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('reporter__email', 'reported_user__email')


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocker', 'blocked_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocker__email', 'blocked_user__email')
