# a python program to grap 500pk and download pictures
# author: Aaron
# 3 Feb 2014

import urllib.request
import urllib.parse
import re
import http.cookiejar
import time
import json
import pickle
import os
import os.path

BASE_URL = 'https://500px.com/'
START_URL = 'https://500px.com/popular'
#API = "https://api.500px.com/v1/photos?rpp=38&feature=popular&image_size%5B%5D=3&image_size%5B%5D=4&\
#page="+page+"&sort=&include_states=true&formats=jpeg%2Clytro&only=&authenticity_token="
API_BASE = "https://api.500px.com/v1/photos?"
Cauth_token = 'A%2Be7bNn8RWMGBFySgzumEk3AZhzqXQ0JPs3zUScmm0%3D'
API_PING = 'https://api.500px.com/v1/ping'
SAVE_PATH = './image/'

query = {'rpp': ['38'],
         'feature': ['popular'],
         'image_size[]': ['3', '4'],
         'page': ['1'],
         'sort': [''],
         'include_states': ['true'], 
         'formats': ['jpeg,lytro'],
         'only': [''],
         'authenticity_token': ['']
         }


visited = []
wait_list = []


#build opener
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [('User-Agent',' Mozilla/5.0 (Windows NT 6.3; Win64; x64)\
                     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36')]

def get_token(taget_url):
    with opener.open(taget_url) as f:
        data = f.read().decode()
        #print(data)
        pattern = '<a data-bind="photo_link" data-ga-action="Image" data-ga-category="Photo Thumbnail" href="\S*" id="\S*">'
        test_pat = 'href="\S*"'
        test_data = re.search(test_pat,data)
        print(test_data.group())
        pic_reg = re.compile(pattern)
        res = pic_reg.search(data)
        print(res)
        auth_patt = 'content="(?P<auth_token>\S*)".name="csrf-token"'
        auth = re.search(auth_patt,data)
        print('auth',auth.group('auth_token'))
        auth_token = auth.group('auth_token')
    save_file = open('test.html','w+')
    save_file.write(data)
    save_file.close()
    return auth_token

def save_image(image):
    pass

def get_image(photo):
    '''
    get and save the image
    '''
    image_url = photo['image_url'][1]
    image_id = photo['id']
    image_category = photo['category']
    path = SAVE_PATH + str(image_category)+'/'
    if not os.path.exists(path):
        os.mkdir(path)
    with opener.open(image_url) as res:
        image = res.read()
        with open(path+str(image_id)+'.jpg','wb') as file:
            file.write(image)
        file.close()
        #print(photo_id,'is ok')

def ping():
    opener.addheaders = [('Origin','https://500px.com'),('Referer','https://500px.com/popular')]
    opener.open(API_PING)

def get_list(API):
    global wait_list
    global visited
    print("reading list")
    with opener.open(API) as f:
        json_data = f.read().decode()
    pic_list = json.loads(json_data)
    for photo in pic_list['photos']:
        if photo['id'] not in visited:
            photo['image_url'][1] = photo['image_url'][1].replace('4.jpg','5.jpg')
            wait_list.append(photo)
    print('dowloaded:',len(visited))
    print('to be dowloaded:',len(wait_list))
    json_file = open('pics.json','w+')
    json_file.write(json_data)
    json_file.close()

def handle_wait_list():
    total = len(wait_list)
    count = 0
    for photo in wait_list:
        get_image(photo)
        count = count + 1
        percentage = 100.0*count/total
        print("%.1f%% is done on this page" %percentage)
        visited.append(photo['id'])
        
def get_page(page):    
    print('Dolowding page: ',page)
    query['page'] = [str(page),]
    API = API_BASE + urllib.parse.urlencode(query,doseq=True)
    ping()
    print('Reading list on page %d.' %page)
    get_list(API)
    print('Starting download the images.')
    handle_wait_list()
    print('Page %d is handled successfully.' %page)
    save_visited()

def save_visited():
    with open('visited','wb') as f:
        pickle.dump(visited,f)

def load_visited():
    global visited
    print('Starting...')
    with open('visited','rb') as f:
        visited = pickle.load(f)
    #print(visited)

def main():
    try:
        load_visited()
    except Exception as err:
        print(err)
    auth_token = get_token(START_URL)
    query['authenticity_token'] = [auth_token,]
    for page in range(1,10):
        get_page(page)
        
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting, please wait')
        save_visited()
    except Exception as err:
        print('Somthing is wrong. Exiting...')
        print(err)


    
