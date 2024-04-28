import argparse
import asyncio
import concurrent.futures
import os
import re
import subprocess
import warnings


from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import edge_tts
from mutagen import mp4
#import nltk
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment

warnings.filterwarnings("ignore", module="ebooklib.epub")

def chap2text_epub(chap):
    blacklist = [
        "[document]",
        "noscript",
        "header",
        "html",
        "meta",
        "head",
        "input",
        "script",
    ]
    paragraphs = []
    soup = BeautifulSoup(chap, "html.parser")

    # Extract chapter title (assuming it's in an <h1> tag)
    chapter_title = soup.find("h1")
    if chapter_title:
        chapter_title_text = chapter_title.text.strip()
    else:
        chapter_title_text = None

    # Always skip reading links that are just a number (footnotes)
    for a in soup.findAll("a", href=True):
        if not any(char.isalpha() for char in a.text):
            a.extract()

    chapter_paragraphs = soup.find_all("p")
    for p in chapter_paragraphs:
        paragraph_text = "".join(p.strings).strip()
        paragraphs.append(paragraph_text)

    return chapter_title_text, paragraphs

def export(book, sourcefile):
    book_contents = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapter_title, chapter_paragraphs = chap2text_epub(item.get_content())
            book_contents.append({"title": chapter_title, "paragraphs": chapter_paragraphs})
    outfile = sourcefile.replace(".epub", ".txt")
    check_for_file(outfile)
    print(f"Exporting {sourcefile} to {outfile}")
    author = book.get_metadata("DC", "creator")[0][0]
    booktitle = book.get_metadata("DC", "title")[0][0]

    with open(outfile, "w") as file:
        file.write(f"Title: {booktitle}\n")
        file.write(f"Author: {author}\n\n")
        for i, chapter in enumerate(book_contents, start=1):
            if chapter["paragraphs"] == [] or chapter["paragraphs"] == ['']:
                continue
            else:
                if chapter["title"] == None:
                    file.write(f"# Part {i}\n")
                else:
                    file.write(f"# {chapter['title']}\n\n")
                for paragraph in chapter["paragraphs"]:
                    file.write(f"{paragraph}\n\n")

def get_book(sourcefile):
    book_contents = []
    book_title = sourcefile
    book_author = "Unknown"
    chapter_titles = []
    with open(sourcefile, "r", encoding="utf-8") as file:
        current_chapter = {"title": None, "paragraphs": []}
        lines_skipped = 0
        for line in file:
            if lines_skipped < 2 and (line.startswith("Title") or line.startswith("Author")):
                lines_skipped += 1
                if line.startswith('Title: '):
                    book_title = line.replace('Title: ', '').strip()
                elif line.startswith('Author: '):
                    book_author = line.replace('Author: ', '').strip()
                continue
            line = line.strip()
            if line.startswith("#"):
                if current_chapter["paragraphs"]:
                    book_contents.append(current_chapter)
                    current_chapter = {"title": None, "paragraphs": []}
                current_chapter["title"] = line[1:].strip()
                chapter_titles.append(current_chapter["title"])
            elif line:
                #skip any lines without at least one letter or number
                if any(char.isalnum() for char in line):
                    current_chapter["paragraphs"].append(line)

        if current_chapter["paragraphs"]:
            print(current_chapter)
            book_contents.append(current_chapter)

    return book_contents, book_title, book_author, chapter_titles

def sort_key(s):
    # extract number from the string
    return int(re.findall(r'\d+', s)[0])

def check_for_file(filename):
    if os.path.isfile(filename):
        print(f"The file '{filename}' already exists.")
        overwrite = input("Do you want to overwrite the file? (y/n): ")
        if overwrite.lower() != 'y':
            print("Exiting without overwriting the file.")
            sys.exit()
        else:
            os.remove(filename)

def append_silence(tempfile, duration=1200):
    audio = AudioSegment.from_file(tempfile)
    # Create a silence segment
    silence = AudioSegment.silent(duration)
    # Append the silence segment to the audio
    combined = audio + silence
    # Save the combined audio back to file
    combined.export(tempfile, format="mp3")

