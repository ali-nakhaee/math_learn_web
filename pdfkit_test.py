import pdfkit
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

settings.configure()

# pdfkit.from_url('http://google.com', 'out.pdf')
template = get_template("learning/add_practice.html")
context = Context({})
html = template.render(context)
pdfkit.from_string(html, 'out.pdf')