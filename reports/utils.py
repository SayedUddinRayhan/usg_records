# utils.py
import openpyxl
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template

def export_to_excel(rows, headers, filename="report"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = filename

    # Add headers
    ws.append(headers)

    # Add data
    for row in rows:
        ws.append(row)

    # Adjust column widths
    for col in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    wb.save(response)
    return response


def export_to_pdf(rows, headers, filename, extra_context=None):
    template = get_template("reports/report_pdf.html")
    context = {"rows": rows, "headers": headers}

    if extra_context:
        context.update(extra_context)

    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response

