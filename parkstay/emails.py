from io import BytesIO

from django.conf import settings

from parkstay import pdf
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.models import Invoice

from ledger.emails.emails import EmailBase

default_campground_email = settings.CAMPGROUNDS_EMAIL
class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'ps/email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'ps/email/base_email.txt'


def send_booking_invoice(booking):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking invoice for {}'.format(booking.campground.name)
    email_obj.html_template = 'ps/email/invoice.html'
    email_obj.txt_template = 'ps/email/invoice.txt'

    email = booking.customer.email

    context = {
        'booking': booking
    }
    filename = 'invoice-{}({}-{}).pdf'.format(booking.campground.name,booking.arrival,booking.departure)
    references = [b.invoice_reference for b in booking.invoices.all()]
    invoice = Invoice.objects.filter(reference__in=references).order_by('-created')[0]
        
    invoice_pdf = create_invoice_pdf_bytes(filename,invoice)

    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    email_obj.send([email], from_address=campground_email, context=context, attachments=[(filename, invoice_pdf, 'application/pdf')])

def send_booking_confirmation(booking,request):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking  REF {} at {},{} is confirmed'.format(booking.confirmation_number,booking.campground.name,booking.campground.park.name)
    email_obj.html_template = 'ps/email/confirmation.html'
    email_obj.txt_template = 'ps/email/confirmation.txt'

    email = booking.customer.email

    cc = None
    bcc = [default_campground_email]

    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    if campground_email != default_campground_email:
        cc = [campground_email]

    my_bookings_url = request.build_absolute_uri('/mybookings/')
    booking_availability = request.build_absolute_uri('/availability/?site_id={}'.format(booking.campground.id))
    unpaid_vehicle = False

    for v in booking.vehicle_payment_status:
        if v.get('Paid') == 'No':
            unpaid_vehicle = True
            break

    context = {
        'booking': booking,
        'campground_email': campground_email,
        'my_bookings': my_bookings_url,
        'availability': booking_availability,
        'unpaid_vehicle': unpaid_vehicle
    }

    att = BytesIO()
    pdf.create_confirmation(att, booking)
    att.seek(0)


    email_obj.send([email], from_address=campground_email, context=context, cc=cc, bcc=bcc attachments=[('confirmation-PS{}.pdf'.format(booking.id), att.read(), 'application/pdf')])
    booking.confirmation_sent = True
    booking.save()

def send_booking_cancelation(booking,request):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Canceled:your booking REF {} at {},{}.'.format(booking.confirmation_number,booking.campground.name,booking.campground.park.name)
    email_obj.html_template = 'ps/email/cancel.html'
    email_obj.txt_template = 'ps/email/cancel.txt'

    email = booking.customer.email

    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    my_bookings_url = request.build_absolute_uri('/mybookings/')
    context = {
        'booking': booking,
        'my_bookings': my_bookings_url,
        'campground_email': campground_email
    }

    email_obj.send([email], from_address=campground_email, context=context)

def send_booking_lapse(booking):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking for {} has expired'.format(booking.campground.name)
    email_obj.html_template = 'ps/email/lapse.html'
    email_obj.txt_template = 'ps/email/lapse.txt'

    email = booking.customer.email

    context = {
        'booking': booking,
        'settings': settings,
    }
    email_obj.send([email], from_address=camground_email, context=context)

