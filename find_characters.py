import os
import re

def find_characters_in_chapter(file_path):
    """
    Finds all unique characters in a given chapter file.
    Characters are identified by the pattern [[id character emotion]].
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # The pattern looks for [[ followed by digits, a space, the character name (captured), another space, and more text, ending with ]]
            matches = re.findall(r'\[\[\d+ (\S+) \w+\]\]', content)
            unique_characters = sorted(list(set(matches)))
            return unique_characters
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")
        return []

def main():
    """
    Main function to iterate through chapter files and print characters.
    """
    book_dir = 'books/oap_en/'
    files = sorted([f for f in os.listdir(book_dir) if f.endswith('.txt')])

    for filename in files:
        chapter_path = os.path.join(book_dir, filename)
        characters = find_characters_in_chapter(chapter_path)
        if characters:
            print(f"Characters in {filename}:")
            for character in characters:
                print(f"- {character}")
            print("-" * 20)

if __name__ == '__main__':
    main() 