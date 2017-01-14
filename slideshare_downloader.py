import requests
import sys
import re
import threading
import queue
import img2pdf
from bs4 import BeautifulSoup
from io import BytesIO
from PyPDF2 import PdfFileMerger


q = queue.Queue()
slide_list = {}
url_list = []
done_list = []
pool_size = 5


class ThreadUrl(threading.Thread):
    """Threaded Image Grab"""

    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q

    def run(self):
        while True:
            slide_dict = self.q.get()
            slide_number = slide_dict['number']
            slide_url = slide_dict['url']

            slide_name = re.compile(r'(\w*-)*(\w*)[.](jpg|png)')\
                        .search(slide_url).group()
            print(slide_name)
            slide_image = getData(slide_url, 'content')

            slide_list[slide_number] = slide_image
            self.q.task_done()


def getData(url, type=None):
    res = requests.get(url, allow_redirects=False, stream = True, timeout=None)
    res.encoding = 'utf-8'
    if type is None:
        return res.text
    if type is 'content':
        return res.content
    if type is 'json':
        return res.json()
    if type is 'raw':
        return res.raw
    print('{type} is unknown'.format(type=type))
    sys.exit()


def convert_pdf(slide_image_list):
    print('image to pdf')
    merger = PdfFileMerger()
    for key in range(len(slide_image_list.keys())):
        slide_image = slide_image_list[key]
        page = img2pdf.convert(slide_image)
        pdf = BytesIO(page)
        merger.append(pdf)

    return merger


def downloader():
    for url in url_list:
        print('open url ...')
        print(url)
        html = getData(url)

        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
        title = soup.select('.j-title-breadcrumb')[0].text
        title = title.lstrip()
        title = title.rstrip()

        print('title : {title}'.format(title=title))
        print('slide list searching ...')

        images = soup.findAll('img', {'class': 'slide_image'})

        print('slide downloading ...')

        # create threadpool
        for i in range(pool_size):
            t = ThreadUrl(q)
            t.setDaemon(True)
            t.start()

        # insert queue
        for idx, image in enumerate(images):
            image_url = image.get('data-full').split('?')[0]
            slide_dict = {'number' : idx, 'url' : image_url}
            q.put(slide_dict)

        q.join()

        print('download done')

        merger = convert_pdf(slide_list)

        with open(title + '.pdf', 'wb') as output:
            merger.write(output)

        print('{title} completed'.format(title=title))
        done_list.append(title)
        slide_list.clear()


def read_list_file(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                url_list.append(line.strip())
    except Exception as err:
        print(err)
        sys.exit()
    for url in url_list:
        print(url)

    downloader()


if __name__ == "__main__":
    try:
        urls = sys.argv[1]
    except IndexError:
        print('Error : please input slideshare url')
        sys.exit()

    try:
        pool_size = int(sys.argv[2])
        print('TheadPool size : {}'.format(sys.argv[2]))
    except IndexError:
        print('TheadPool size : 5')
    finally:
        if re.compile(r'^http[s]?\:\/\/').match(sys.argv[1]):
            url_list.append(sys.argv[1])
            downloader()
        else:
            read_list_file(sys.argv[1])

        print('=' * 30 + ' download list ' + '=' * 30)
        for done in done_list:
            print(done)
        print('{0} / {1}'.format(len(done_list), len(url_list)))
        print('=' * 75)

