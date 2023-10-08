from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_file_bhejo_pdf(qr_code_file_name, user_id, name=""):
    # Define the color codes
    color_codes = {
        'blue': colors.HexColor('#3498db'),
        'white': colors.HexColor('#ffffff'),
        'pink': colors.HexColor('#B92980'),
        'dark_blue': colors.HexColor('#34495e'),
        'light_gray': colors.HexColor('#f9f9f9')
    }

    # Create a PDF document
    pdf_file = f"static/qr_report/file_bhejo_{user_id}.pdf"
    document = SimpleDocTemplate(pdf_file, pagesize=letter)

    # Define styles
    styles = getSampleStyleSheet()
    heading1_style = ParagraphStyle(name='Heading1', parent=styles['Heading1'], textColor=color_codes['blue'], alignment=1)
    heading2_style = ParagraphStyle(name='Heading2', parent=styles['Heading2'], alignment=1)
    paragraph_style = ParagraphStyle(name='Normal', parent=styles['Normal'], alignment=1)

    # Create story elements
    story = []

    # Logo image
    logo = Image("static/UT_LOGO.jpg", width=1*inch, height=1*inch)
    logo.hAlign = 'CENTER'
    story.append(logo)

    # Heading 1
    heading1 = Paragraph(f"<font color='%s'><b>File Bhejo Id: {user_id}</b></font>" % color_codes['blue'], heading1_style)
    heading1.hAlign = "CENTER"
    story.append(heading1)

    # Heading 2
    heading2 = Paragraph("Quick File Sharing with www.filebhejo.in", heading2_style)
    heading2.hAlign = "CENTER"
    story.append(heading2)

    # A Image in the center
    center_image = Image(qr_code_file_name, width=5*inch, height=5*inch)
    story.append(center_image)

    # Heading 2 (How to Use)
    story.append(heading2)

    # List of instructions
    instructions = [
        "1. Open Any QR scanner (Google lens).",
        "2. Scan the QR Image.",
        "3. Click the Link and Upload."
    ]

    for instruction in instructions:
        instruction_paragraph = Paragraph(instruction, paragraph_style)
        story.append(instruction_paragraph)

    # Copyright and disclaimer
    copyright_text = "<font color='%s'>© 2023 Udian Tower | FileBhejo. All rights reserved. | Free to use. Uploaded files will be automatically deleted after 1 month.</font>" % color_codes['dark_blue']
    copyright = Paragraph(copyright_text, paragraph_style)
    story.append(copyright)

    # Build the PDF document
    document.build(story)

    print(f"PDF '{pdf_file}' created successfully.")
    return pdf_file

# Example usage:
if __name__ == "__main__":
    qr_code_file_name = "static/qrcodes/456_qr.png"
    user_id = 7631256855
    generate_file_bhejo_pdf(qr_code_file_name, user_id)
