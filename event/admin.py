from django.contrib import admin
from event.models import Event, Meeting, EventAttachment
from poll.models import Submitting

class MeetingInline(admin.StackedInline):
    fieldsets = [
        (
            None,
            {'fields': ['title', 'datetime']}
        ),
        (
            'Extra informations',
            {'fields': ['description'], 'classes': ['collapse']}
        )
        ]
    model = Meeting

class EventAttachmentInline(admin.StackedInline):
    model = EventAttachment

class SubmittedPollAdmin(admin.TabularInline):
    model = Submitting

    def get_readonly_fields(self, request, obj=None):
        fields = ['poll', 'user', 'answer']
        return [f.name for f in self.model._meta.fields if f.name in fields]
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs["queryset"] = Submitting.objects.filter(
            event__id=db_field.primary_key
            ).order_by('poll')

        return super(SubmittedPollAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

class EventAdmin(admin.ModelAdmin):
    fields = ['title', 'description']
    list_display = ['title', 'owner']
    inlines = [MeetingInline, EventAttachmentInline, SubmittedPollAdmin]

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super(EventAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(EventAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

admin.site.register(Event, EventAdmin)