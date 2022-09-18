import fitz
import requests
import time
from bs4 import BeautifulSoup
import webbrowser                     
from pandas import Series
from pandas import DataFrame
from pandas import read_html
from numpy import array
import os
from os import remove as os_remove
from os import path as os_path
from os import stat
from os.path import exists
from threading import Thread
from socket import gethostbyname
from socket import gethostname
from pathlib import Path
from download import download
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tkinter import Tk
from tkinter import PhotoImage
from tkinter import Canvas
from tkinter import Label
from tkinter import Text
from tkinter import Button
from tkinter import messagebox
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def epub_to_pdf_gen():                           
    downloads_path = str(Path.home() / "Downloads")
    for fname in os.listdir(downloads_path):
        if fname.endswith('.epub'):
            fname_n         = fname.split('.epub')[0]
            file_path_epub  = f"{downloads_path}\\{fname_n}.epub"
            file_path_pdf   = f"{downloads_path}\\{fname_n}.pdf"
            try:
                doc = fitz.open(file_path_epub)
                a   = doc.convert_to_pdf()
                pdf = fitz.open("pdf", a)
                pdf.save(file_path_pdf)
                doc.close()
                os_remove(file_path_epub)
            except:
                pass
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
def remove_character_not_valid_in_pdfname(a):
    char_list   = "/:?*<>|"
    for i in char_list:
        a = a.replace(i, "")
    return a
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
pdf_size_to_download_for_zlib = ""
byte_info_for_pdfdrive = ""
keep_running = True
# ---------------------------------------------------------       LIBGEN        -----------------------------------------------------------------------------------------
def downloaded_stat_for_libgen(Pdf_file_size_to_download):
    global keep_running
    while keep_running:
        for fname in os.listdir(downloads_path):
            if fname.endswith('.part'):
                try:
                    file_size = os.path.getsize(f"{downloads_path}\\{fname}")
                    info_text.config(text=f'Downloading....{round((file_size / (1024 * 1024)),1)} {Pdf_file_size_to_download.split()[1]} / {Pdf_file_size_to_download}')
                    time.sleep(0.2)                                      
                except Exception as e:
                    print(e)
        if(keep_running == False):
            break
