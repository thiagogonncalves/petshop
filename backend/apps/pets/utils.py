"""
Utilities for pet card generation
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
from io import BytesIO
from django.conf import settings
import os


def generate_pet_card(pet):
    """
    Generate a PDF pet card - 1/4 of A4 page (foldable layout)
    Card size: 105mm x 148.5mm (half width, half height of A4)
    """
    
    buffer = BytesIO()
    width, height = A4  # A4 = 210mm x 297mm
    
    # Card dimensions: 1/4 of A4 = 105mm x 148.5mm
    card_width = 100*mm  # Slightly smaller to fit margins
    card_height = 140*mm
    
    # Create PDF with canvas for precise positioning
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Calculate position for top-left card (can be folded)
    x_start = 5*mm
    y_start = height - card_height - 5*mm
    
    # Draw card border (orange border matching theme)
    c.setStrokeColor(colors.HexColor('#ea580c'))
    c.setLineWidth(2)
    c.rect(x_start, y_start, card_width, card_height, fill=0, stroke=1)
    
    # Inner padding
    inner_padding = 5*mm
    inner_x = x_start + inner_padding
    inner_y = y_start + card_height - inner_padding
    current_y = inner_y
    
    # Title "Happy Pets"
    c.setFillColor(colors.HexColor('#1e40af'))
    c.setFont("Helvetica-Bold", 16)
    title_width = c.stringWidth('Happy Pets', 'Helvetica-Bold', 16)
    c.drawString(inner_x + (card_width - 2*inner_padding - title_width) / 2, current_y, 'Happy Pets')
    current_y -= 8*mm
    
    # Subtitle
    c.setFillColor(colors.HexColor('#ea580c'))
    c.setFont("Helvetica", 10)
    subtitle = 'Carteirinha do Pet'
    subtitle_width = c.stringWidth(subtitle, 'Helvetica', 10)
    c.drawString(inner_x + (card_width - 2*inner_padding - subtitle_width) / 2, current_y, subtitle)
    current_y -= 12*mm
    
    # Photo (if available)
    if pet.photo:
        try:
            photo_path = os.path.join(settings.MEDIA_ROOT, str(pet.photo))
            if os.path.exists(photo_path):
                img = PILImage.open(photo_path)
                # Resize to fit card (max 30mm)
                max_size = 30*mm
                img_width, img_height = img.size
                aspect = img_width / img_height
                
                if img_width > img_height:
                    display_width = max_size
                    display_height = max_size / aspect
                else:
                    display_height = max_size
                    display_width = max_size * aspect
                
                img_width_px = int(display_width / mm * 2.83465)  # Convert mm to points
                img_height_px = int(display_height / mm * 2.83465)
                
                img = img.resize((img_width_px, img_height_px), PILImage.Resampling.LANCZOS)
                img_reader = ImageReader(img)
                
                img_x = inner_x + (card_width - 2*inner_padding - display_width) / 2
                c.drawImage(img_reader, img_x, current_y - display_height, width=display_width, height=display_height)
                current_y -= display_height + 5*mm
        except Exception:
            pass
    
    # Pet Information
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 8)
    current_y -= 3*mm
    c.drawString(inner_x, current_y, 'INFORMAÇÕES DO PET')
    current_y -= 6*mm
    
    c.setFont("Helvetica", 7)
    info_items = [
        f'Nome: {pet.name}',
        f'Espécie: {pet.get_species_display()}',
        f'Raça: {pet.breed or "N/I"}',
        f'Idade: {f"{pet.age} anos" if pet.age else "N/I"}',
        f'Sexo: {pet.get_sex_display()}',
        f'Cor: {pet.color or "N/I"}',
    ]
    
    for item in info_items:
        # Wrap text if too long
        max_width = card_width - 2*inner_padding
        if c.stringWidth(item, 'Helvetica', 7) > max_width:
            words = item.split(': ')
            if len(words) == 2:
                label = words[0] + ':'
                value = words[1]
                c.drawString(inner_x, current_y, label)
                # Try to fit value on next line if needed
                if c.stringWidth(value, 'Helvetica', 7) > max_width - 30:
                    # Truncate
                    value = value[:30] + '...'
                c.drawString(inner_x + 25, current_y - 3*mm, value)
                current_y -= 6*mm
            else:
                c.drawString(inner_x, current_y, item[:35])
                current_y -= 4*mm
        else:
            c.drawString(inner_x, current_y, item)
            current_y -= 4*mm
    
    current_y -= 3*mm
    
    # Client Information
    c.setFont("Helvetica-Bold", 8)
    c.drawString(inner_x, current_y, 'DONO')
    current_y -= 6*mm
    
    c.setFont("Helvetica", 7)
    client_items = [
        f'Nome: {pet.client.name[:25]}' if len(pet.client.name) > 25 else f'Nome: {pet.client.name}',
        f'Tel: {pet.client.phone}',
        f'CPF/CNPJ: {pet.client.document[:20]}' if len(pet.client.document) > 20 else f'CPF/CNPJ: {pet.client.document}',
    ]
    
    for item in client_items:
        if c.stringWidth(item, 'Helvetica', 7) > max_width:
            item = item[:35] + '...'
        c.drawString(inner_x, current_y, item)
        current_y -= 4*mm
    
    # Footer
    current_y -= 3*mm
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 6)
    footer_text = f'Emitido: {pet.created_at.strftime("%d/%m/%Y")}'
    footer_width = c.stringWidth(footer_text, 'Helvetica', 6)
    c.drawString(inner_x + (card_width - 2*inner_padding - footer_width) / 2, current_y, footer_text)
    
    # Save PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
