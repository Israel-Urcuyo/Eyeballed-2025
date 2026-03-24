import pytesseract
from PIL import Image
from PyPDF2 import PdfWriter
import openai

# API Keys
openai.organization = "org-qeuLnmOrc8uBn9rfTJcAgDHV"
openai.api_key = "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"
openai.Model.list()

# Load input image
image_path = 'untitled.png'
image = Image.opken('/Users/homefolder/Downloads/Untitled.png')

# Extract text
text = pytesseract.image_to_string(image)

# New PDF
output_pdf_path = 'output.pdf'
pdf_writer = PdfWriter()

# Extracted Text becomes PDF content
pdf_writer.add_blank_page(595, 842)  # A4 size: 8.27 x 11.69 inches or approximately 595 x 842 pixels

# Save PDF file
with open(output_pdf_path, 'wb') as output_pdf:
    pdf_writer.write(output_pdf)

# Generate text using ChatGPT
generated_text = openai.Completion.create(
    engine='text-davinci-003',  # GPT model
    prompt=text,  # Extracted Text as prompt
    max_tokens=100,
    n=1,
    temperature=0.7
).choices[0].text.strip()

# Add the generated text to the PDF as content
pdf_writer.add_blank_page(595, 842)  # A4 size: 8.27 x 11.69 inches or approximately 595 x 842 pixels

# Save the modified PDF file
with open(output_pdf_path, 'wb') as output_pdf:
    pdf_writer.write(output_pdf)

print("PDF created successfully.")