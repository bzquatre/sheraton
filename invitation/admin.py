from django.contrib import admin ,messages
from .models import  Invitation,Visitor
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'number_of_guests', 'email')
    list_display = ['name', 'number_of_guests', 'email','pdf']
    readonly_fields =('pdf',)
    actions = ['export_selected_to_pdf']
    
    # 1️⃣ Limit visible records to only the current user's invitations
    def get_fields(self, request, obj = ...):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        else:
            return ('name', 'number_of_guests', 'email')
        

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