def read_book(book_contents, speaker):
    segments = []
    for i, chapter in enumerate(book_contents, start=1):
        files = []
        partname = f"part{i}.flac"
        if os.path.isfile(partname):
            print(f"{partname} exists, skipping to next chapter")
            segments.append(partname)
        else:
            print(f"Chapter: {chapter['title']}\n")
            asyncio.run(parallel_edgespeak([chapter['title']], [speaker], ['paras0.mp3']))
            append_silence('paras0.mp3', 1200)
            for pindex, paragraph in enumerate(chapter["paragraphs"]):
                sentences = sent_tokenize(paragraph)
                filenames = ['paras'+str(z+1)+".mp3" for z in range(len(sentences))]
                speakers = [speaker] * len(sentences)
                asyncio.run(parallel_edgespeak(sentences, speakers, filenames))
                append_silence(filenames[-1], 1200)
                #combine sentences in paragraph
                sorted_files = sorted(filenames, key=sort_key)
                if os.path.exists("paras0.mp3"):
                    sorted_files.insert(0, "paras0.mp3")
                combined = AudioSegment.empty()
                for file in sorted_files:
                    combined += AudioSegment.from_file(file)
                ptemp = f"pgraphs{pindex}.flac"
                combined.export(ptemp, format='flac')
                for file in sorted_files:
                    os.remove(file)
                files.append(ptemp)
            #combine paragraphs into chapter
            append_silence(files[-1], 2800)
            combined = AudioSegment.empty()
            for file in files:
                combined += AudioSegment.from_file(file)
            combined.export(partname, format="flac")
            for file in files:
                os.remove(file)
            segments.append(partname)
    return segments

def generate_metadata(files, author, title, chapter_titles):
    chap = 0
    start_time = 0
    with open("FFMETADATAFILE", "w") as file:
        file.write(";FFMETADATA1\n")
        file.write(f"ARTIST={author}\n")
        file.write(f"ALBUM={title}\n")
        file.write("DESCRIPTION=Made with https://github.com/aedocw/epub2tts-edge\n")
        for file_name in files:
            duration = get_duration(file_name)
            file.write("[CHAPTER]\n")
            file.write("TIMEBASE=1/1000\n")
            file.write(f"START={start_time}\n")
            file.write(f"END={start_time + duration}\n")
            file.write(f"title={chapter_titles[chap]}\n")
            chap += 1
            start_time += duration

def get_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_milliseconds = len(audio)
    return duration_milliseconds

def make_m4b(files, sourcefile, speaker):
    filelist = "filelist.txt"
    basefile = sourcefile.replace(".txt", "")
    outputm4a = f"{basefile}-{speaker}.m4a"
    outputm4b = f"{basefile}-{speaker}.m4b"
    with open(filelist, "w") as f:
        for filename in files:
            filename = filename.replace("'", "'\\''")
            f.write(f"file '{filename}'\n")
    ffmpeg_command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        filelist,
        "-codec:a",
        "flac",
        "-f",
        "mp4",
        outputm4a,
    ]
    subprocess.run(ffmpeg_command)
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        outputm4a,
        "-i",
        "FFMETADATAFILE",
        "-map_metadata",
        "1",
        "-codec",
        "aac",
        outputm4b,
    ]
    subprocess.run(ffmpeg_command)
    os.remove(filelist)
    os.remove("FFMETADATAFILE")
    os.remove(outputm4a)
    for f in files:
        os.remove(f)
    return outputm4b

def add_cover(cover_img, filename):
    try:
        if os.path.isfile(cover_img):
            m4b = mp4.MP4(filename)
            cover_image = open(cover_img, "rb").read()
            m4b["covr"] = [mp4.MP4Cover(cover_image)]
            m4b.save()
        else:
            print(f"Cover image {cover_img} not found")
    except:
        print(f"Cover image {cover_img} not found")

def run_edgespeak(sentence, speaker, filename):
    communicate = edge_tts.Communicate(sentence, speaker)
    run_save(communicate, filename)

def run_save(communicate, filename):
    asyncio.run(communicate.save(filename))

async def parallel_edgespeak(sentences, speakers, filenames):
    semaphore = asyncio.Semaphore(10)  # Limit the number of concurrent tasks

    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = []
        for sentence, speaker, filename in zip(sentences, speakers, filenames):
            async with semaphore:
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(executor, run_edgespeak, sentence, speaker, filename)
                tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(
        prog="epub2tts-edge",
        description="Read a text file to audiobook format",
    )
    parser.add_argument("sourcefile", type=str, help="The epub or text file to process")
    parser.add_argument(
        "--speaker",
        type=str,
        nargs="?",
        const="en-US-AndrewNeural",
        default="en-US-AndrewNeural",
        help="Speaker to use (ex en-US-MichelleNeural)",
    )
    parser.add_argument(
        "--cover",
        type=str,
        help="jpg image to use for cover",
    )

    args = parser.parse_args()
    print(args)

    #If we get an epub, export that to txt file, then exit
    if args.sourcefile.endswith(".epub"):
        book = epub.read_epub(args.sourcefile)
        export(book, args.sourcefile)
        exit()

    book_contents, book_title, book_author, chapter_titles = get_book(args.sourcefile)
    files = read_book(book_contents, args.speaker)
    generate_metadata(files, book_author, book_title, chapter_titles)
    m4bfilename = make_m4b(files, args.sourcefile, args.speaker)
    add_cover(args.cover, m4bfilename)


if __name__ == "__main__":
    main()
