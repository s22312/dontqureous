import json
import requests
import datetime

ENABLE_DPRINT = not False
dprint = lambda *a: print(*a) if ENABLE_DPRINT else None

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
        print(c, "個のワークブックが利用可能です") if c != 0 else print("利用可能なワークブックはありません", c)
        dprint(res.status_code, res.text)

    def do_all(self) -> None: #todo add leaning things
        print("ワークブックを取得中")
        workbooks = self.get_workbooks()
        _workbook_dones = [workbook["workbook_name"] for workbook in workbooks if workbook["is_finished"]]
        for workbook in workbooks:
            print(workbook["workbook_name"], "を処理中")
            if workbook["is_finished"] or workbook["workbook_name"] in _workbook_dones:
                print(workbook["workbook_name"], "は既に完了しています")
            else:
                self.start_action()
                self.do_workbook(workbook)
                #self.end_workbook()
                if not workbook["workbook_name"] in _workbook_dones: _workbook_dones.append(workbook["workbook_name"])
                print(workbook["workbook_name"], "を処理しました")

        print("復習問題を取得中")
        review = self.get_review()
        if review["next_question"] == "finish":
            print("復習問題は既に完了しています")
        else:
            print("復習問題を処理中")
            self.start_action(f2=False)
            self.do_review(review)

    def start_action(self, f1: bool = True, f2: bool = True) -> None:
        if f1:
            res = self.session.post(
                "https://api-from-202204.kcat.qureous.com/api/v7/student_settings/",
                json={
                    "play_launched": True
                }
            )
            dprint(res.status_code, res.text)
        if f2:
            res = self.session.post(
                "https://api-from-202204.kcat.qureous.com/api/v7/student_settings/",
                json={
                    "basic_played": True
                }
            )
            dprint(res.status_code, res.text)

    def get_workbooks(self) -> list[dict]:
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v7/workbooks/" + self.info["uuid"] + "/?state=0")
        dprint(res.status_code, res.text)
        j = res.json()
        return j

    def do_workbook(self, workbook: dict) -> None:
        #date = date
        date = "0001/01/01 00:00:00.0000"
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v6/questions/current/workbook/" + self.info["uuid"] + "/" + str(workbook["workbook_id"]) + "/")
        dprint(res.status_code, res.text)
        j = res.json()
        res = self.session.get("https://api-from-202204.kcat.qureous.com/api/v7/workbooks/" + str(workbook["workbook_id"]) + "/lock_status/" + self.info["uuid"] + "/")
        dprint(res.status_code, res.text)
        for i in range(workbook["number_of_questions"] - workbook["number_of_answers"]):
            res = self.session.post(
                "https://api-from-202204.kcat.qureous.com/api/v6/questions/next/",
                json={
                    "uuid": self.info["uuid"],
                    "question": j["question_num"],
                    "answer": [{
                        "correct": 1,
                        "column_no": index+1,
                        "answer": a["answers"][0]["answer"]
                    } for index, a in enumerate(j["answer_column"])] if len(j["answer_column"]) > 1 else [a["answers"][0]["answer"] for a in j["answer_column"]],
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
                    "date": date,
                    "workbook_id": workbook["workbook_id"],
                    "activity_log": [
                        {
                            "activity": "QuestionStart",
                            "time": date
                        },
                        {
                            "activity": "AnswerTap",
                            "time": date
                        },
                        {
                            "activity": "ModelAnswerShow",
                            "time": date
                        },
                        {
                            "activity": "ModelAnswerOk",
                            "time": date
                        }
                    ]
                }
            )
            dprint(res.status_code, res.text)
            print("ok", workbook["number_of_answers"] + i + 1, "/", workbook["number_of_questions"], end="\r")
            j = res.json()
        else:
            dprint(res.status_code, res.text)

    def get_review(self) -> dict:
        res = self.session.get("https://api-from-202204.kcat.qubena.com/db/getsections/home/" + self.info["uuid"] + "/")
        dprint(res.status_code, res.text)
        j = res.json()
        return j

    def do_review(self, review: dict) -> None:
        date = "0001/01/01 00:00:00.0000"
        res = self.session.get("https://api-from-202204.kcat.qubena.com/api/v5/questions/current/home/" + review["next_question"] + "/" + self.info["uuid"] + "/")
        dprint(res.status_code, res.text)
        j = res.json()
        while j["question_num"] not in ["end", "clear"]:
            res = self.session.post(
                "https://api-from-202204.kcat.qureous.com/api/v6/questions/next/",
                json={
                    "uuid": self.info["uuid"],
                    "question": j["question_num"],
                    "answer": [json.dumps({
                        "correct": 1,
                        "column_no": index+1,
                        "answer": a["answers"][0]["answer"]
                    }) for index, a in enumerate(j["answer_column"])] if len(j["answer_column"]) > 1 else [a["answers"][0]["answer"] for a in j["answer_column"]],
                    "correct": "1",
                    "time": "50000", #idk
                    "section": j["section"],
                    "subsection": j["subsection"],
                    "mode": "home",
                    "session_id": j["session_id"],
                    "trans_type": j["trans_type"],
                    "is_reviewing": True,
                    "wrong_count": "-1",
                    "category": j["category"],
                    "date": date,
                    "activity_log": [
                        {
                            "activity": "QuestionStart",
                            "time": date
                        },
                        {
                            "activity": "AnswerTap",
                            "time": date
                        },
                        {
                            "activity": "ModelAnswerShow",
                            "time": date
                        },
                        {
                            "activity": "ModelAnswerOk",
                            "time": date
                        }
                    ]
                }
            )
            dprint(res.status_code, res.text)
            print("ok", (j["total_question_amount"] - j["current_question_index"]) + 1, "/", j["total_question_amount"], end="\r")
            j = res.json()
        else:
            review = self.get_review()
            if review["next_question"] not in ["end", "clear"]:
                self.do_review(review)

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        j = json.load(f)
    processor = Processor(j["username"], j["password"])
    processor.do_all()
    print("All-Done")

if __name__ == "__main__":
    main()