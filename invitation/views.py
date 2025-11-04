from django_tex.shortcuts import render_to_pdf
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from invitation.models import *
# Create your views here.

def invitation_view(request,id):
    invitation = get_object_or_404(Invitation, pk=id)
    context = {
        'invitation': invitation,
    }
    return render_to_pdf(request,'invitation.tex', context, filename=f"invitation_{invitation.code}.pdf")
def invitation_bulk_view(request):
    """
    Generate one PDF containing multiple invitations.
    Example URL: /invitations/bulk/?ids=1,2,3
    """
    ids_str = request.GET.get("ids", "")
    ids = [int(i) for i in ids_str.split(",") if i.isdigit()]

    invitations = Invitation.objects.filter(id__in=ids)

    if not invitations.exists():
        return HttpResponse("No valid invitations selected.", status=400)

    context = {'invitations': invitations}
    return render_to_pdf(request, 'invitation_list.tex', context,
                        filename="invitations_bulk.pdf")
