import datetime
import os
import sys
from gensim.summarization import summarize
import nltk
from nltk.corpus import stopwords
import heapq
import re

nltk.download("punkt")
nltk.download("stopwords")

def summarize_text(file_path):
    with open(file_path, 'r') as file:
        text = file.read()

        # Generate the summary
        compression_ratio = 0.4
        summary = 'No summary'
        try:
            summary = summarize(text, compression_ratio)
        except Exception as e:
            print(e, text)
            
        output_text_path = file_path[:-4]  + '_res.txt'

        with open(output_text_path, "w") as f:
            f.write(summary)
            print(f"PID:{os.getpid()} {datetime.datetime.now()} Summary saved to {output_text_path}")

        return summary


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarizer.py path/to/text1.txt path/to/text2.txt ...")
    else:
        file_paths = sys.argv[1:]
        for file in file_paths:
            print(file)
            summarize_text(file)


if __name__ == '__main__':
    main()