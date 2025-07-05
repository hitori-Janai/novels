import re
import sys

if len(sys.argv) != 2:
    print("Usage: python extract_chapter.py <chapter_number>")
    sys.exit(1)

chapter_number = int(sys.argv[1])

text = open('D:/workspace/js/novels/books/oap_en/cn/cn.txt', 'r', encoding='utf-8').read()

start_pattern = f'第{chapter_number}章'
end_pattern = f'第{chapter_number + 1}章'

match = re.search(f'({start_pattern}.*?){end_pattern}', text, re.DOTALL)

if match:
    chapter_text = match.group(1).strip()
    output_filename = f'D:/workspace/js/novels/books/oap_en/{chapter_number:04d}.txt'
    open(output_filename, 'w', encoding='utf-8').write(chapter_text)
else:
    print(f'Chapter {chapter_number} not found')
