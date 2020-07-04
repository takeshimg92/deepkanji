import string
import random
import os
import pickle
import urllib.request as url
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from bs4 import BeautifulSoup
from multiprocessing import Pool
from pathlib import Path
from time import time, sleep
from tqdm import tqdm


def random_string(n=10):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def get_page_list():
    page = url.urlopen("https://www.unicode.org/charts/unihangridindex.html").read()
    bs = BeautifulSoup(page)

    page_list = []
    for table in tqdm(bs.find("blockquote").findAll("table")):
        for sub in table.findAll("p"):
            link = sub.find("a")
            if link is not None:
                page_list.append(link["href"])
    print(f"Page list found with {len(page_list)} entries")
    return page_list


def get_kanji_page_list(page_list: list):
    kanji_list = []

    for page_url in tqdm(page_list):
        page = url.urlopen(page_url).read()
        bs = BeautifulSoup(page)
        for td in bs.find("td", attrs={"class": "contents"}).findAll("td"):
            if not (td.has_attr("align")) :
                if td.find("a") is not None:
                    kanji_url = td.find("a")["href"]
                    if not "copyright" in kanji_url:
                        kanji_list.append(kanji_url)

    print(f"Kanji page list found with {len(kanji_list)} entries")
    return kanji_list

def load_single_kanji(page_url: str, show_image=False):
    """
    Page should point to a single kanji"s page, 
    eg. https://www.unicode.org/cgi-bin/GetUnihanData.pl?codepoint=3463&useutf8=true
    """
    try:
        page = url.urlopen(page_url).read()
        bs = BeautifulSoup(page)
    except:
        print(f"{page_url}: couldn't open page. Cancelling operation.")
        return 0
    
    try:
        # extract exact link to image
        link_to_image = bs.find("td", attrs={"class": "contents"}).\
            findAll("table")[3].\
            findAll("tr")[1].\
            find("td").\
            find("img")["src"]
    except AttributeError:
        print(f"{page_url}: page structure doesn't follow standard. Cancelling.")
        return 0
    
    # create file to save: use original name + random string
    filename_jpg = os.path.join("kanjis",
                                page_url.split("codepoint=")[1].split("&")[0] + random_string() + ".jpg"
                               )

    # download image
    try:
        url.urlretrieve(link_to_image, filename_jpg)
    except:
        print(f"{page_url}: link to image found, but could not download. Cancelling.")
        return 0
    
    # show image
    if show_image:
    #     Image.open(filename_jpg).show()
        img = mpimg.imread(filename_jpg)
        imgplot = plt.imshow(img)
        plt.show()
        
    # sleep to avoid excess calls
#     sleep(1)
    
    return 1
        
if __name__ == "__main__":
    
    # load list with all kanjis
    print("Load pages list...")
    page_list = get_page_list()
    
    print("Load names of all pages with kanjis...")
    t0 = time()
    with Pool(7) as p:
        kanji_page_list = list(tqdm(p.imap_unordered(get_kanji_page_list, page_list), total=len(page_list)))
    print(f"Finished, runtime = {round((time()-t0)/60.0, 1)} minutes")

    print("Save and reload URL list")
    Path('support_data').mkdir(parents=True, exist_ok=True)
    with open("support_data/kanji_url_list.p", "wb") as f:
        pickle.dump(kanji_page_list, f)
    
    with open("support_data/kanji_url_list.p", "rb") as f:
        kanji_page_list = pickle.load(f)
    
    # Download all kanjis
    Path('kanjis').mkdir(parents=True, exist_ok=True)

    print("Downloading all kanjis...")
    t0 = time()
    with Pool(10) as p:
        list(tqdm(p.imap_unordered(load_single_kanji, kanji_page_list), total=len(kanji_page_list)))
    print(f"Download finished, runtime = {round((time()-t0)/60.0)} minutes")
    