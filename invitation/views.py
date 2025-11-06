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
    
    context = {
        'invitation': invitation,
        'items': invitation_items,  # single item for this PDF
    }
    # Render the PDF for this item
    return  render_to_pdf(request, 'invitation.tex', context,filename=f"{invitation.name}")

def invitation_view_confirmation(request, code):
    # Get the invitation or return 404 if not found
    invitation_item = get_object_or_404(InvitationItems, code=code)
    
    # Get all related invitation items
    invitation = Invitation.objects.filter(id=invitation_item.invitation_id).first()
    
    context = {
        'invitation': invitation,
        'item': invitation_item,  # single item for this PDF
    }
    # Render the PDF for this item
    return  render_to_pdf(request, 'invitation_confermation.tex', context,filename=f"{invitation.name}")


    
def invitation_zip_view(request, id):
    # Get the invitation or return 404 if not found
    invitation = get_object_or_404(Invitation, pk=id)
    
    # Get all related invitation items
    invitation_items = InvitationItems.objects.filter(invitation=invitation)
    
    # Create a memory buffer for the ZIP file
    zip_buffer = io.BytesIO()
    
    # Open ZIP file in memory
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Generate one PDF per invitation item
        for i,item in enumerate(invitation_items):
            context = {
                'invitation': invitation,
                'item': item,  # single item for this PDF
            }
            # Render the PDF for this item
            pdf = render_to_pdf(request, 'invitation_list.tex', context)
            
            # Create a filename for each PDF (example: "Guest_1.pdf")
            pdf_filename = f"{invitation.name}_invitation_{i}.pdf"
            
            # Write PDF bytes into ZIP file
            zip_file.writestr(pdf_filename, pdf.content)
    
    # Prepare the response as a downloadable ZIP
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=invitation_{invitation.name}.zip'
    return response