from django_tex.shortcuts import render_to_pdf
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from invitation.models import *
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

def invitation_view(request,id):
    invitation = get_object_or_404(Invitation, pk=id)
    invitation_item =InvitationItems.objects.filter(invitation=invitation).all()
    context = {
        'invitation': invitation,
        'invitation_item':invitation_item,
    }
    return render_to_pdf(request,'invitation_list.tex', context, filename=f"invitation_{invitation.name}.pdf")
def invitation_bulk_view(request):
    """
    Generate one PDF containing multiple invitations.
    Example URL: /invitations/bulk/?ids=1,2,3
    """
    ids_str = request.GET.get("ids", "")
    ids = [i for i in ids_str.split(",")]

    invitations = Invitation.objects.filter(id__in=ids)

    if not invitations.exists():
        return HttpResponse("No valid invitations selected.", status=400)

    context = {'invitations': invitations}
    return render_to_pdf(request, 'invitation_list.tex', context,
                        filename="invitations_bulk.pdf")
