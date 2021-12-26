from tkinter import *
from tkinter.ttk import Combobox
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import csv

x = 0
y = 0
labels = []
location = False
loc_fil = "None"

def filteren():
    global filter_en
    global x
    global y
    filter_en = Entry(root)
    filter_en.insert(END, 'Enter')
    x += 1
    filter_en.grid(column=1, row=x)
    root.bind('<Return>', callback)


def url_filter(url):
    filter_true = True
    filterurl = ['breaking-news', 'live', 'updates', 'up-front', 'video','magazine']
    for i in filterurl:
        if i in url:
            filter_true = False
            break
    return filter_true


def cswrite(url):
    global location
    global loc_fil
    url += '?page='
    urls = []
    for i in range(15):
        urls.append(url + str(i))
    with open('news.csv', 'w', newline='') as outfile:
        fields = ['date', 'location', 'author', 'title', 'article', 'url']
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        for i in urls:
            page = BeautifulSoup(requests.get(i).content, 'html.parser')
            links = [j.get('href') for j in page.find_all('a')]
            links_temp = links.copy()
            for k in links_temp:
                if k is not None and ('/story' not in k or 'https' in k):
                    links.remove(k)
                elif k is None:
                    links.remove(k)
            links = [urljoin(url, t) for t in links]
            for h in links:
                if url_filter(h):
                    page = BeautifulSoup(requests.get(h).content, 'html.parser')
                    filterart = ['ALSO']
                    title = (page.find('h1')).text
                    article = [e.text for e in page.find_all('p')[2:-14]]
                    article_temp = article.copy()
                    for l in article_temp:
                        for m in filterart:
                            if m in l:
                                article.remove(l)
                    article = " ".join(article)

                    location = (page.find_all('dt', class_=None)[4]).text.strip()
                    date = page.find('dt', class_='pubdata').text.strip()
                    author = page.find('dt', class_='title').text.strip()
                    head = {'date': date, 'location': location, 'author': author, 'title': title, 'article': article,
                            'url': i}
                    writer.writerow(head)
    outfile.close()


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_cat_ind(url):
    global url_dict
    url_dict = {}
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    cat = ['India', 'Sports', 'Business', 'Politics', 'Entertainment', 'Science', 'International', 'World']
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            continue
        if domain_name not in href:
            continue
        if a_tag.text not in cat:
            continue
        if href not in url_dict:
            url_dict[a_tag.text] = href
    url_dict = {k: v for k, v in url_dict.items() if k}


def callback(event):
    global x
    addbtn = Button(root, image=icon, command=adbtncre, height=15, width=15)
    addbtn.grid(column=3, row=x)
    if filter_en.get() == 'category':
        global label
        label = Label(root, text=filter_en.get())
        labels.append(label)
        site = website_cb.get()
        dis_cat(site)
    global locationen
    if filter_en.get() == 'location':
        global label2
        label2 = Label(root, text=filter_en.get())
        labels.append(label2)
        locationen = Entry(root)
        locationen.grid(column=2, row=x)
        dis_loc(site)


def adbtncre():
    global labels
    lbl = labels[-1]
    lbl.grid(filter_en.grid_info())
    filter_en.destroy()
    filteren()

def dis_loc():
    global location
    location = True

def dis_cat(site):
    global catfil_cb
    global x
    if site == 'India Today':
        get_cat_ind('https://www.indiatoday.in/sitemap')
        cat_fil = list(url_dict.keys())
        catfil_cb = Combobox(root)
        catfil_cb['values'] = cat_fil
        catfil_cb['state'] = 'readonly'
        catfil_cb.grid(column=2, row=x)



def web_catch():


    if label["text"] == 'category' or label2["text"] == 'category':
        catlink = url_dict[catfil_cb.get()]
        txt3 = Label(root, text="Extracting....")
        txt3.grid(row=4, column=1)
        cswrite(catlink)
        txt4 = Label(root, text="Done")
        txt4.grid(row=4, column=1)



root = Tk()
root.geometry("480x270")
root.resizable(False, False)
root.title('News Scrapper')

websites = ['India Today']

text = Label(text="Select Website:")
text.config(font=('Times Roman', 10))
text.grid(column=0, row=0, padx=6, pady=6)

website_cb = Combobox(root)
website_cb['values'] = websites
website_cb['state'] = 'readonly'
website_cb.grid(column=1, row=0)

text2 = Label(root, text="Filter:")
text2.config(font=('Times Roman', 10))
text2.grid(column=0, row=1, padx=6, pady=6)
filteren()
pathtophoto = Image.open("plus.jpg")
icon = ImageTk.PhotoImage(pathtophoto)

sum_btn = Button(root, text='Extract', command=web_catch)
sum_btn.grid(column=1, row=5, pady=20)

root.mainloop()
