from tkinter import * # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3

top = Tk()

# Code to add widgets will go here...

top.title("PDF Downloader")
top.geometry('400x400')


def printInput():
    book_inp    = Book_text.get(1.0, "end-1c")
    author_inp  = Author_text.get(1.0, "end-1c")
    sample(book_inp, author_inp)
    lbl.config(text = book_inp + "\n" + author_inp )
    
def sample(a,b) :
    print(a)
    print(b)

Book_text = Text(top, height = 5, width = 30)

Author_text = Text(top, height = 5, width = 30)

download_btn = Button(top, text = "Download", command=printInput)

  
# Label Creation
lbl = Label(top, text = "")
lbl.pack()

Book_text.pack()
Book_text.insert(index = END , chars = "Book")

Author_text.pack()
Author_text.insert(index = END , chars = "Author")

download_btn.pack(side = 'bottom')   

top.mainloop()
