import os
from pathlib import Path

downloads_path = str(Path.home() / "Downloads")

title_of_book = "Laughing"

print(len(os.listdir(downloads_path)))
print(os.listdir(downloads_path)[0])


# for filename in os.listdir(downloads_path):
#     print(filename)
#     try:
#         # print(filename)
#         if(title_of_book in filename):
#             print(filename)
#             pdf_found = True
#             break
#     except:
#         pass

    # if(title_of_book in filename):
    #     pdf_found = True
    #     break
