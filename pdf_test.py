import os
import reportlab
from reportlab.pdfgen import canvas
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/learning/lib/reportlabs/fonts')

# reportlab.rl_config.TTFSearchPath.append(str(BASE_DIR))

# need to copy font file to /"v_env"/lib/python3.12/site-packages/reportlab/fonts
pdfmetrics.registerFont(TTFont('samim', 'samim.ttf'))

c = canvas.Canvas("hello_again.pdf", pagesize=(595.27, 841.89))
c.setFont('samim', 14)
c.drawString(50, 780, ". سلام سلام دوباره")
c.showPage()
c.save()
