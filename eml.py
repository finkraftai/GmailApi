import io
import smtplib
import email.generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Create the container email message
msg = MIMEMultipart()
msg['From'] = 'sudhakar.a_cse2019@svec.edu.in'
msg['To'] = 'yatra.gst@yatra.com'
msg['Subject'] = 'Subject of the Email'

# Email body
body = "This is the body of the email."
msg.attach(MIMEText(body, 'plain'))

# File attachment (PDF)
filename_pdf = r"C:\Users\annav\Downloads\Tutorial_EDIT.pdf"  # Path to the PDF file you want to attach
with open(filename_pdf, 'rb') as attachment:
    part_pdf = MIMEBase('application', 'octet-stream')
    part_pdf.set_payload(attachment.read())
    encoders.encode_base64(part_pdf)
    part_pdf.add_header(
        'Content-Disposition',
        f'attachment; filename={filename_pdf}',
    )
    msg.attach(part_pdf)

# Generate the .eml file content
eml_bytes = io.BytesIO()
gen = email.generator.BytesGenerator(eml_bytes)
gen.flatten(msg)

# Create a new email message with the generated .eml file as an attachment
msg_with_eml_attachment = MIMEMultipart()
msg_with_eml_attachment['From'] = 'sudhakar.a_cse2019@svec.edu.in'
msg_with_eml_attachment['To'] = 'yatra.gst@yatra.com'
msg_with_eml_attachment['Subject'] = 'Email with .eml attachment'

# Attach the generated .eml file as a MIME attachment
eml_attachment = MIMEBase('message', 'rfc822')
eml_attachment.set_payload(eml_bytes.getvalue())
encoders.encode_base64(eml_attachment)
eml_attachment.add_header(
    'Content-Disposition',
    'attachment',
    filename='email.eml'
)
msg_with_eml_attachment.attach(eml_attachment)

# Connect to SMTP server and send the email
with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login('sudhakar.a_cse2019@svec.edu.in', '9573745244')
    server.sendmail('sudhakar.a_cse2019@svec.edu.in', 'yatra.gst@yatra.com', msg_with_eml_attachment.as_string())
