from ebaysdk.finding import Connection as finding
from bs4 import BeautifulSoup
from Book import Book
from Token import Token
import time
from app import Search
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from IDAPP import ID_APP
from BannedSellers import BannedSellers

class Scraper:

    from_mail = 'ebayalert123@gmail.com'
    password_mail = 'sfoxktdmsbauccqa'
    # to_mail = 'sethbaker51@gmail.com'
    to_mail = 'gracia9828@gmail.com'

    def __init__(self):
        self.urls_sent = set()
        self.Token = Token()
        self.banned_sellers = '|'.join(BannedSellers)

    def check_books(self, book_id, max_price):
        # items = soup.find_all('item')
        # books = []
        # for item in items:
        #     book = Book(book_id, max_price, price, shipping_service_cost, title, url, book_xml)
        #     books.append(book)
        
        base_url = 'https://api.ebay.com/buy/browse/v1/item_summary/search?'
        filter_url = 'q=' + book_id + '&filter=price:[..' + max_price + '],priceCurrency:USD,excludeSellers:{' + self.banned_sellers + '}'
        complete_url = base_url + filter_url

        headers = {
            'Authorization': 'Bearer ' + self.Token.get_token()
        }

        response = requests.get(url=complete_url, headers=headers)

        print(response.json())

        return books

    def run(self):
        while True:
            rows = Search.Search.query.all()
            for row in rows:
                books = self.check_books(row.book_id, row.max_price)
                for book in books:
                    self.send_email(book)

    def send_email(self, book):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.from_mail, self.password_mail)

        msg = MIMEMultipart('mixed')
        msg['Subject'] = 'Book Alert'
        msg['From'] = self.from_mail
        msg['To'] = self.to_mail

        if book.url not in self.urls_sent:
            self.urls_sent.add(book.url)           
            html_mail = self.email_html(book)
            text_xml = book.book_xml.prettify()
            msg.attach(MIMEText(html_mail, 'html'))
            msg.attach(MIMEText(text_xml, 'plain')) 
            server.sendmail(self.from_mail, self.to_mail, msg.as_string())
            print('url: ' + book.url)

        server.quit()

    def email_html(self, book):
        html_mail = """\
        <html>
        <head>
            <style>
                table,
                th,
                td {
                    padding: 10px;
                    border: 1px solid black;
                    border-collapse: collapse;
                }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>Book ID</th>
                    <th>Title</th>
                    <th>Max Price</th>
                    <th>Price</th>
                    <th>Shipping Cost</th>
                    <th>URL</th>
                </tr>
                <tr>
                    <th>"""+book.book_id+"""</th>\
                    <th>"""+book.title+ """</th>\
                    <th>"""+str(book.max_price)+"""</th>\
                    <th>"""+str(book.price)+"""</th>\
                    <th>"""+str(book.shipping_service_cost)+"""</th>\
                    <th>"""+book.url+"""</th>\
                </tr>
            </table>
        </body>
        </html>
        """
        return html_mail

    def reset_urls_sent(self):
        self.urls_sent = set()

