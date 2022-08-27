import fitz, os
from pathlib import Path
import requests, bs4, webbrowser                        # Importing the Modules for Web-Scraping
import pandas as pd                                     # Importing the Module for DataFrames
from download import download                           # Importing the Module for downloading PDF
import pandas as pd, numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from download import download
import os
from os.path import exists
import typing as T

# ---------------------------------------------------------------------------------------------------------------------------------------------

def epub_to_pdf(epub_filename: str, pdf_filename: str) -> None:                 # Convert EPUB to PDF

    downloads_path = str(Path.home() / "Downloads")

    file_path_epub = f"{downloads_path}\\{epub_filename}.epub"

    file_path_pdf = f"{downloads_path}\\{pdf_filename}.pdf"

    doc = fitz.open(file_path_epub)

    a = doc.convert_to_pdf()

    pdf = fitz.open("pdf", a)

    pdf.save(file_path_pdf)

    doc.close()

    os.remove(file_path_epub)

# ---------------------------------------------------------------------------------------------------------------------------------------------

def remove_unwanted_characters(pdf_name: str,) -> str:              # Removes all the Characters that are not valid
    chars = list("/:?*<>|,.();")
    result = pdf_name
    for char in chars:
        result = result.replace(char, "")
    return result

# ---------------------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------       LIBGEN                -----------------------------------------------------------


