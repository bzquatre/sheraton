import io, zipfile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Invitation, InvitationItems
from django_tex.shortcuts import render_to_pdf

def invitation_view(request, id):
    # Get the invitation or return 404 if not found
    invitation = get_object_or_404(Invitation, pk=id)
    
    # Get all related invitation items
    invitation_items = InvitationItems.objects.filter(invitation=invitation)
    
    # Create a memory buffer for the ZIP file
    zip_buffer = io.BytesIO()
    
    # Open ZIP file in memory
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Generate one PDF per invitation item
        for item in invitation_items:
            context = {
                'invitation': invitation,
                'item': item,  # single item for this PDF
            }
            # Render the PDF for this item
            pdf = render_to_pdf(request, 'invitation_list.tex', context)
            
            # Create a filename for each PDF (example: "Guest_1.pdf")
            pdf_filename = f"{invitation.name}_{item.id}.pdf"
            
            # Write PDF bytes into ZIP file
            zip_file.writestr(pdf_filename, pdf.content)
    
    # Prepare the response as a downloadable ZIP
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=invitation_{invitation.name}.zip'
    return response
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
