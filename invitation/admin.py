from django.contrib import admin ,messages
from django.contrib.auth.admin import UserAdmin
from .models import Client, Invitation,Visitor
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError


@admin.register(Client)
class ClientAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('name','logo','number_of_guests')}),
        ("Compte", {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name','email', 'password1', 'password2',  'logo','number_of_guests')}
        ),
    )
    list_display = ('email', 'name','number_of_guests' )
    list_filter = []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs.filter(is_superuser=False)
            if request.user.groups.filter(name="admins").exists():
            # Show only users who belong to group "yyyyyy"
                return qs.filter(groups__name="clients")
        return qs

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
            return('client','first_name', 'last_name', 'email', 'job','pdf')
        else:
            return ('first_name', 'last_name', 'email', 'job','pdf')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name="admins").exists() or request.user.groups.filter(name="agents").exists():
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
    search_fields = ['guest__code']
    search_help_text = "Scan a QR code to check and log the visitor."
    class Media:
        js = ('js/clear_search.js',)
    def get_search_results(self, request, queryset, search_term):
        # Try to find an exact QR code match
        match = Invitation.objects.filter(code__iexact=search_term).first()
        if match:
            try:
                
                    # Log the scan
                    Visitor.objects.create(guest=match)

                    # Show success message in Django admin
                    self.message_user(
                        request,
                        f"✅  {match}  Cette invitation a été scannée et enregistrée avec succès.",
                        messages.SUCCESS
                    )
            except IntegrityError:
                    # Handle duplicate scan attempt
                    self.message_user(
                        request,
                        f"⚠️  '{match}' Cette invitation a déjà été utilisée.",
                        messages.WARNING
                    )

                    # Return only the matching visitor
            return super().get_search_results(request, queryset, search_term)

        # Show error message if not found
        if search_term:
            self.message_user(
                request,
                f"❌ '{search_term}' Cette carte d’invitation n’existe pas.",
                messages.ERROR
            )

        return super().get_search_results(request, queryset, search_term)
    def guest_first_name(self, obj):
        return obj.guest.first_name
    guest_first_name.short_description = 'Prénom'
    def guest_last_name(self, obj):
        return obj.guest.last_name
    guest_last_name.short_description = 'Nom'
    def guest_client(self, obj):
        return obj.guest.client.name
    guest_client.short_description = 'Client'