def search_in_libgen(author_searched_by_user, book_searched_by_user, extension):

    author = author_searched_by_user                        # Name of the Author

    to_search = book_searched_by_user                       # Name of the Book

    pdf_title = to_search                                   # Title for the PDF to be downloaded

    to_search_online = to_search.replace(" ", "+")          # Replacing whitespaces with '+' for the link, to search on libgen

    link_to_search = f"https://libgen.is/search.php?req={to_search_online}&open=0&res=100&view=simple&phrase=1&column=title"
                                                            # The link to search on libgen

    download_of_libgen_completed = False

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    list_of_dataframes = pd.read_html( link_to_search )     # Adds the Table of the Webpage in a List

    table = list_of_dataframes[2]                           # DataFrame of Books from the List

    a = list(table.loc[0])                                  # Placing the Contents of the 1st Row in 'a'

    table.columns = a                                       # Changing the Names of the Columns

    table.drop(0, axis=0, inplace=True)                     # Dropping the 1st Row of the DataFrame

    table.reset_index(inplace=True)                         # Making the Index start from 0 to 99
                                                            # So it has 100 books in the table

    table = table[ (table["Extension"] == extension) ]      # Taking all the Books which are in the PDF format

    table.sort_values( "Year", ascending=False, inplace=True )  # Sorting the Books in the Descending, so the Latest Book is on the Top

    # -------------------------------------------------------------------------------------------------------------------------------------

    result = requests.get(link_to_search)

    soup = bs4.BeautifulSoup(result.text, "lxml")

    titles_list = [soup.find_all("a", id=x)[0].getText() for x in table["ID"]]

    table["Title"] = pd.Series(titles_list, index=table.index, dtype="str")

    table = table.astype({"Author(s)": str, "Title": str})

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    table_2 = table[ ["Author(s)", "Title"] ]   # A new table which consists of the 'Name of the Author' and 'Title of the Books'

    index_number = 0                            # For getting the 'Number of the Book' to be downloaded
                                                # Here, 'Number of the Book' can be 1 or 2 or 3 or 4......

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_for_author( index_for_author):    # For Matching the 'Name of the Author given by the user'
                                                # and the 'Name of the Author of the Books from Libgen'

        actual_author_name = table_2["Author(s)"][index_for_author].split(" ")  # Name of the Author of the Book from Libgen

        result = (
            False  # Setting it to false so at the first match we can break the loop
        )

        for (
            word
        ) in (
            actual_author_name
        ):  # Looping through the Name of the Author given by the user
            if word in author:  # Returns a Number >= 0 if it finds the input given
                result = True
                break

        if len(author) == 0:
            result = True

        return result

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_for_title(
        title_of_book,
    ):  # For Matching the 'Title of the Book given by the user'
        # and the 'Title of the Books from Libgen'
        len_of_book_searched = len(
            to_search.split(" ")
        )  # Length of the List of Words in the Title given by the user

        len_of_book_by_libgen = len(title_of_book.split(" "))

        split_of_book_by_user = to_search.lower().split(
            " "
        )  # List of Words in the Title given by Libgen

        split_of_book_by_libgen = title_of_book.lower().split(
            " "
        )  # List of Words in the Title given by Libgen

        no_of_matches = 0  # Variable for the matches of Titles given by user and Libgen

        if len_of_book_searched <= len_of_book_by_libgen:

            for i in range(
                0, len_of_book_searched
            ):  # Looping through the List of Words in the Title given by Libgen
                if (
                    split_of_book_by_libgen[i].lower()
                    in split_of_book_by_user[i].lower()
                ):  # Checking if the Word is in the Title given by the user
                    no_of_matches += (
                        1  # On a successful match, we increase the number of matches
                    )

            if no_of_matches != len_of_book_searched:

                no_of_matches = 0

                for i in range(
                    0, len_of_book_searched
                ):  # Looping through the List of Words in the Title given by Libgen
                    if (
                        split_of_book_by_user[i].lower()
                        in split_of_book_by_libgen[i].lower()
                    ):  # Checking if the Word is in the Title given by the user
                        no_of_matches += 1
        else:

            for i in range(
                0, len_of_book_by_libgen
            ):  # Looping through the List of Words in the Title given by Libgen
                if (
                    split_of_book_by_libgen[i].lower()
                    in split_of_book_by_user[i].lower()
                ):  # Checking if the Word is in the Title given by the user
                    no_of_matches += (
                        1  # On a successful match, we increase the number of matches
                    )

            if no_of_matches != len_of_book_by_libgen:

                no_of_matches = 0

                for i in range(
                    0, len_of_book_by_libgen
                ):  # Looping through the List of Words in the Title given by Libgen
                    if (
                        split_of_book_by_user[i].lower()
                        in split_of_book_by_libgen[i].lower()
                    ):  # Checking if the Word is in the Title given by the user
                        no_of_matches += 1
        return (no_of_matches == len_of_book_searched) or (
            no_of_matches == len_of_book_by_libgen
        )

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    book_found = False

    for (
        i
    ) in (
        table_2.index
    ):  # Looping through the DataFrame which has 'Author' & 'Title' Columns
        if (check_for_title(table_2["Title"][i])) & (
            check_for_author(i)
        ):  # Checking if the Title Given by the User is
            # in the Title Given by Libgen
            book_found = True
            index_number = i  # Setting the i'th index to index_number
            break

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if book_found:

        result = requests.get(
            link_to_search
        )  # Getting the Info about the Libgen Page, which the User searched

        soup = bs4.BeautifulSoup(result.text, "lxml")  # Beautfiul Soup Instance

        a = soup.select(
            ".c > tr > td > a"
        )  # List of the Anchor Elements from the Webpage Source Code

        c = []  # List for Unique Number('Codes') of the
        # 'URL Links' of the Download Pages

        for i in a:  # Looping through the Anchor Elements of the Webpage
            b = i.get("href")  # Getting the URL('href' attribute) of the Anchor Element
            if b.find("book") == 0:  # Checking if the URL starts with the word 'book'
                c.append(
                    b.split("=")[1]
                )  # Splitting it between '=' and getting the Unique Number('Code')
                # On observation, we decide to take the 2nd element
                # of the Splitted String

        index_of_book_to_download = c

        link_of_download_page = f"http://library.lol/main/{index_of_book_to_download[index_number]}"  # The Download Page for the Chosen Book

        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        result_2 = requests.get(
            link_of_download_page
        )  # Getting the Info about the Download Page, which the Code chose

        soup = bs4.BeautifulSoup(result_2.text, "lxml")  # Beautfiul Soup Instance

        d = soup.select(
            "#download > h2 > a"
        )  # List of the Anchor Elements from the Webpage Source Code

        download_link = d[0].get(
            "href"
        )  # Getting the URL('href' attribute) of the Anchor Element which
        # is our download link

        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        url = download_link  # Setting the url to the download link

        book_name = remove_unwanted_characters(table_2["Title"][index_number])

        downloads_path = str(Path.home() / "Downloads")

        if extension == "pdf":

            file_path = f"{downloads_path}\\{book_name}.pdf"

            path = download(
                url, file_path, replace=True, kind="file", timeout=300.0
            )  # Downloading the Pdf

            download_of_libgen_completed = True

        elif extension == "epub":

            file_path = f"{downloads_path}\\{book_name}.epub"

            path = download(
                url, file_path, replace=True, kind="file", timeout=300.0
            )  # Downloading the Epub

            epub_to_pdf(book_name, book_name)

            download_of_libgen_completed = True

    else:

        download_of_libgen_completed = False

    return download_of_libgen_completed

