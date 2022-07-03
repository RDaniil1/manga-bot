from requests import get
from bs4 import BeautifulSoup
from json import loads
from PIL import Image
from pathlib import Path
import os 
from fake_useragent import UserAgent
from shutil import rmtree


def get_manga_from_vol_num(info_gained: int, url, vol: int = 0, chapter: int = 1):
    try:
        int(vol)
    except Exception:
        return []
    
    os.chdir(Path(__file__).parent)

    current_chapter_link = url.replace('https://readmanga.io/', '') + f'/vol{vol}/{chapter}'
    previous_chapter_link = ''
    manga_name = ''
    headers = {
        'User-Agent' : UserAgent().random
    }

    vol_pdf_paths = []
    while not_last_manga(current_chapter_link, vol, chapter)[info_gained]:

        resp = get(f'https://readmanga.io/{current_chapter_link}', headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')
        picture_uris = []
        
        # manga_name = soup.find('a', attrs={'class' : 'manga-link'}).text
        
        for link in soup.find_all('script', attrs={'type' : 'text/javascript'}):
            if 'rm_h.initReader' in link.text:
                start_lst = link.text.find('[[')
                end_lst = link.text.find(']]') + 2
                
                # json loads method can't work with ' but only with "
                picture_uris = link.text[start_lst:end_lst].replace("'", '"')
                picture_uris = loads(picture_uris)
                del picture_uris[-1] 
                
                picture_uris = [url_data[0] + url_data[2] for url_data in picture_uris]
                
                start_next_link = link.text.find('= "') + 4
                end_next_link = link.text.find('";')
                previous_chapter_link = current_chapter_link
                current_chapter_link = link.text[start_next_link:end_next_link]
                break
        
        if not picture_uris:
            return []
        
        FOLDER_NAME = 'Temp'
        if Path(FOLDER_NAME).is_dir():
            rmtree(FOLDER_NAME, True)
            
        os.mkdir(FOLDER_NAME)
        img_paths = []
        for i in range(len(picture_uris)):
            resp = get(picture_uris[i])
            img_paths += [FOLDER_NAME + '//' + f'{i + 1}.jpg']
            with open(FOLDER_NAME + '//' + f'{i + 1}.jpg', 'wb') as file:
                file.write(resp.content)
                
        pdf_images = []
        img_1 = Image.open(img_paths[0]).convert('RGB')
        for image_path in img_paths[1:]:
            pdf_images += [Image.open(image_path).convert('RGB')] 
        
        for image_path in img_paths:
            os.remove(image_path)
            
        filename = previous_chapter_link.replace('/', '_') + '.pdf'
        vol_pdf_paths += [str(Path(__file__).parent) + '/' + filename]
        
        if len(img_paths) > 1:
            img_1.save(filename, save_all=True, append_images=pdf_images)
        else: 
            img_1.save(filename)
            
        os.rmdir(FOLDER_NAME)

    return vol_pdf_paths

def not_last_manga(current_chapter_link, vol, chapter):
    return {
        1 : 'finish' not in current_chapter_link,
        2 : 'finish' not in current_chapter_link and f'vol{vol}' in current_chapter_link,
        3 : 'finish' not in current_chapter_link and f'vol{vol}' in current_chapter_link and f'/{chapter}' in current_chapter_link,
    }

def find_picture_uris_in_html():
    pass