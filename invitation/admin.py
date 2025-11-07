from django.contrib import admin ,messages
from .models import  *
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from urllib.parse import unquote

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'email')
    list_display = ['name', 'number_of_guests','nombre_visiteurs', 'email','pdf','zip']
    readonly_fields =('pdf','zip')
    
    # 1️⃣ Limit visible records to only the current user's invitations
    def get_fields(self, request, obj = ...):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        else:
            return ('name','logo', 'number_of_guests', 'email')

        
    

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    fields = ['guest']
    list_display= ('guest','guest_name','time','user')
    search_fields = ['guest__code','guest__invitation__name','pk']
    search_help_text = "Scan a QR code to check and log the visitor."
    class Media:
        js = ('js/clear_search.js',)
    def has_change_permission(self, request, obj = ...):
        return False
    def get_search_results(self, request, queryset, search_term):
        search_term = unquote(search_term.strip())
        if search_term.startswith('https://sheratonevents.pythonanywhere.com/'):
            search_term = search_term.split('/')[-2]
            if not InvitationItems.objects.filter(code__iexact=search_term).exists():
                self.message_user(
                    request,
                    f"❌ '{search_term}' Cette carte d’invitation n’existe pas.",
                    messages.ERROR
                )
                return super().get_search_results(request, queryset, search_term)
            # Try to find an exact QR code match
            elif Visitor.objects.filter(guest__code__iexact=search_term).first():
                self.message_user(
                                request,
                                f"⚠️ '{search_term}'  Cette invitation a déjà scannée.",
                                messages.WARNING
                            )
                return super().get_search_results(request, queryset, search_term)
            else :
                    match = InvitationItems.objects.filter(code__iexact=search_term).first()
                    visitor=Visitor.objects.create(guest=match,user=request.user)

                    # Show success message in Django admin
                    self.message_user(
                        request,
                        f"✅  {match}  Cette invitation a été scannée et enregistrée avec succès.",
                        messages.SUCCESS
                    )
                    return super().get_search_results(request, queryset, visitor.pk)
        else:
            return  super().get_search_results(request, queryset, search_term)
    def has_change_permission(self, request, obj = ...):
        return False
        
    def save_model(self, request, obj, form, change):
        obj.user =request.user
        return super().save_model(request, obj, form, change)
        
    def guest_name(self, obj):
        return obj.guest.invitation.name
    guest_name.short_description = 'name'