# -------------------------------------------------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------            PDF-Drive             ----------------------------------------------------------


def search_in_pdf_drive(author_searched_by_user, book_searched_by_user):

    author = author_searched_by_user
    author = author.split()

    to_search = book_searched_by_user
    pdf_title = to_search

    to_search_online = to_search.replace(" ", "-")

    link_to_search = f"http://www.pdfdrive.com/{to_search_online}-books.html"

    download_of_pdfdrive_completed = False

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    result = requests.get(link_to_search)

    soup = bs4.BeautifulSoup(result.text, "lxml")

    name_of_books = soup.select(".ai-search > h2")

    year_of_books = soup.select(".file-info > .fi-year ")

    downloads_of_books = soup.select(".file-info > .fi-hit")

    to_make_download_links = soup.select(".file-right > a ")

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    a = []
    b = []

    for x in name_of_books:
        a.append(x.getText())

    for y in downloads_of_books:
        b.append(int(y.getText().split(" ")[0].replace(",", "")))

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    df_book = pd.DataFrame(data=zip(a, b), columns=["Book", "Downloads"])

    df_book = df_book.astype({"Book": str, "Downloads": int})

    df_book.sort_values("Downloads", ascending=False, inplace=True)

    index_of_book = -1

    for x in df_book.index:
        if df_book.loc[x]["Book"].find(to_search) == 0:
            index_of_book = x
            break

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if index_of_book > -1:

        raw_download_link = to_make_download_links[index_of_book].get("href")

        download_link = raw_download_link[::-1].replace("e", "d", 1)[::-1]

        link_of_download_page = f"http://www.pdfdrive.com{download_link}"

        # webbrowser.open(link_of_download_page)

        download_of_pdfdrive_completed = selenium_headless_downloader(
            "pdfdrive", link_of_download_page, "pdf"
        )

    else:

        download_of_pdfdrive_completed = False

    return download_of_pdfdrive_completed

# ---------------------------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------       Zlib             --------------------------------------------------------------------


