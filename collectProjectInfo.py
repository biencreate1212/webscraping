import requests
import sys
import re
from bs4 import BeautifulSoup

# ↓スクレピング対象のURL初期化↓
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

# ↑スクレピング対象のURL初期化↑

# ↓Httpリクエスト発行↓

# リクエスト発行時に設定するヘッダー情報
headers = { "User-Agent": "Mozilla/5.0  (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}

# 案件情報格納用クラス
class ProjectInfo:
    projectName = ""
    link = ''
    price = ''
    applyTerm = ''
    workPeriod = ''
    programLanguage = ''

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

        # ループの終了条件を変更
        tmpSoup = soup.find('a', class_='pager__item__anchor')


        print(dictionaryToReturn)

        for item in dictionaryToReturn:
            print(dictionaryToReturn[item].projectName)
            print(dictionaryToReturn[item].price)
            print(dictionaryToReturn[item].link)
            print(dictionaryToReturn[item].applyTerm)
            print(dictionaryToReturn[item].programLanguage)
            print('\n' + 'ZZZZZZZZZZZZZZZ' + '\n')

        sys.exit()
        # TODO: Web・システム開発に関しては成功。あとはwhileが正しく回るように修正する

        if tmpSoup is not None:
            # targetUrlの更新処理
            href = tmpSoup.get('href')
            targetUrl = baseUrl + href
            isNextFound = True
        else:
            isNextFound = False



    return dictionaryToReturn


tmp = []
for item in urlList:
    arrayClass = getProjectInfo(item, headers)
    for key in array:
        tmp.append(array[key])

print()

# ↑Httpリクエスト発行↑

# ↓取得したHTMLから必要な情報を抜き出し整理↓

# 1.「classにc-media-list__item c-media」が含まれているdivを取得
#       ページが複数ある場合は、ページ分繰り返す
#       タグ=「初心者OK」の案件のみ
#
# 2. 1.で集まった情報から、以下を抽出
#    案件名、値段、募集期間、取引期間、開発言語(あれば)


### 案件名取得メソッドの定義
### tag="span", かつclass="c-media__title-inner"のものを検索し、li要素を除いて返却
def getProjectNameForLancers (soup):

    # 案件名の取得
    projectNameHTMLWithli = soup.find("span", class_="c-media__title-inner")

    # 取得したHTMLからli要素を削除
    liToDelete = projectNameHTMLWithli.li
    liToDelete.decompose()

    return projectNameHTMLWithli.get_text().strip()

# 案件名の取得
projectName = getProjectNameForLancers (soupLancers)

# メモ
# ランサーズ
# カテゴリ: Web・システム開発、スマホアプリモバイル開発、アプリケーション開発、業務システムツール開発
# 検索条件: タグ=初心者OK、
# 欲しい情報: 案件名、値段、募集期間、取引期間、開発言語

if len(projectName) > 0:
    print(projectName)

#2020/12/9

# ★必要な情報を閲覧するためのHTMLを作成★

sys.exit()

for item in newsHeadings:
    print(item)
