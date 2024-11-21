from spire.pdf.common import *
from spire.pdf import *

# Create a PdfDocument object
doc = PdfDocument()

# Load a PDF file
doc.LoadFromFile("C:\\Users\\4madh\\Desktop\\Streamlit\\testpdf.pdf")

# Specify the path of the pfx certificate
pfxCertificatePath = "C:\\Users\\Administrator\\Desktop\\MyCertificate.pfx"

# Specify the password of the pdf certificate
pfxPassword = "08100601"

# Create a signature maker
signatureMaker = PdfOrdinarySignatureMaker(doc, pfxCertificatePath , pfxPassword)

# Get the signature
signature = signatureMaker.Signature

# Create a signature appearance
appearance = PdfSignatureAppearance(signature)

# Load an image
image = PdfImage.FromFile("C:\\Users\\Administrator\\Desktop\\signature.png")

# Set the image as the signature image
appearance.SignatureImage = image

# Set the graphic mode as SignImageOnly
appearance.GraphicMode = GraphicMode.SignImageOnly

# Get the last page
page = doc.Pages[doc.Pages.Count - 1]

# Add the signature to a specified location of the page
signatureMaker.MakeSignature("Signature by Alexander", page, 54.0, page.Size.Height - 100.0, (float)(image.Width), (float)(image.Height), appearance)

# Save the signed document
doc.SaveToFile("SignWithImage.pdf")

# Dispose resources
doc.Dispose()