import getpass, calendar, os, platform, sys, urllib.request, json, re, pickle, time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from random import randint
from bs4 import BeautifulSoup
# Global Variables

driver = None

def login(email, password, is_symbian = False):
    """ Logging into our own profile """

    try:
        global driver

        options = Options()

        #  Code to disable notifications pop up of Chrome Browser
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")

        if is_symbian:
            options.add_argument("user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/14.14263")

        try:
            platform_ = platform.system().lower()
            if platform_ in ['linux', 'darwin']:
                driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
            else:
                driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)
        except:
            print("Kindly replace the Chrome Web Driver with the latest one from"
                  "\nhttp://chromedriver.chromium.org/downloads"
                  "\nYour OS: {}".format(platform_)
                 )
            # exit()
        driver.get("https://facebook.com")
        driver.maximize_window()
        
        # cookies for authorization
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)



        # if cookies doesn't work:


        # # filling the form
        # driver.find_element_by_name('email').send_keys(email)
        # time.sleep(0.732)
        # driver.find_element_by_name('pass').send_keys(password)
        # time.sleep(1.231)
        # # clicking on login button
        # driver.find_element_by_id('loginbutton').click()
        # time.sleep(1.112)

    except Exception as e:
        print("There's some error in log in.")
        print(sys.exc_info())
        print('\n', e, sep='')
        # driver.close()
        # driver.quit()
        # exit()

def get_post_id(url: str) -> str:
    post_id = ''

    i = url.find('fbid=')
    if i != -1:
        i = i + len('fbid=')
        while url[i].isdigit():
            post_id += url[i]
            i += 1
            if i == len(url):
                break
        return post_id

    i = url.find('view=permalink')
    if i != -1:
        i = url.find("&id=")
        if i != -1:
            i = i + len("&id=")
            while url[i].isdigit():
                post_id += url[i]
                i += 1
                if i == len(url):
                    break
            return post_id

    i = url.find('/permalink/')
    if i != -1:
        i = i + len('/permalink/')
        while url[i].isdigit():
            post_id += url[i]
            i += 1
            if i == len(url):
                break
        return post_id

    i = url.find('/posts/')
    if i != -1:
        i = i + len('/posts/')
        while url[i].isdigit():
            post_id += url[i]
            i += 1
            if i == len(url):
                break
        return post_id

    i = url.find('/photos/')
    if i != -1:
        temp = url[i + len('/photos/'):]
        i = temp.find('/') + 1
        while temp[i].isdigit():
            post_id += temp[i]
            i += 1
            if i == len(url):
                break
        return post_id

    i = url.find('/videos/')
    if i != -1:
        i = i + len('/videos/')
        while url[i].isdigit():
            post_id += url[i]
            i += 1
            if i == len(url):
                break
        return post_id  
    return None

def get_video_post_id(post_url):
    driver.get(post_url)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    secondary_soup = soup.find(rel="dialog", ajaxify=re.compile("/ufi/reaction/profile/dialog/?.+"))
    text = secondary_soup['href']
    idx = text.find('ft_ent_identifier=')
    post_id = ''
    ok = True
    i = 0
    text = text[idx + len('ft_ent_identifier=')::]

    while ok:
        ok = text[i].isdigit()
        if not ok:
            break
        post_id += text[i]
        i += 1

    return post_id

users_dict = {}

