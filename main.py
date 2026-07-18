from openai import OpenAI
from dotenv import load_dotenv

from readPDF import read_pdf_text

load_dotenv()

client = OpenAI()


def read_txt_file(txt_path: str) -> str:
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()


# 向用户询问使用 txt 还是 pdf 导入
file_type = input("请选择导入的文件类型（1: txt，2: pdf，默认 1）：").strip()

if file_type == "2":
    pdf_path = input("请输入要读取的 pdf 文件路径（默认 report.pdf）：").strip()
    if not pdf_path:
        pdf_path = "report.pdf"
    document = read_pdf_text(pdf_path)
else:
    txt_path = input("请输入要读取的 txt 文件路径（默认 conflict.txt）：").strip()
    if not txt_path:
        txt_path = "conflict.txt"
    document = read_txt_file(txt_path)

prompt = f"""
你是一个文档分析助手。
请根据下面的文档，分析文档中的内容。

要求：
1. 总结文档中的主要内容
2. 提取文档中的关键信息
3. 分析文档中的问题和解决方案
4. 不要编造文档中没有的信息

必须以markdown格式输出。
文档：
{document}
"""

response = client.responses.create(
    model="gpt-5",
    input=prompt
)

output_text = response.output_text

# 让用户选择输出方式：打印、保存为 txt，或两者都要
output_type = input(
    "请选择输出方式（1: 打印到屏幕，2: 保存为 txt，3: 同时打印+保存，默认 1）："
).strip()

if output_type in ("2", "3"):
    save_path = input("请输入保存的 txt 文件路径（默认 report_output.txt）：").strip()
    if not save_path:
        save_path = "report_output.txt"
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"已保存到：{save_path}")

if output_type != "2":
    print(output_text)