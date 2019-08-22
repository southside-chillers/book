#!/usr/bin/env python3
import json
import io
import os
import shutil
import glob
import re


RE_EMOJI = re.compile('[\U00010000-\U0010ffff]|⚔', flags=re.UNICODE)


def convert_file(filename):
    jsonblob = io.StringIO()
    markdownblob = io.StringIO()
    with open(filename) as f:
        while True:
            line = f.readline()
            jsonblob.write(line)
            if line.strip() == "}" or line is None:
                break
        markdownblob.write(f.read())

    jsonblob.seek(0)
    markdownblob.seek(0)
    metadata = json.load(jsonblob)

    chapter = metadata['chapter']
    if isinstance(chapter, str):
        chapter = chapter.replace(':', '_').replace(' ', '_')

    with open(f'output/md/{chapter}.md', 'w') as out:
        markdown = markdownblob.read()
        # postprocess markdown
        markdown = RE_EMOJI.sub("", markdown)
        markdown.rstrip("- \n")
        out.write(markdown)

    os.system(f"pandoc -o output/tex/{chapter}.tex output/md/{chapter}.md")

    # post-process markdown
    texfilename = f"output/tex/{chapter}.tex"
    with open(texfilename) as f:
        text = f.read()

    prepend = f"\chapter{{{metadata['title']}}}\n\chapdesc{{{metadata['description']}}}\n"
    with open(texfilename, "w") as f:
        f.write(prepend + "\n" + text)


def convert():
    os.makedirs("output/md")
    os.makedirs("output/tex")

    for ch in glob.glob("southside.chillers.online/southside/content/chapters/*.md"):
        if "_index" in ch:
            continue
        print(ch)
        convert_file(ch)


def build():
    chapters = list(range(1, 26)) + ["26__Part_I", "26__Part_II"] + list(range(27, 40))
    frontmatter = open("book-frontmatter.tex").read()
    body = "\n\n".join(open(f"output/tex/{c}.tex").read() for c in chapters)
    backmatter = """\n\end{document}"""
    with open("master.tex", "w") as f:
        f.write(frontmatter)
        f.write(body)
        f.write(backmatter)
    os.system("tectonic master.tex")


def clean():
    try:
        shutil.rmtree("output/")
    except FileNotFoundError:
        pass

def main():
    clean()
    convert()
    build()

if __name__ == "__main__":
    main()