def search_in_libgen(author_searched_by_user, book_searched_by_user, extension):
    author = author_searched_by_user
    to_search = book_searched_by_user                   
    pdf_title = to_search
    to_search_online = to_search.replace(" ", "+")
    link_to_search = f"https://libgen.is/search.php?req={to_search_online}&open=0&res=100&view=simple&phrase=1&column=title"
    download_of_libgen_completed = False
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    list_of_dataframes = read_html(link_to_search)
    table = list_of_dataframes[2]
    a = list(table.loc[0])
    table.columns = a
    table.drop(0, axis=0, inplace=True)
    table.reset_index(inplace=True)
    table = table[(table['Extension'] == extension)]
    table.sort_values('Year', ascending=False, inplace=True)
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    result = requests.get(link_to_search)
    soup = BeautifulSoup(result.text, "lxml")
    titles_list = [soup.find_all('a', id=x)[0].getText() for x in table['ID']]
    table['Title'] = Series(titles_list, index=table.index, dtype='str')
    table = table.astype({'Author(s)': str, 'Title': str})
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    table_2 = table[['Author(s)', 'Title']]
    index_number = 0
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def check_for_author(index_for_author):
        actual_author_name = table_2['Author(s)'][index_for_author].split(" ")   
        result = False
        for word in actual_author_name:
            if (word in author):
                result = True
                break
        if(len(author) == 0):
            result = True
        return result
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def check_for_title(title_of_book):
        len_of_book_searched = len(to_search.split(" "))
        len_of_book_by_libgen = len(title_of_book.split(" "))
        split_of_book_by_user = to_search.lower().split(" ")
        split_of_book_by_libgen = title_of_book.lower().split(" ")
        no_of_matches = 0
        if(len_of_book_searched <= len_of_book_by_libgen):
            for i in range(0, len_of_book_searched):
                if(split_of_book_by_libgen[i].lower() in split_of_book_by_user[i].lower()):
                    no_of_matches += 1
            if(no_of_matches != len_of_book_searched):
                no_of_matches = 0
                for i in range(0, len_of_book_searched):
                    if(split_of_book_by_user[i].lower() in split_of_book_by_libgen[i].lower()):
                        no_of_matches += 1
        else:
            for i in range(0, len_of_book_by_libgen):
                if(split_of_book_by_libgen[i].lower() in split_of_book_by_user[i].lower()):
                    no_of_matches += 1
            if(no_of_matches != len_of_book_by_libgen):
                no_of_matches = 0
                for i in range(0, len_of_book_by_libgen):
                    if(split_of_book_by_user[i].lower() in split_of_book_by_libgen[i].lower()):
                        no_of_matches += 1
        return ((no_of_matches == len_of_book_searched) or (no_of_matches == len_of_book_by_libgen))
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    book_found = False
    for i in table_2.index:
        if((check_for_title(table_2['Title'][i])) & (check_for_author(i))):
            book_found = True
            index_number = i
            break
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if(book_found):
        result = requests.get(link_to_search)
        soup = BeautifulSoup(result.text, "lxml")
        a = soup.select(".c > tr > td > a")
        c = []
        for i in a:
            b = i.get('href')
            if(b.find("book") == 0):
                c.append(b.split("=")[1])
        index_of_book_to_download = c
        link_of_download_page = f"http://library.lol/main/{index_of_book_to_download[index_number]}"
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        result_2 = requests.get(link_of_download_page)
        soup = BeautifulSoup(result_2.text, "lxml")
        d = soup.select("#download > h2 > a")
        download_link = d[0].get('href')
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        url = download_link
        book_name = remove_character_not_valid_in_pdfname(table_2['Title'][index_number])
        downloads_path = str(Path.home() / "Downloads")
        global keep_running
        if(extension == 'pdf'):
            info_text.config(text="Downloading....")
            file_path = f"{downloads_path}\\{book_name}.pdf"
            file_path_while_downloading = f"{downloads_path}\\{book_name}.pdf.part"
            pdf_file_size_to_download = table.loc[index_number]["Size"]
            thread_3 = Thread(target=downloaded_stat_for_libgen,args=(pdf_file_size_to_download,))
            thread_3.start()
            path = download(url, file_path, replace=True,kind="file", timeout=300.0) 
            button_1['state'] = "normal"           
            keep_running = False
            info_text.config(text="Book has been downloaded!")
            download_of_libgen_completed = True
        elif(extension == 'epub'):
            info_text.config(text="Downloading....")
            file_path = f"{downloads_path}\\{book_name}.epub"
            pdf_file_size_to_download = table.loc[index_number]["Size"]
            thread_3 = Thread(target=downloaded_stat_for_libgen,args=(pdf_file_size_to_download,))
            thread_3.start()
            path = download(url, file_path, replace=True,kind="file", timeout=300.0)
            epub_to_pdf_gen()
            button_1['state'] = "normal"
            keep_running = False
            info_text.config(text="Book has been downloaded!")
            download_of_libgen_completed = True
    else:
        download_of_libgen_completed = False
    return download_of_libgen_completed
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------            PDF-Drive             ------------------------------------------------------------------------------------------
def search_in_pdf_drive(author_searched_by_user, book_searched_by_user):
    author = author_searched_by_user
    author = author.split()
    to_search = book_searched_by_user
    pdf_title = to_search
    to_search_online = to_search.replace(" ", "-")
    link_to_search = f"http://www.pdfdrive.com/{to_search_online}-books.html"
    download_of_pdfdrive_completed = False
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    try:
        result = requests.get(link_to_search)
        soup = BeautifulSoup(result.text, "lxml")
        name_of_books = soup.select(".ai-search > h2")
        year_of_books = soup.select(".file-info > .fi-year ")
        downloads_of_books = soup.select(".file-info > .fi-hit")
        to_make_download_links = soup.select(".file-right > a ")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        a = []
        b = []
        for x in name_of_books:
            a.append(x.getText())
        for y in downloads_of_books:
            b.append(int(y.getText().split(" ")[0].replace(",", "")))
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        df_book = DataFrame(data=zip(a, b), columns=["Book", "Downloads"])
        df_book = df_book.astype({"Book": str, "Downloads": int})
        df_book.sort_values("Downloads", ascending=False, inplace=True)
        index_of_book = -1
        for x in df_book.index:
            if df_book.loc[x]["Book"].lower().find(to_search.lower()) == 0:
                index_of_book = x
                break
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if index_of_book > -1:
            raw_download_link = to_make_download_links[index_of_book].get("href")
            download_link = raw_download_link[::-1].replace("e", "d", 1)[::-1]
            link_of_download_page = f"http://www.pdfdrive.com{download_link}"
            result = requests.get(f"http://www.pdfdrive.com{raw_download_link}")
            soup = BeautifulSoup(result.text, "lxml")
            book_info_for_pdfdrive = soup.select(".ebook-file-info > .info-green")
            global byte_info_for_pdfdrive
            for i in book_info_for_pdfdrive:
                if "KB" in i.getText():
                    byte_info_for_pdfdrive = i.getText()
                    break
                elif "MB" in i.getText():
                    byte_info_for_pdfdrive = i.getText()
                    break
            download_of_pdfdrive_completed = selenium_headless_downloader("pdfdrive", link_of_download_page, "pdf")
        else:
            download_of_pdfdrive_completed = False
    except:
        pass
    return download_of_pdfdrive_completed
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------       Zlib       --------------------------------------------------------------------------------
def search_in_zlib(author_searched_by_user, book_searched_by_user, extension):
    author = author_searched_by_user
    to_search = book_searched_by_user
    pdf_title = to_search
    to_search_online = (to_search.replace(" ", "%20") + "%20" + author.replace(" ", "%20"))
    link_to_search = f"https://b-ok.asia/s/{to_search_online}/?languages%5B0%5D=english&extensions%5B0%5D={extension}"
    author = author.split()
    download_of_zlib_completed = False
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    try:
        result = requests.get(link_to_search)
        soup = BeautifulSoup(result.text, "lxml")
        a = soup.select(".book-rating-interest-score")
        b = soup.select(".book-rating-quality-score")
        book_rating_interest_score_list = array([float(x.getText().strip()) for x in a])
        book_rating_quality_score_list = array([float(y.getText().strip()) for y in b])
        rating_of_book_list = (book_rating_interest_score_list + book_rating_quality_score_list)
        d = soup.find_all("h3", itemprop="name")
        link_of_book_list = [("https://b-ok.asia" + x.select("a")[0].get("href")) for x in d]
        title_of_book_list = [x.select("a")[0].getText() for x in d]
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        e = soup.find_all("div", class_="authors")
        author_list = []
        for length in e:
            individual_author_name = ""
            for element in length:
                individual_author_name = individual_author_name + element.getText() + " "
            author_list.append(individual_author_name)
        books_dataframe = DataFrame({"Title": title_of_book_list,"Author": author_list,"Rating": rating_of_book_list,"Link": link_of_book_list,})
        books_dataframe = books_dataframe.astype({"Title": str, "Author": str, "Rating": float, "Link": str})
        books_dataframe.sort_values("Rating", ascending=False, inplace=True)
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        def check_for_author(index_for_author,):  
            actual_author_name = books_dataframe["Author"][index_for_author].split(" ")  
            result = (False)
            for (word) in (actual_author_name):  
                if word in author:  
                    result = True
                    break
            if len(author) == 0:
                result = True
            return result
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        def check_for_title(title_of_book,):  
            len_of_book_searched = len(to_search.split(" "))  
            len_of_book_by_zlib = len(title_of_book.split(" "))
            split_of_book_by_user = to_search.lower().split(" ") 
            split_of_book_by_zlib = title_of_book.lower().split(" ")  
            no_of_matches = 0  
            for i in range(0, len_of_book_by_zlib):  
                if (split_of_book_by_zlib[i].lower() in to_search.lower()):  
                    no_of_matches += (1)
            if no_of_matches != len_of_book_by_zlib:
                no_of_matches = 0
                for i in range(0, len_of_book_searched):  
                    if (split_of_book_by_user[i].lower() in title_of_book.lower()):  
                        no_of_matches += 1
            return (no_of_matches == len_of_book_searched) or (no_of_matches == len_of_book_by_zlib)
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        book_found = False
        index_number = 0
        for(i) in (books_dataframe.index):  
            if (check_for_title(books_dataframe["Title"][i])) & (check_for_author(i)): 
                book_found = True
                index_number = i 
                break
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if book_found:
            link_of_download_page = books_dataframe.loc[index_number, "Link"]
            try:
                result = requests.get(link_of_download_page)
                soup = BeautifulSoup(result.text, "lxml")
                global pdf_size_to_download_for_zlib
                pdf_size_to_download_for_zlib = soup.select(".bookDetailsBox > .bookProperty.property__file > .property_value ")[0].getText().split(",")[1]
            except:
                print("Error faced")
            download_of_zlib_completed = selenium_headless_downloader("zlib", link_of_download_page, extension)
        else:
            download_of_zlib_completed = False
    except:
        pass
    return download_of_zlib_completed
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------       SELENIUM FOR PDF-DRIVE & ZLIB          ----------------------------------------------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os_path.dirname(__file__)
    return os_path.join(base_path, relative_path)
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def remove_unwanted_characters_for_pdfdrive(pdf_name: str,) -> str:
    chars = list("/:?*<>|,.();")
    result = pdf_name
    for char in chars:
        result = result.replace(char, "_")
    return result
