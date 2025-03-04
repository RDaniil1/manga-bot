from requests import get
from bs4 import BeautifulSoup
from json import loads
from PIL import Image
from pathlib import Path
import os 
from fake_useragent import UserAgent
from shutil import rmtree



def get_picture_uris(link):
    start_lst = link.text.find('[[')
    end_lst = link.text.find(']]') + 2
    
    # json loads method can't work with ' but only with "
    picture_uris = link.text[start_lst:end_lst].replace("'", '"')
    picture_uris = loads(picture_uris)
    del picture_uris[-1] 
    
    picture_uris = [url_data[0] + url_data[2] for url_data in picture_uris]
    return picture_uris

def get_previous_current_link(link, current_chapter_link):
    start_next_link = link.text.find('= "') + 4
    end_next_link = link.text.find('";')
    return current_chapter_link, link.text[start_next_link:end_next_link]

def get_image_paths(folder_name, picture_uris):
    img_paths = []
    for i in range(len(picture_uris)):
        resp = get(picture_uris[i])
        img_paths += [folder_name + '//' + f'{i + 1}.jpg']
        with open(folder_name + '//' + f'{i + 1}.jpg', 'wb') as file:
            file.write(resp.content)
    return img_paths

def recreate_temp_folder(folder_name):
    if Path(folder_name).is_dir():
        rmtree(folder_name, True)
    os.mkdir(folder_name)

def get_image_and_pdf_images(img_paths):
    pdf_images = []
    img_1 = Image.open(img_paths[0]).convert('RGB')
    for image_path in img_paths[1:]:
        pdf_images += [Image.open(image_path).convert('RGB')] 
        os.remove(image_path)
    os.remove(image_path[0])
    return img_1, pdf_images

def get_manga_from_vol_num(info_gained: int, url, vol: int = 0, chapter: int = 1):
    try:
        int(vol)
    except ValueError:
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
        
        for link in soup.find_all('script', attrs={'type' : 'text/javascript'}):
            if 'rm_h.initReader' in link.text:
                picture_uris = get_picture_uris(link)
                previous_chapter_link, current_chapter_link = get_previous_current_link(link, current_chapter_link)
                break
        if not picture_uris:
            return []
        
        FOLDER_NAME = 'Temp'
        recreate_temp_folder(FOLDER_NAME)
        img_paths = get_image_paths(FOLDER_NAME, picture_uris)
        img_1, pdf_images = get_image_and_pdf_images(img_paths)
            
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
