import json
import requests
import datetime

ENABLE_DPRINT = False
if ENABLE_DPRINT: dprint = lambda *a: print(*a)
else: dprint = lambda *a: None

class Processor:
    def __init__(self, username: str, password: str) -> None:
        self.session = requests.session()
        self.workbooks_config = {}
        self.info = {}
        self.initialize(username, password)
        self.session.headers = {
            "User-Agent": "Qubena Kawai/1.0 (00000000.0000000000000; build:0; Windows.Desktop 10.0.10000.0000/Unknown)",
            "Cache-Control": "no-cache",
            "uuid": self.info["uuid"]
        }

    def initialize(self, username: str, password: str) -> None:
        res = self.session.post(
            "https://api-from-202204.kcat.qureous.com/api/v7/students/customize_type/",
            json={
                "username": username
            }
        )
        dprint(res.status_code, res.text)
        res = self.session.post(
            "https://api-from-202204.kcat.qureous.com/api/v5/students/login/",
            json={
                "username": username,
                "password": password,
                "appid": "zLeYTK8S5kJC5bjT"
            }
        )
        dprint(res.status_code, res.text)
        j = res.json()
        self.info.update(j)
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v7/workbooks/config/" + self.info["uuid"] + "/")
        dprint(res.status_code, res.text)
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v7/workbooks/unread_count/" + self.info["uuid"] + "/")
        c = res.json()["count"]
        if c != 0: print(c, "個のワークブックが利用可能です")
        dprint(res.status_code, res.text)

    def do_all(self) -> None:
        workbooks = self.get_workbooks()
        for workbook in workbooks:
            print(workbook["workbook_name"], "を処理中")
            if workbook["is_finished"]:
                print(workbook["workbook_name"], "は既に完了しています")
            else:
                self.start_workbook()
                self.do_workbook(workbook)
                #self.end_workbook()
                print(workbook["workbook_name"], "を処理しました")

    def get_workbooks(self) -> list[dict]:
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v7/workbooks/" + self.info["uuid"] + "/?state=0")
        dprint(res.status_code, res.text)
        j = res.json()
        return j

    def start_workbook(self) -> None:
        res = self.session.post(
            "https://api-from-202204.kcat.qureous.com/api/v7/student_settings/",
            json={
                "play_launched": True
            }
        )
        dprint(res.status_code, res.text)
        res = self.session.post(
            "https://api-from-202204.kcat.qureous.com/api/v7/student_settings/",
            json={
                "basic_played": True
            }
        )
        dprint(res.status_code, res.text)

    def do_workbook(self, workbook: dict) -> None:
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v6/questions/current/workbook/" + self.info["uuid"] + "/" + str(workbook["workbook_id"]) + "/")
        dprint(res.status_code, res.text)
        j = res.json()
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v7/workbooks/" + str(workbook["workbook_id"]) + "/lock_status/" + self.info["uuid"] + "/")
        dprint(res.status_code, res.text)
        for i in range(workbook["number_of_questions"]-workbook["number_of_answers"]):
            res = self.session.post(
                "https://api-from-202204.kcat.qureous.com/api/v6/questions/next/",
                json={
                    "uuid": self.info["uuid"],
                    "question": j["question_num"],
                    "answer": [a["answers"][0]["answer"] for a in j["answer_column"]],
                    "correct": "1",
                    "time": "50000", #idk
                    "section": j["section"],
                    "subsection": j["subsection"],
                    "mode": "workbook",
                    "session_id": j["session_id"],
                    "trans_type": j["trans_type"],
                    "is_reviewing": "False",
                    "wrong_count": "-1",
                    "category": j["category"],
                    "date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-2],
                    "workbook_id": workbook["workbook_id"],
                    "activity_log": [
                        {
                            "activity": "QuestionStart",
                            "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-2]
                        },
                        {
                            "activity": "AnswerTap",
                            "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-2]
                        },
                        {
                            "activity": "ModelAnswerShow",
                            "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-2]
                        },
                        {
                            "activity": "ModelAnswerOk",
                            "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-2]
                        }
                    ]
                }
            )
            dprint(res.status_code, res.text)
            print("ok", workbook["number_of_answers"] + i + 1, "/", workbook["number_of_questions"], end="\r")
            j = res.json()
        else:
            dprint(res.status_code, res.text)

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        j = json.load(f)
    processor = Processor(j["username"], j["password"])
    processor.do_all()

if __name__ == "__main__":
    main()