downloads_path = str(Path.home() / "Downloads")
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def book_title_for_pdfdrive(download_link):
    result = requests.get(download_link)
    soup = BeautifulSoup(result.text, "lxml")
    a = soup.find("h1", class_="ebook-title")
    title_of_book = a.select("a")[0].getText()
    title_of_book = title_of_book.replace(":", "_")
    return title_of_book
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def book_title_for_zlib(download_link):
    result = requests.get(download_link)
    soup = BeautifulSoup(result.text, "lxml")
    a = soup.find("h1", itemprop="name").getText()
    a = a.strip(" \n")
    b = soup.find("div", class_="col-sm-9")
    b = b.find_all("a", title="Find all the author's books")
    title_of_pdf = a
    c = ""
    if len(b) > 1:
        for x in b:
            c = c + x.getText() + ", "
        c = c.strip(", ")
        title_of_pdf = title_of_pdf + " " + f"({c})"
    elif len(b) == 1:
        title_of_pdf = title_of_pdf + " " + f"({b[0].getText()})"
    return title_of_pdf
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def selenium_headless_downloader(website, download_link, extension):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(resource_path("chromedriver.exe"), options=options)
    params = {"behavior": "allow", "downloadPath": downloads_path}
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
    download_complete_via_selenium = False
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    if website == "pdfdrive":
        try:
            driver.get(download_link)
        except:
            info_text.config(text="Servor Error. Please Try Again")
            button_1['state'] = "normal"
        driver.implicitly_wait(10)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        content = driver.find_elements(By.CLASS_NAME, "btn.btn-success.btn-responsive")  
        if len(content) == 0:
            content = driver.find_element(By.CLASS_NAME, "btn.btn-primary.btn-user")  
        else:
            content = driver.find_element(By.CLASS_NAME, "btn.btn-success.btn-responsive") 
    elif website == "zlib":
        try:
            driver.get(download_link)
        except:
            info_text.config(text="Servor Error. Please Try Again")
            button_1['state'] = "normal"
        content = driver.find_element(By.CLASS_NAME, "book-details-button")
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    content.click()
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    title_of_book = ""
    if website == "pdfdrive":
        print("Downloading E-Book from PDF-Drive Please check your Downloads Folder")
        info_text.config(text="Downloading....")
        title_of_book = book_title_for_pdfdrive(download_link)
        title_of_book = remove_unwanted_characters_for_pdfdrive(title_of_book)
        title_of_book = title_of_book + " ( PDFDrive )"
        file_name_pdfdrive = ""       
        path_to_file = ""         
        while True:
            for fname in os.listdir(downloads_path):
                if fname.endswith('.crdownload'):
                    if(file_name_pdfdrive == ""):
                        file_name_pdfdrive = fname.split(".crdownload")[0]
                        path_to_file = f"{downloads_path}\\{file_name_pdfdrive}"
                    try:
                        file_size = os.path.getsize(f"{downloads_path}\\{fname}")
                        info_text.config(text=f'Downloading....{round((file_size / (1024 * 1024)),1)} {byte_info_for_pdfdrive.split()[1]} / {byte_info_for_pdfdrive}')
                        time.sleep(0.2)
                    except Exception as e:
                        print(e)
                elif (fname == file_name_pdfdrive):
                    path_to_file = f"{downloads_path}\\{file_name_pdfdrive}" 
                    break
            try:
                file_exists = exists(path_to_file)
                if file_exists:
                    break
            except Exception as e:
                print(e)
                pass
        epub_to_pdf_gen()
        download_complete_via_selenium = True
        button_1['state'] = "normal"
        info_text.config(text="Book has been downloaded!")
        driver.quit()
    elif website == "zlib":
        result = requests.get(driver.current_url)
        soup = BeautifulSoup(result.text, "lxml")
        try:
            driver.find_element(By.CLASS_NAME, "download-limits-error")
            download_complete_via_selenium = False
            print("Zlibs Daily Limit Error")
        except:
            print("Downloading E-Book from Zlib \nPlease check your Downloads Folder")
            info_text.config(text="Downloading....")
            title_of_book = book_title_for_zlib(download_link)
            title_of_book = remove_character_not_valid_in_pdfname(title_of_book)
            title_of_book = title_of_book + " (z-lib.org)"
            file_name_zlib = ""       
            path_to_file = ""         
            while True:
                for fname in os.listdir(downloads_path):
                    if fname.endswith('.crdownload'):
                        if(file_name_zlib == ""):
                            file_name_zlib = fname.split(".crdownload")[0]
                            path_to_file = f"{downloads_path}\\{file_name_zlib}"
                        try:
                            file_size = os.path.getsize(f"{downloads_path}\\{fname}")
                            info_text.config(text=f'Downloading....{round((file_size / (1024 * 1024)),1)} MB / {str(pdf_size_to_download_for_zlib)}')
                            time.sleep(0.2)
                        except Exception as e:
                            print(e)
                    elif (fname == file_name_zlib):
                        path_to_file = f"{downloads_path}\\{file_name_zlib}" 
                        break
                try:
                    file_exists = exists(path_to_file)
                    if file_exists:
                        break
                except Exception as e:
                    print(e)
                    pass
            download_complete_via_selenium = True
            epub_to_pdf_gen()
            button_1['state'] = "normal"
            info_text.config(text="Book has been downloaded!")
            driver.quit()
    return download_complete_via_selenium
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------    SEARCH A BOOK         ---------------------------------------------------------------------------------------------------------------------
def remove_unwanted_characters_from_author(a):
    char_list   = "/:?*<>|,.();"
    for i in char_list:
        a = a.replace(i, "")
    return a
