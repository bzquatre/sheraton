from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client, Invitation,Visitor
from django.urls import reverse
from django.http import HttpResponseRedirect

@admin.register(Client)
class ClientAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'logo','number_of_guests')}),
    )
    list_display = ('username', 'name', 'email', 'is_staff')


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields =('pdf',)
    actions = ['export_selected_to_pdf']
    # 1️⃣ Limit visible records to only the current user's invitations
    def get_fields(self, request, obj = ...):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        else:
            return ('first_name', 'last_name', 'email', 'job')
    def get_list_display(self, request):
        if request.user.is_superuser:
            return('client','first_name', 'last_name', 'email', 'job')
        else:
            return ('first_name', 'last_name', 'email', 'job','pdf')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(client=request.user)

    # 2️⃣ Automatically assign client when creating new
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:  # when creating new
            obj.client = request.user
        obj.save()

    # 3️⃣ Prevent adding more than number_of_guests
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if not hasattr(request.user, 'number_of_guests'):
            return False
        current_count = Invitation.objects.filter(client=request.user).count()
        return current_count < request.user.number_of_guests
    def has_change_permission(self, request, obj = None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # Allow seeing list
        visited = Visitor.objects.filter(guest=obj.id).count()
        return visited == 0
    def has_delete_permission(self, request, obj = None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # Allow seeing list
        visited = Visitor.objects.filter(guest=obj.id).count()
        return visited == 0
    def export_selected_to_pdf(self, request, queryset):
        ids = ",".join(str(obj.id) for obj in queryset)
        url = reverse('invitations_bulk_pdf') + f'?ids={ids}'
        return HttpResponseRedirect(url)

    export_selected_to_pdf.short_description = "🖨 Export selected invitations to one PDF"
    

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display= ('guest','guest_first_name','guest_last_name','guest_client','time')
    def guest_first_name(self, obj):
        return obj.guest.first_name
    guest_first_name.short_description = 'First Name'
    def guest_last_name(self, obj):
        return obj.guest.last_name
    guest_last_name.short_description = 'Last Name'
    def guest_client(self, obj):
        return obj.guest.client.name
    guest_client.short_description = 'Client'