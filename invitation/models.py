import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
# ---------------------------
# Custom Client User Model
# ---------------------------
class Client(AbstractUser):
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    name = models.CharField(_("Client Name"), max_length=100)
    logo = models.ImageField(_("Logo"), upload_to='logos/', blank=True, null=True)
    email = models.EmailField(_("Email Address"), unique=True)
    number_of_guests = models.IntegerField(_("Number of Guests"), default=0)

    # Ensure staff status true by default
    is_staff = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name='client_users',
        blank=True,
        help_text='The groups this client belongs to.',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='client_users',
        blank=True,
        help_text='Specific permissions for this client.',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    def save(self, *args, **kwargs):
        # Ensure is_staff is True by default
        if self.is_staff is None:
            self.is_staff = True

        super().save(*args, **kwargs)

        # Automatically add to "clients" group
        try:
            group, created = Group.objects.get_or_create(name="clients")
            self.groups.add(group)
        except Exception:
            # Avoid crash during first migrations
            pass

    def __str__(self):
        return self.name or self.username


# ---------------------------
# invitation Model
# ---------------------------
class Invitation(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invitations')
    first_name = models.CharField(verbose_name="Prénom" ,max_length=100)
    last_name = models.CharField(verbose_name="Nom" ,max_length=100)
    email = models.EmailField()
    job = models.CharField(verbose_name="Fonction" ,max_length=100)
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


    def pdf(self):
        return mark_safe(f'<a target="_blank"  href="/invitation-pdf/{self.id}/"><i class="fa fa-file-pdf"></i></a>')
    
    def __str__(self):
        return f"{self.code}"

class Visitor(models.Model):
    class Meta:
        verbose_name = "Visiteur"
        verbose_name_plural = "Visiteurs"
    guest = models.OneToOneField(Invitation,verbose_name="Invité", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True,verbose_name="Temp")
    