def easy_search_for_book(a):
    char_list = ":?;*,(|#[!@$%+={<"
    for i in char_list:
        if(i in a):
            a = a.split(i)[0]
            break
    return a
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def search_the_book(author_, book_):
    author = author_
    book = book_
    characters_to_strip = " .,;:/?!#*&^-}_{~`@$%)[](<>|+="
    author = author.strip(characters_to_strip)
    book = book.strip(characters_to_strip)
    author = remove_unwanted_characters_from_author(author)
    book = easy_search_for_book(book)
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    extension_pdf = 'pdf'
    if(search_in_libgen(author, book, extension_pdf) == False):
        if(search_in_zlib(author, book, extension_pdf) == False):
            extension_epub = 'epub'
            if(search_in_libgen(author, book, extension_epub) == False):
                if(search_in_zlib(author, book, extension_epub) == False):
                    extension_pdf = 'pdf'
                    if(search_in_pdf_drive(author, book) == False):
                        print('The Book is not available in the Ebook Format')
                        info_text.config(text="Book Not Available")
                        button_1['state'] = "normal"
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------Current GUI -----------------------------------------------------------------------------------------------------------------------
window = Tk()
window.geometry("574x230")
window.title("Books.io")
photo = PhotoImage(file=resource_path("book.png"))
window.iconphoto(False, photo)
window.configure(bg="#FFFFFF")
canvas = Canvas(window,bg="#FFFFFF",height=287,width=574,bd=0,highlightthickness=0,relief="ridge")
canvas.place(x=0, y=0)
canvas.create_text(27.600372314453125,96.34383392333984,anchor="nw",text="Author",fill="#000000",font=("Abel Regular", 20 * -1))
info_text = Label(window,background="#FFFFFF",text="",font=("Abel Regular", 7))
info_text.place(relx=0.0,rely=1.0,anchor='sw')
info_text_for_download = Label(window,background="#FFFFFF",text="Tip: Use the exact Book Title and Author Name",font=("Abel Regular", 7),fg="green")
info_text_for_download.place(relx=0.16,rely=0.04)
def callback(url):
    webbrowser.open_new_tab(url)