def search_in_zlib(author_searched_by_user, book_searched_by_user, extension):

    author = author_searched_by_user

    to_search = book_searched_by_user
    pdf_title = to_search

    to_search_online = (
        to_search.replace(" ", "%20") + "%20" + author.replace(" ", "%20")
    )

    link_to_search = f"https://b-ok.asia/s/{to_search_online}/?languages%5B0%5D=english&extensions%5B0%5D={extension}"

    author = author.split()

    download_of_zlib_completed = False

    # ----------------------------------------------------------------------------------------------------------------------------------------------------

    result = requests.get(link_to_search)

    soup = bs4.BeautifulSoup(result.text, "lxml")

    a = soup.select(".book-rating-interest-score")
    b = soup.select(".book-rating-quality-score")

    book_rating_interest_score_list = np.array([float(x.getText().strip()) for x in a])

    book_rating_quality_score_list = np.array([float(y.getText().strip()) for y in b])

    rating_of_book_list = (
        book_rating_interest_score_list + book_rating_quality_score_list
    )

    d = soup.find_all("h3", itemprop="name")

    link_of_book_list = [
        ("https://b-ok.asia" + x.select("a")[0].get("href")) for x in d
    ]

    title_of_book_list = [x.select("a")[0].getText() for x in d]

    # ---------------------------------------------------------------------------------------------------------------------------------------------------

    e = soup.find_all("div", class_="authors")

    author_list = []

    for length in e:

        individual_author_name = ""

        for element in length:
            individual_author_name = individual_author_name + element.getText() + " "

        author_list.append(individual_author_name)

    books_dataframe = pd.DataFrame(
        {
            "Title": title_of_book_list,
            "Author": author_list,
            "Rating": rating_of_book_list,
            "Link": link_of_book_list,
        }
    )

    books_dataframe = books_dataframe.astype(
        {"Title": str, "Author": str, "Rating": float, "Link": str}
    )

    books_dataframe.sort_values("Rating", ascending=False, inplace=True)

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_for_author(
        index_for_author,
    ):  # For Matching the 'Name of the Author given by the user'
        # and the 'Name of the Author of the Books from Libgen'

        actual_author_name = books_dataframe["Author"][index_for_author].split(
            " "
        )  # Name of the Author of the Book from Libgen

        result = (
            False  # Setting it to false so at the first match we can break the loop
        )

        for (
            word
        ) in (
            actual_author_name
        ):  # Looping through the Name of the Author given by the user
            if word in author:  # Returns a Number >= 0 if it finds the input given
                result = True
                break

        if len(author) == 0:
            result = True

        return result

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def check_for_title(
        title_of_book,
    ):  # For Matching the 'Title of the Book given by the user'
        # and the 'Title of the Books from Libgen'
        len_of_book_searched = len(
            to_search.split(" ")
        )  # Length of the List of Words in the Title given by the user

        len_of_book_by_zlib = len(title_of_book.split(" "))

        split_of_book_by_user = to_search.lower().split(
            " "
        )  # List of Words in the Title given by Libgen

        split_of_book_by_zlib = title_of_book.lower().split(
            " "
        )  # List of Words in the Title given by Libgen

        no_of_matches = 0  # Variable for the matches of Titles given by user and Libgen

        for i in range(
            0, len_of_book_by_zlib
        ):  # Looping through the List of Words in the Title given by Libgen
            if (
                split_of_book_by_zlib[i].lower() in to_search.lower()
            ):  # Checking if the Word is in the Title given by the user
                no_of_matches += (
                    1  # On a successful match, we increase the number of matches
                )

        if no_of_matches != len_of_book_by_zlib:

            no_of_matches = 0

            for i in range(
                0, len_of_book_searched
            ):  # Looping through the List of Words in the Title given by Libgen
                if (
                    split_of_book_by_user[i].lower() in title_of_book.lower()
                ):  # Checking if the Word is in the Title given by the user
                    no_of_matches += 1

        return (no_of_matches == len_of_book_searched) or (
            no_of_matches == len_of_book_by_zlib
        )  # Returns the Boolean of the match

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    book_found = False

    index_number = 0

    for (
        i
    ) in (
        books_dataframe.index
    ):  # Looping through the DataFrame which has 'Author' & 'Title' Columns

        if (check_for_title(books_dataframe["Title"][i])) & (
            check_for_author(i)
        ):  # Checking if the Title Given by the User is
            # in the Title Given by Libgen
            book_found = True
            index_number = i  # Setting the i'th index to index_number
            break

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if book_found:

        link_of_download_page = books_dataframe.loc[index_number, "Link"]

        # webbrowser.open(link_of_download_page)

        download_of_zlib_completed = selenium_headless_downloader(
            "zlib", link_of_download_page, extension
        )

    else:
        download_of_zlib_completed = False

    return download_of_zlib_completed



# -------------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------       SELENIUM FOR PDF-DRIVE & ZLIB          ----------------------------------------------------------------


def remove_unwanted_characters_for_pdfdrive(pdf_name: str,) -> str:              # Removes all the Characters that are not valid
    chars = list("/:?*<>|,.();")
    result = pdf_name
    for char in chars:
        result = result.replace(char, "_")
    return result



downloads_path = str(Path.home() / "Downloads")

# --------------------------------------------------------------------------------------------------------------------------------------------------


def book_title_for_pdfdrive(download_link):

    result = requests.get(download_link)

    soup = bs4.BeautifulSoup(result.text, "lxml")

    a = soup.find("h1", class_="ebook-title")

    title_of_book = a.select("a")[0].getText()

    title_of_book = title_of_book.replace(":", "_")

    return title_of_book


