import os
import shutil

from pypdf import PdfReader 

from ..util.debug import dprint
from .config import app


class HTMLBuilder():

    def __init__(self, deb_dir, report_dir):
        self.deb_dir = deb_dir
        self.report_dir = report_dir
        self.replacements = {}

    def _build_figures(self):
        figures_dir = os.path.join(self.report_dir, 'figures')
        shutil.copytree(os.path.join(self.deb_dir, 'figures'), figures_dir)

        pdfs = [
            ('clusteredtraitmatrix', 'kinetic_plot.pdf', 'Substrate Kinetic Traits'),
            ('traitvariance_acrossgenomes', 'phenotype_plot.pdf', 'Batch Phenotypic Traits'),
            ('guild2traitprofile', 'mixed_plot.pdf', 'Mixed Medium'),
            ('guildsizedist', 'competition_plot.pdf', 'Competition'),
        ]
        display_first = 'clusteredtraitmatrix'

        button_l = []
        content_l = []
        for i, pdf in enumerate(pdfs):
            id, fn, title = pdf

            if fn not in os.listdir(figures_dir): continue
            try:
                # simple check of pdf file validity, is fn a pdf
                # switched from PyPDF2:PdfFileReader to PdfReader
                PdfReader(os.path.join(figures_dir, fn))
            except:
                continue

            button_l.append(
                '''<button class="tablinks %s" onclick="openTab(event, '%s')">%s</button>'''
                % (
                    'active' if id == display_first else '',
                    id,
                    title,
                )
            )

            content_l.append(
                '<div id="%s" class="tabcontent" %s>\n' % (
                    id,
                    ('style="display:inline-flex;"' if id == display_first else ''),
                ) +
                f'<embed src="figures/{fn}" width="100%" height="100%">'
                '</div>\n'
            )

        self.replacements['BUTTONS_TAG'] = '\n'.join(button_l)
        self.replacements['CONTENT_TAG'] = '\n'.join(content_l)

    def write(self):
        self._build_figures()

        REPORT_HTML_TEMPLATE_FLPTH = '/kb/module/lib/debmicrotrait/template/report_deb.html'
        html_fp = os.path.join(app.report_dir, 'report_deb.html')

        with open(REPORT_HTML_TEMPLATE_FLPTH, 'r') as src_fh:
            with open(html_fp, 'w') as dst_fh:
                for line in src_fh:
                    s = line.strip()
                    if s in self.replacements:
                        dst_fh.write(self.replacements[s].strip() + '\n')
                    else:
                        dst_fh.write(line)

        return html_fp
