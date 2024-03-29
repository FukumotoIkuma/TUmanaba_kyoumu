from account import USER_NAME,PASSWORD

import requests
from bs4 import BeautifulSoup

class TU(object):
    def __init__(self, user, password):
        #sessionを開始。cookieを自分で操作して同様の処理をすることも可能
        #dartによる実装を以前行ったので、そのレポジトリが参考になるかもしれない
        self.session = requests.Session()
        self.user = user
        self.password = password
        self.log_index = 1

    def main(self):
        self._login_manaba()
        self._login_kyoumu()

    def _login_manaba(self):
        #ログインページの基底サイトにアクセス。
        response_1 = self.session.get(
            url="https://manaba.lms.tokushima-u.ac.jp/ct/home_course"
            )
        
        #リダイレクトされる
        print(f"redirect:{response_1.history}")
        print(f"current url:{response_1.url}")
        print(f"cookies:{response_1.cookies}")
        print("\n")

        self._logger(response_1)

        #ログイン処理
        response_2 = self.session.post(
                url=response_1.url,
                data={
                    "j_username": self.user,
                    "j_password": self.password,
                    "_eventId_proceed":""
                    
                }
            )

        self._logger(response_2)


    def _login_kyoumu(self):
        #直接時間割のページに行くことはできなかった。
        #このページで認証情報が生成されるっぽい
        #response3はjs駆動のため、スクリプトでは能動的同じことをする
        response_3 = self.session.get(
            url = "https://eweb.stud.tokushima-u.ac.jp/Portal/shibboleth_login.aspx"
        )
        self._logger(response_3)


        #HTMLファイルを解析し、認証情報を取り出す
        res3_soup = BeautifulSoup(response_3.content,"html.parser")
        info = res3_soup.findAll("input")
        RelayState = info[0]["value"]
        SAMLResponse=info[1]["value"]

        #認証情報をもとに、教務システムにログインする
        #（リダイレクトを能動的に行う）
        response_4 = self.session.post(
            url = "https://eweb.stud.tokushima-u.ac.jp/Shibboleth.sso/SAML2/POST",
            data={
                "RelayState":RelayState,
                "SAMLResponse":SAMLResponse
                }
            )
        self._logger(response_4)

        #ログイン完了したので、自由にスクレイピング可能。今回は時間割
        response_5 = self.session.get("https://eweb.stud.tokushima-u.ac.jp/Portal/StudentApp/Regist/RegistList.aspx")
        self._logger(response_5) 

    def _logger(self,response):
        with open(f'output{self.log_index}.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        self.log_index +=1

def main():
    tu = TU(USER_NAME,PASSWORD)
    tu.main()
if __name__ == "__main__":
    main()