info_text_for_github = Label(window,background="#FFFFFF",text="Give a star to our project",fg="blue",cursor="hand2",font=("Abel Regular", 7))
info_text_for_github.pack()
info_text_for_github.bind("<Button-1>", lambda e: callback("https://github.com/RohitKonge/PDF-Version-of-any-Book"))
info_text_for_github.place(relx=1.0,rely=1.0,anchor='se')
canvas.create_text(32.243743896484375,28.401931762695312,anchor="nw",text="Book",fill="#000000",font=("Abel Regular", 20 * -1))
entry_image_1 = PhotoImage(file=resource_path("entry_1.png"))
entry_bg_1 = canvas.create_image(316.0,38.5,image=entry_image_1)
entry_1 = Text(font=("Abel Regular", 10),bd=0,bg="#FFFFFF",highlightthickness=0)
entry_1.place(x=94.0,y=28.6,width=444.0,height=22.0)
entry_image_2 = PhotoImage(file=resource_path("entry_2.png"))
entry_bg_2 = canvas.create_image(316.0,106.5,image=entry_image_2)
entry_2 = Text(font=("Abel Regular", 10),bd=0,bg="#FFFFFF",highlightthickness=0)
entry_2.place(x=94.0,y=96.6,width=444.0,height=22.0)
def btn_click():
    book_inp = entry_1.get(1.0, "end-1c")
    author_inp = entry_2.get(1.0, "end-1c")
    book_inp = book_inp.strip()
    author_inp = author_inp.strip()
    book_inp = book_inp.title()
    author_inp = author_inp.title()
    global keep_running
    if(book_inp == "" and author_inp == ""):
        info_text.config(text="Please enter the Book's Title and Author")
        button_1['state'] = "normal"
    elif(book_inp == "" and author_inp != ""):
        info_text.config(text="Please enter the Book's Title")
        button_1['state'] = "normal"
    else:
        keep_running = True
        search_the_book(author_inp, book_inp)
        thread_2 = Thread()
        thread_2.start()
        thread_2.join()
