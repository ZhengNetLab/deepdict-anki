import csv
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

BASE = Path(__file__).resolve().parent

# 从脚本所在目录加载 .env（不受当前工作目录影响）
load_dotenv(BASE / ".env")

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

SYSTEM = (
    "德汉词典。德语译中文，中文译德语。纯文本输出，不用任何Markdown符号。"
    "单词：一行释义，名词加冠词和复数，动词加过去式和过去分词，其他词性不加任何额外信息，最后附一个短例句及中文。"
    "句子：只输出译文。"
)

# ---------- Anki 导出 ----------
ANKI_FILE = BASE / "anki" / "deepdict.txt"
ANKI_HEADER = (
    "#separator:tab\n"
    "#html:true\n"
    "#notetype:Basic\n"
    "#deck:Deutsch::Deepdict\n"
    "#tags column:3\n"
)


def is_sentence(text):
    """粗略判断：有句末/句中标点、德语超过 3 个词、或中文超过 8 个字，就当作句子。"""
    if re.search(r"[.!?,;:。！？，；：]", text):
        return True
    if len(text.split()) > 3:
        return True
    if len(re.findall(r"[一-鿿]", text)) > 8:
        return True
    return False


def load_saved_fronts():
    if not ANKI_FILE.exists():
        return set()
    with ANKI_FILE.open(encoding="utf-8", newline="") as f:
        lines = (line for line in f if not line.startswith("#"))
        return {row[0] for row in csv.reader(lines, delimiter="\t") if row}


def save_to_anki(query, result, saved):
    """把单词查询追加到 Anki 文件；句子和重复项跳过。"""
    query = " ".join(query.split())
    result = result.strip()
    if not result or is_sentence(query) or query in saved:
        return
    back = "<br>".join(line.strip() for line in result.splitlines() if line.strip())
    back = back.replace("\t", " ")
    ANKI_FILE.parent.mkdir(exist_ok=True)
    new_file = not ANKI_FILE.exists()
    with ANKI_FILE.open("a", encoding="utf-8", newline="") as f:
        if new_file:
            f.write(ANKI_HEADER)
        csv.writer(f, delimiter="\t", lineterminator="\n").writerow(
            [query, back, "deepdict"]
        )
    saved.add(query)


# ---------- 翻译 ----------
def translate(text):
    r = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": text}],
        temperature=0.3,
    )
    return r.choices[0].message.content


def lookup(text, saved):
    # 去掉 BOM（PowerShell 管道或某些复制来源会带上），避免空查询被发出和保存
    text = text.replace("\ufeff", "").strip()
    if not text:
        return
    result = translate(text)
    print(result)
    try:
        save_to_anki(text, result, saved)
    except OSError as e:
        print(f"(Anki 保存失败: {e})", file=sys.stderr)


saved = load_saved_fronts()

if len(sys.argv) > 1:
    lookup(" ".join(sys.argv[1:]), saved)
else:
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if q:
            lookup(q, saved)
