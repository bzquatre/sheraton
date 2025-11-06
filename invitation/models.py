import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
# ---------------------------
# invitation Model
# ---------------------------

class Invitation(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    name = models.CharField(_("Client Name"), max_length=100)
    number_of_guests = models.IntegerField(_("Nombre d'invités"), default=0)
    logo = models.ImageField(_("Logo"), upload_to='logos/', blank=True, null=True)
    email = models.EmailField( blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk :
            InvitationItems.objects.filter(invitation=self).delete()
        super().save(*args, **kwargs)
        for _ in range(self.number_of_guests):
            InvitationItems.objects.create(invitation=self)
        
    def  nombre_visiteurs(self):
        return InvitationItems.objects.filter(invitation=self, visitor__isnull=False).count()

    def pdf(self):
        return mark_safe(f'<a target="_blank"  href="/invitation-pdf/{self.id}/"><i class="fa fa-file-pdf"></i></a>')
    def zip(self):
        return mark_safe(f'<a target="_blank"  href="/invitation-zip-pdf/{self.id}/"><i class="fa fa-folder"></i></a>')
   
    def __str__(self):
        return f"{self.name}"

class InvitationItems(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    invitation=models.ForeignKey(Invitation,on_delete=models.CASCADE)
    code = models.CharField(verbose_name="Code" ,max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        # Ensure a unique code is generated
        if not self.code:
            while True:
                new_code = get_random_string(10).upper()
                if not InvitationItems.objects.filter(code=new_code).exists():
                    self.code = new_code
                    break
        super().save(*args, **kwargs)
    def __str__(self):
        return self.code


class Visitor(models.Model):
    class Meta:
        verbose_name = "Visiteur"
        verbose_name_plural = "Visiteurs"
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="Agent", null=True)
    guest = models.OneToOneField(InvitationItems,verbose_name="Invité", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True,verbose_name="Temp")
    
    