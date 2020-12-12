import requests
import sys
import re
import webbrowser
from bs4 import BeautifulSoup
from jinja2 import Template, Environment, FileSystemLoader

'''
スクレピング対象のURL初期化
'''
# システム開発・運用URL (ベースURL)
lancersBaseUrl = 'https://www.lancers.jp/work/search/system'
# キーワード=初心者OK
lancersQueryCondition = '?sort=deadlined&show_description=1&work_rank%5B%5D=3&work_rank%5B%5D=2&work_rank%5B%5D=0&budget_from=&budget_to=&search=%E6%A4%9C%E7%B4%A2&keyword=%E5%88%9D%E5%BF%83%E8%80%85OK&not='
# ランサーズのURL(Web・システム開発)
lancersWebSystemAlias = 'development'
# ランサーズのURL(スマホアプリモバイル開発)
lancersSmartPhoneAlias = 'smartphoneapp'
# ランサーズのURL(アプリケーション開発)
lancersAppDevAlias = 'app'
# ランサーズのURL(業務システムツール開発)
lancersEnterpriseToolAlias = 'tool'

# URLを配列に格納
urlList = []
aliasList = [lancersWebSystemAlias, lancersSmartPhoneAlias, lancersAppDevAlias, lancersEnterpriseToolAlias]
for item in aliasList:
    urlList.append(lancersBaseUrl + "/" + item + lancersQueryCondition)

'''
Httpリクエスト発行
'''
# リクエスト発行時に設定するヘッダー情報
headers = { "User-Agent": "Mozilla/5.0  (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
# 案件情報格納用クラス
class ProjectInfo:
    projectName = ''
    link = ''
    price = ''
    applyTerm = ''
    programLanguage = '未定/希望なし'

# 対象のURLからHTMLを取得し、「次へ」ボタンがページにある間、処理を繰り返す
def getProjectInfo(url, headers):

    # 「次へ」がそのページにあるかどうか
    isNextFound = True
    # スクレイピング対象のURL
    targetUrl = url
    # 基本となるURL(ランサーズ)
    baseUrl = 'https://www.lancers.jp'
    # 返却用連想配列　
    dictionaryToReturn = {}

    while isNextFound:

        # 引数のURLからHTMLを取得
        response = requests.get(url=targetUrl, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        projectList = soup.find_all("div", onclick=re.compile('goToLjp.*'))

        # 情報の格納
        for item in projectList:

            # 仕事詳細ページのリンクを作成
            href = item.find('a', class_='c-media__title').get('href')
            innerUrl = baseUrl + href
            innerResponse = requests.get(url=innerUrl, headers=headers)
            innerSoup = BeautifulSoup(innerResponse.text, "html.parser")

            # 案件情報をクラスに格納
            projectInfo = ProjectInfo()
            soupProjectName = item.find('span', class_='c-media__title-inner')
            liInSoupProjectName = soupProjectName.find('li', class_='c-media__job-tag c-media__job-tag--inexperiencedCount')
            if liInSoupProjectName is not None:
                liInSoupProjectName.decompose()

            projectInfo.projectName = soupProjectName.get_text().strip()
            projectInfo.price = item.find('span', class_='c-media__job-price').get_text().strip().replace('\n', '')
            projectInfo.link = innerUrl
            projectInfo.applyTerm = innerSoup.find('p', class_='worksummary__text').get_text().strip()

            tableKeyList = innerSoup.find_all('dl', class_='c-definitionList definitionList--holizonalA01')
            for item in tableKeyList:
                tmp = item.find('dt', class_="definitionList__term").get_text().strip()
                if tmp == '希望開発言語':
                    projectInfo.programLanguage = item.find('dd', class_="definitionList__description").get_text().strip()

            dictionaryToReturn[projectInfo.projectName] =  projectInfo

        # 「次へ」がページにある場合、次のページに遷移し、ループする
        nextButtonHTML = soup.find('span', class_='pager__item pager__item--next')
        if nextButtonHTML is not None:
            # targetUrlの更新処理
            nextPageUrl = nextButtonHTML.a.get('href')
            targetUrl = baseUrl + nextPageUrl
            isNextFound = True
        else:
            isNextFound = False

    return dictionaryToReturn

# 対象の4サイトから取得した情報を1つの配列にまとめる
projectInfoArray = {}
for item in urlList:
    arrayClass = getProjectInfo(item, headers)
    for key in arrayClass:
        projectInfoArray[key] = arrayClass[key]

'''
for item in projectInfoArray:
    print(projectInfoArray[item].projectName)
    print(projectInfoArray[item].link)
    print(projectInfoArray[item].price)
    print(projectInfoArray[item].applyTerm)
    print(projectInfoArray[item].programLanguage)
    print('\n')

sys.exit()
'''

'''
必要な情報を閲覧するためのHTMLを作成
'''

# テンプレートファイルの読み込み
env = Environment(loader = FileSystemLoader('./', encoding='utf-8'))
template = env.get_template('template.j2')

# templateからHTMLを作成
renderedHTML = template.render({'projectInfo': projectInfoArray})

# 作成したHTMLでファイルを作成
htmlFilePath = '/Users/Koichi/Private/WorkHelp/Webscraping/freelanceProjectForBeginners.html'
with open(htmlFilePath, mode='w') as file:
    file.write(renderedHTML)

# 作成されたHTMLファイルを開く
localPath = 'file://' + htmlFilePath
webbrowser.open_new_tab(localPath)
