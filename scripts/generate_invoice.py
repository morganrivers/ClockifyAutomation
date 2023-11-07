import json
import pdfkit

JSON_PARAMETERS_LOCATION = "../data/invoice_params.json"

params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))

invoice_number = dict(params.items())["invoice_number"]
hourly_rate = dict(params.items())["hourly_rate"]
total_hours = dict(params.items())["total_hours"]
month_for_invoice = dict(params.items())["month_for_invoice"]
current_month = dict(params.items())["current_month"]
current_day = dict(params.items())["current_day"]
current_year = dict(params.items())["current_year"]
due_month = dict(params.items())["due_month"]
due_day = dict(params.items())["due_day"]
due_year = dict(params.items())["due_year"]
payment_method = dict(params.items())["payment_method"]
bill_to_address = dict(params.items())["bill_to_address"]
ship_to_address = dict(params.items())["ship_to_address"]

invoice_number_int = int(invoice_number)
total_hours_float = float(total_hours)
hourly_rate_float = float(hourly_rate)

created = current_month + " " + current_day + ", " + current_year
due = due_month + " " + due_day + ", " + due_year
month_title = month_for_invoice.upper()
multiplied_total_float = total_hours_float * hourly_rate_float
multiplied_total = str(total_hours_float * hourly_rate_float)
overall_total = multiplied_total


output = (
    """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>A simple, clean, and responsive HTML invoice template</title>

        <style>
            @page { size: auto;  margin: 0mm; }
            .invoice-box {
                max-width: 800px;
                margin: auto;
                padding: 30px;
                border: 1px solid #eee;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
                font-size: 16px;
                line-height: 24px;
                font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
                color: #555;
            }

            .invoice-box table {
                width: 100%;
                line-height: inherit;
                text-align: left;
            }

            .invoice-box table td {
                padding: 5px;
                vertical-align: top;
            }

            .invoice-box table tr td:nth-child(2) {
                text-align: right;
            }

            .invoice-box table tr.top table td {
                padding-bottom: 20px;
            }

            .invoice-box table tr.top table td.title {
                font-size: 45px;
                line-height: 45px;
                color: #333;
            }

            .invoice-box table tr.information table td {
                padding-bottom: 40px;
            }

            .invoice-box table tr.heading td {
                background: #eee;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }

            .invoice-box table tr.details td {
                padding-bottom: 20px;
            }

            .invoice-box table tr.item td {
                border-bottom: 1px solid #eee;
            }

            .invoice-box table tr.item.last td {
                border-bottom: none;
            }

            .invoice-box table tr.total td:nth-child(2) {
                border-top: none;
                font-weight: bold;
            }

            @media only screen and (max-width: 600px) {
                .invoice-box table tr.top table td {
                    width: 100%;
                    display: block;
                    text-align: center;
                }

                .invoice-box table tr.information table td {
                    width: 100%;
                    display: block;
                    text-align: center;
                }
            }

            /** RTL **/
            .invoice-box.rtl {
                direction: rtl;
                font-family: Tahoma, 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
            }

            .invoice-box.rtl table {
                text-align: right;
            }

            .invoice-box.rtl table tr td:nth-child(2) {
                text-align: left;
            }
        </style>
    </head>

    <body>
        <div class="invoice-box">
            <table cellpadding="0" cellspacing="0">
                <tr class="top">
                    <td colspan="5">
                        <table>
                            <tr>
                                <td class="title">
                                    """
    + month_title
    + """ INVOICE
                                </td>

                                <td>
                                    <strong>Invoice #:</strong> """
    + invoice_number
    + """<br />
                                    <strong>Created:</strong> """
    + created
    + """<br />
                                    <strong>Due:</strong> """
    + due
    + """
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <tr class="information">
                    <td colspan="5">
                        <table>
                            <tr>
                                <td>
                                    <strong>Bill To:</strong><br />
                                    """
    + bill_to_address
    + """
                                </td>

                                <td>
                                    <strong>Ship To:</strong><br />
                                    """
    + ship_to_address
    + """
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <tr class="heading">
                    <td>Payment Method</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>

                <tr class="details">
                    <td>"""
    + payment_method
    + """</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>

                <tr class="heading">
                    <td>Item</td>
                    <td></td>
                    <td>Quantity</td>
                    <td>Rate</td>
                    <td>Amount</td>
                </tr>

                <tr class="item last">
                    <td>Research Associate Compensation, month of """
    + month_for_invoice
    + """, """
    + current_year
    + """</td>
                    <td></td>
                    <td>"""
    + total_hours
    + """ hours</td>
                    <td>$"""
    + hourly_rate
    + """</td>
                    <td>$"""
    + multiplied_total
    + """</td>
                </tr>

                <tr class="total">
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>

                    <td><strong>Total:</strong> $"""
    + overall_total
    + """</td>
                </tr>
            </table>
        </div>
    </body>
</html>"""
)

html_filename = "../data/Invoice_" + invoice_number + ".html"
pdf_filename = "../data/Invoice_" + invoice_number + ".pdf"

f = open(html_filename, "w")
f.write(output)
f.close()

# convert to pdf
pdfkit.from_file(html_filename, pdf_filename)