def get_liked(post_url: str) -> dict:
    post_id = get_post_id(post_url)

    if '/videos/' in post_url:
        post_id = get_video_post_id(post_url)


    likes_url = "https://www.facebook.com/ufi/reaction/profile/browser/fetch/?limit={}&total_count={}&fb_dtsg_ag=AQx9oiov5RsBh4etTkjpDEeLgv-1psQbRIcFNGWG9GOenQ%3AAQzYpw4dcUwNbZ-jS8XzO4RVnsDLhdv8r6q8xpJ4W7cPXA&__user=100025733181366&__a=1&__dyn=7AgNe-4am2d2u6aJGeFxqewRyWzEpF4Wo8ovxGdwIhE98nwgUaoepovGbwSwIK7EiwXwgUOdwJx61jDxicxu1Zxa2m4o6e2fwmWwaWu0LVEtxy5Urwr8lwHx-2K1KxO4Wx21Ox28xa4oC2bwEBUjUeoOGyo8U8Kq0YEuzHAy85iaxa3u4UO68pwAwhVKcxp2Utwwwi8y&__req=h&__be=1&__pc=PHASED%3Aufi_home_page_pkg&dpr=1&__rev=4745726&jazoest=28113&__spin_r=4745726&__spin_b=trunk&__spin_t=1549529577&total_count=98&ft_ent_identifier={}".format(2521 + randint(-300, 300), 7443 + randint(-500, 500), post_id)


    driver.get(likes_url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
  
    js = json.loads(str(soup.text)[9::])

    html = js['domops'][0][3]['__html']
    soup = BeautifulSoup(html, 'html.parser')

    user_soups = soup.find_all(attrs={'data-gt': re.compile('.+"engagement".+"eng_src":"2".+')})
    
    likes = []
    for user_soup in user_soups:
        user_json = json.loads(user_soup['data-gt'])
        user_id = user_json['engagement']['eng_tid']

        user_url = user_soup['href']
        if "profile.php" in user_url:
            nickname = user_id
        else:
            nickname = user_url.split('?')[0][user_url.find("com/") + len("com/")::]

        users_dict[nickname] = user_id
        temp = {"user_id": user_id, "nickname": nickname}

        likes.append(temp)

    liked = {"count": len(likes), "content": likes}

    return liked

def get_nickname_soup(i):
    body = i.find(attrs={'data-sigil': "comment-body"})
    nickname_soup = body.previousSibling

    if nickname_soup:
        pass
    else:
        nickname_soup = body

    return nickname_soup

def get_nickname(i):

    nickname_soup = get_nickname_soup(i)

    profile_href =  nickname_soup.a['href']
    nickname = profile_href[1::].split('?', 1)[0]

    if nickname == "profile.php":
        nickname = profile_href[profile_href.find('id=') + 3:profile_href.find('&'):]

    return nickname

def get_content(i):
    body = i.find(attrs={'data-sigil': "comment-body"})
    nickname_soup = body.previousSibling

    if nickname_soup:
        content = body.text
    else:
        content = "Sticker or Photo or Video"

    return content

def get_page_comments(page_url: str) -> list:

    driver.get(page_url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    global users_dict

    comments = []
    for i in soup.find_all(attrs={'data-sigil': "comment"}):
        temp = {}
        nickname = get_nickname(i)
        content = get_content(i)
        like_count = i.find(attrs={"href": re.compile("/ufi/reaction/profile/browser/?.+")}).text

        if like_count:
            like_count = like_count.strip()
        else:
            like_count = "0"

        user_id = users_dict.get(nickname)

        if user_id is None:
          user_id = -1

        content = get_content(i)
        temp["user_nickname"] = nickname
        temp["user_id"] = user_id
        temp["content"] = content
        temp["like_count"] = like_count

        comments.append(temp)
    return comments

def get_commented(post_url: str) -> list:
    magic_comments_url = 'https://m.facebook.com/story.php?id=4&refid=52&story_fbid='

    if "view=permalink" in post_url:
        if "&p=" not in post_url:
            post_url = post_url + "&p="
        post_url = post_url.replace("www.facebook", "m.facebook").replace("web.facebook", "m.facebook")

    elif "/groups/" in post_url:
        s = post_url.split('/groups/', 1)[1]

        post_id = get_post_id(post_url)
        group_id = s.split('/')[0]

        post_url = 'https://m.facebook.com/groups/{}?view=permalink&refid=18&id={}&p='.format(group_id, post_id)
    elif "permalink.php?" in post_url or "story.php?" in post_url or "photo.php?" in post_url:
        if "&p=" not in post_url:
            post_url = post_url + "&p="
    elif "/videos/" in post_url:
        post_id = get_video_post_id(post_url)
        post_url = magic_comments_url + get_post_id(post_url) + "&p="
    else:
        post_url = magic_comments_url + get_post_id(post_url) + "&p="

    all_comments = []
    ok = True
    i = 0
    while ok:
        page_url = post_url + str(i)
        temp = get_page_comments(page_url)

        all_comments += temp

        if len(temp) < 29:
            break
        else:
            i += 30

    comments_dict = {"count": len(all_comments), "content": all_comments}
    return comments_dict


def open_link_under_symbian(url):
    driver.execute_script("window.open('{}')".format(url))
    # WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument('disable-infobars')
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/14.14263")
    

    driver.get(url)
    return driver.page_source

def get_shared(url):
    magic_shares_url = "https://m.facebook.com/shares/view?id="
    #
    #
    #
    #
    # login(email='79103443074', password='Zcca12Qwdzf', is_symbian=True)
    #
    #
    #
    #
    #

    post_id = get_post_id(url)

    url = magic_shares_url + post_id

    driver.get(url)
    html = driver.page_source

    soup =BeautifulSoup(html, 'html.parser')
    soup.prettify()

    shares_list = soup.find_all(id='m_story_permalink_view')
    
    shares_count = len(shares_list)


    shares_trunk = []
    for element in shares_list:
        temp = {}

        t = element.find(attrs={'data-ft': re.compile(".+content_owner_id_new.+")})
        jsonData = json.loads(t["data-ft"])
        
        user_id = jsonData["content_owner_id_new"]
        share_id = jsonData["top_level_post_id"]

        temp["user_id"] = user_id
        temp["share_id"] = share_id
        shares_trunk.append(temp)

    shares_dict = {"count": shares_count, "content": shares_trunk}

    return shares_dict

def scrap(url: str) -> dict:
    """ Scraping url """
    
    data = {}
    post_id = get_post_id(url)

    temp = {"url": url}

    liked = get_liked(url)

    comments = get_commented(url)

    shared = get_shared(url)

    temp["post_id"] = post_id
    temp["comments"] = comments
    temp["likes"] = liked
    temp["shares"] = shared

    data['data'] = temp

    return data

def main():
    login(email='79103443074', password='Zcca12Qwdzf')
    # 'https://m.facebook.com/groups/497617433710914?view=permalink&id=1311718185634164&refid=18&__tn__=-R'
    # 'https://m.facebook.com/groups/497617433710914?view=permalink&id=1311718185634164&refid=18&__tn__=-R'

    # Вставьте сюда ссылку на пост:
    post_url = 'https://m.facebook.com/groups/497617433710914?view=permalink&id=1311718185634164&refid=18&__tn__=-R'

    data = scrap(post_url)

    filename = get_post_id(post_url) + ".json"
    with open(filename, 'w', encoding='utf-8') as jsonfile:
       json.dump(data, jsonfile)

    print(data)

    driver.close()
    driver.quit()


if __name__ == '__main__':
    main()

# 79853381759   Xvbbg5ERtfgz - забаненный бот