def thread_make():
    if(check_internet_connection()):
        info_text.config(text="Searching....")
        button_1['state'] = "disabled"
        try:
            thread_1 = Thread(target=btn_click)
            thread_1.start()
        except:
            info_text.config(text="Please Restart the App")
def check_internet_connection():
    connected_to_internet = False
    IPaddress = gethostbyname(gethostname())
    if IPaddress == "127.0.0.1":
        connected_to_internet = False
        info_text.config(text="Check your internet connection")
    else:
        connected_to_internet = True
    return connected_to_internet
check_internet_connection()
button_image_1 = PhotoImage(file=resource_path("button_1.png"))
button_1 = Button(image=button_image_1,borderwidth=0,highlightthickness=0,command=thread_make,relief="flat",cursor="hand2",state="normal")
button_1.place(x=200.0,y=150.0,width=174.8668212890625,height=43.995155334472656)
def on_opening():
    for fname in os.listdir(downloads_path):
        if (fname.endswith('.part') or fname.endswith('.crdownload')):
            try:
                os_remove((f"{downloads_path}\\{fname}"))
            except Exception as e:
                print(e)    
def on_closing():
    for fname in os.listdir(downloads_path):
        if (fname.endswith('.part') or fname.endswith('.crdownload')):
            try:
                os_remove((f"{downloads_path}\\{fname}"))
            except Exception as e:
                print(e)
    thread_2 = Thread()
    thread_2.start()
    thread_2.join()
    window.destroy()
on_opening()
window.protocol("WM_DELETE_WINDOW", on_closing)
window.resizable(False, False)
window.attributes('-topmost', 1)
window.mainloop()
# --------------------------------------------------------------    Current GUI    ---------------------------------------------------------------------------------------
# Code For .exe :
# pyinstaller Books.py -n Books.io -w --add-binary chromedriver.exe;. -i book.png --add-data book.png;. --add-data entry_1.png;. --add-data entry_2.png;. --add-data button_1.png;.
