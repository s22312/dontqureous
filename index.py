import json
import requests.session

class Processor:
    def __init__(self, email: str, password: str) -> None:
        self.session = requests.session()
        self.authorize(email, password)

    def authorize(self, email: str, password: str) -> None:
        raise NotImplementedError()
        self.session.headers = {}

    def do_all(self) -> None:
        raise NotImplementedError()

    def get_workbooks(self) -> list[dict]:
        raise NotImplementedError()

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        j = json.load(f)
    processor = Processor()
    processor.do_all()

if __name__ == "__main__":
    main()