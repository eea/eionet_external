from __future__ import absolute_import
from StringIO import StringIO
import xlwt
import jinja2
import six
from six.moves import range

def generate_excel(header, rows):
    style = xlwt.XFStyle()
    normalfont = xlwt.Font()
    headerfont = xlwt.Font()
    headerfont.bold = True
    style.font = headerfont

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet 1')
    row = 0
    for col in range(0, len(header)):
        ws.row(row).set_cell_text(col, header[col], style)

    style.font = normalfont
    for item in rows:
        row += 1
        for col in range(0, len(item)):
            if item[col] is None:
                data = ''
            else:
                data = item[col]
            if not isinstance(data, six.text_type):
                data = str(data) 
            ws.row(row).set_cell_text(col, data, style)

    output = StringIO()
    wb.save(output)

    return output.getvalue()

html = """
  <html>
    <head>
      <style type="text/css">
        table{
          border-collapse: collapse;
          border: 1px solid black;
          white-space: nowrap;
          border-spacing: 6px;
        }
        table td, table th {
          border: 1px solid black;
          padding: 2px;
        }
        </style>
    </head>
    <body>
    <h2>{{ rows|length }} results</h2>
    {% if rows %}
      <table>
        <thead>
          <tr>
            {% for name in header %}
              <th>{{ name }}</th>
            {% endfor %}
          </tr>
        </thead>
        <tbody>
          {% for records in rows %}
          <tr>
            {% for record in records %}
              <td>{{ record | urlize if record != None }}</td>
            {% endfor %}
          </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>No records found for this namespace</p>
    {% endif %}
    </body>
  </html>
"""

def generate_html(header, rows):
    template = jinja2.Template(html)
    result = template.render(header=header, rows=rows)
    return result

