import json
import requests.session

class Processor:
    def __init__(self) -> None:
        self.session = requests.session()

    def do_all(self) -> None:
        raise NotImplementedError()

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        j = json.load(f)
    processor = Processor()
    processor.do_all()

if __name__ == "__main__":
    main()