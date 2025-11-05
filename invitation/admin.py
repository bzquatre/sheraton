from django.contrib import admin ,messages
from .models import  Invitation,Visitor
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

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
    list_display= ('guest','name','guest_name','time')
    list_editable = ['name']
    search_fields = ['guest__code','pk']
    search_help_text = "Scan a QR code to check and log the visitor."
    class Media:
        js = ('js/clear_search.js',)
    def get_search_results(self, request, queryset, search_term):
        # Show error message if not found
        if not search_term or search_term=="" :
             return super().get_search_results(request, queryset, search_term)
        elif not Invitation.objects.filter(code__iexact=search_term).exists():
            self.message_user(
                request,
                f"❌ '{search_term}' Cette carte d’invitation n’existe pas.",
                messages.ERROR
            )
            return super().get_search_results(request, queryset, search_term)
        # Try to find an exact QR code match
        else:
            match = Invitation.objects.filter(code__iexact=search_term).first()
            if match:
                try:
                    
                        # Log the scan
                        visitor=Visitor.objects.create(guest=match)

                        # Show success message in Django admin
                        self.message_user(
                            request,
                            f"✅  {match}  Cette invitation a été scannée et enregistrée avec succès.",
                            messages.SUCCESS
                        )
                        return super().get_search_results(request, queryset, visitor.pk)
                except ValidationError :
                        # Handle duplicate scan attempt
                        self.message_user(
                            request,
                            f"⚠️ '{match}'  Cette invitation a déjà atteint le nombre maximum de visiteurs ({match.number_of_guests}).",
                            messages.WARNING
                        )

                        # Return only the matching visitor
                        
                        return super().get_search_results(request, queryset, search_term)

        

        
        
    def guest_name(self, obj):
        return obj.guest.name
    guest_name.short_description = 'name'