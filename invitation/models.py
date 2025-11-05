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
    email = models.EmailField()
    code = models.CharField(verbose_name="Code" ,max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        # Ensure a unique code is generated
        if not self.code:
            while True:
                new_code = get_random_string(10).upper()
                if not Invitation.objects.filter(code=new_code).exists():
                    self.code = new_code
                    break
        super().save(*args, **kwargs)
    def  nombre_visiteurs(self):
        return self.visitor_set.count()

    def pdf(self):
        return mark_safe(f'<a target="_blank"  href="/invitation-pdf/{self.id}/"><i class="fa fa-file-pdf"></i></a>')
    
    def __str__(self):
        return f"{self.code}"

class Visitor(models.Model):
    class Meta:
        verbose_name = "Visiteur"
        verbose_name_plural = "Visiteurs"
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="Agent", null=True)
    guest = models.ForeignKey(Invitation,verbose_name="Invité", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True,verbose_name="Temp")
    def clean(self):
        # Count how many visitors are already linked
        if self.guest.visitor_set.count() >= self.guest.number_of_guests:
            raise ValidationError(f"This invitation already has the maximum number of visitors ({self.guest.number_of_guests}).")

    def save(self, *args, **kwargs):
        self.clean()  # validate before saving
        super().save(*args, **kwargs)
    