# ----------------------------------------------------------------------------------------------------------------------------------------------------


def book_title_for_zlib(download_link):

    result = requests.get(download_link)

    soup = bs4.BeautifulSoup(result.text, "lxml")

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


# -----------------------------------------------------------------------------------------------------------------------------------------------------


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

    driver = webdriver.Chrome("chromedriver", options=options)  # For Headless Browser

    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))      # For Browser

    params = {"behavior": "allow", "downloadPath": downloads_path}

    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

    download_complete_via_selenium = False

    # -------------------------------------------------------------------------------------------------------------------------------------------------

    # The Below Code Worked Perfectly for 'PDF Drive' for 'GET PDF' And  'PDF'   for HeadLess Browser

    if website == "pdfdrive":

        # For PDf - Drive

        driver.get(download_link)

        driver.implicitly_wait(10)

        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        content = driver.find_elements(
            By.CLASS_NAME, "btn.btn-success.btn-responsive"
        )  # For 'GET PDF'

        if len(content) == 0:

            content = driver.find_element(
                By.CLASS_NAME, "btn.btn-primary.btn-user"
            )  # For 'PDF'

        else:

            content = driver.find_element(
                By.CLASS_NAME, "btn.btn-success.btn-responsive"
            )  # For 'GET PDF'

    # The Below Code Worked Perfectly for Zlib 'PDF' for HeadLess Browser

    elif website == "zlib":

        # For Zlib

        driver.get(download_link)

        content = driver.find_element(By.CLASS_NAME, "book-details-button")

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    content.click()

    # -------------------------------------------------------------------------------------------------------------------------------------------------

    title_of_book = ""

    if website == "pdfdrive":

        print("Downloading E-Book from PDF-Drive \n Please check your Downloads Folder")

        title_of_book = book_title_for_pdfdrive(download_link)

        title_of_book = remove_unwanted_characters_for_pdfdrive(title_of_book)

        title_of_book = title_of_book + " ( PDFDrive )"

        path_to_file = f"{downloads_path}\\{title_of_book}.pdf"

        while True:

            file_exists = exists(path_to_file)

            if file_exists:
                break

        download_complete_via_selenium = True

        driver.quit()

    elif website == "zlib":

        result = requests.get(driver.current_url)

        soup = bs4.BeautifulSoup(result.text, "lxml")

        daily_limit_error = soup.find_all("td", class_="g-page-content")

        # if(len(daily_limit_error) > 0) :

        #     print("Daily Limit of Downloads for Zlib has been reached")

        #     download_complete_via_selenium = False

        #     driver.quit()

        # elif
        if len(daily_limit_error) > 0:

            print("Downloading E-Book from Zlib \nPlease check your Downloads Folder")

            title_of_book = book_title_for_zlib(download_link)

            title_of_book = title_of_book + " (z-lib.org)"

            path_to_file = f"{downloads_path}\\{title_of_book}.{extension}"

            while True:

                file_exists = exists(path_to_file)

                if file_exists:
                    break

            download_complete_via_selenium = True

            driver.quit()

    return download_complete_via_selenium


# -------------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------    SEARCH A BOOK         ---------------------------------------------------------------------------

def easy_search_for_book(a):

    separation_candidates = list(":?;*,(|#[!@$%+={<")
    for char in separation_candidates:
        if char in book:
            a = a.split(char)[0]
            return a
        
# -------------------------------------------------------------------------------------------------------------------------------------------------------------

# book = input("Enter book name : ")
# author = input("Enter book author : ")

book   = ""
author = ""

characters_to_strip = " .,;:/?!#*&^-}_{~`@$%)[](<>|+="

author = author.strip(characters_to_strip)
book = book.strip(characters_to_strip)

author = remove_unwanted_characters(author)

book = easy_search_for_book(book)

extension_pdf = "pdf"

if search_in_libgen(author, book, extension_pdf) == False:

    if search_in_zlib(author, book, extension_pdf) == False:

        if search_in_pdf_drive(author, book) == False:

            extension_epub = "epub"

            if search_in_libgen(author, book, extension_epub) == False:

                if search_in_zlib(author, book, extension_epub) == False:

                    print("The Book is not available in the Ebook Format")
