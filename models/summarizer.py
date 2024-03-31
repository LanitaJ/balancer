import sys
from gensim.summarization import summarize
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq
import re
from gensim.summarization import summarize

nltk.download("punkt")
nltk.download("stopwords")

def summarize_text(file_path):
    with open(file_path, 'r') as file:
        text = file.read()    
        # print('text', text)
        # Tokenize the text into sentences and words
        # sentences = sent_tokenize(text)
        # words = word_tokenize(text)

        # Remove stopwords and perform stemming
        stop_words = set(stopwords.words("english"))
        stemmer = nltk.PorterStemmer()
        # filtered_words = [stemmer.stem(word) for word in words if word.lower() not in stop_words and word.isalnum()]

        # Join the filtered words to create a preprocessed version of the text
        # preprocessed_text = " ".join(filtered_words)
        # print(preprocessed_text)
        
        # Generate the summary
        compression_ratio = 0.4
        summary = summarize(text, ratio=compression_ratio)

        # Print the summary
        # print("Original text:")
        # print(text)
        # print("\nSummary:")
        # print(summary)
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