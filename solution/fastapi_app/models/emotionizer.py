import datetime
import os
import sys
import text2emotion as te

def analyze_emotion(file_path):
    """
    Analyzes the emotions in the given text and returns the scores for each emotion.
    
    :param text: A string containing the text to analyze.
    :return: A dictionary with emotion scores.
    """
    with open(file_path, 'r') as file:
        text = file.read()
        emotion_scores = te.get_emotion(text)
        output_text_path = file_path[:-4]  + 'res.txt'
        with open(output_text_path, "w") as f:
            f.write(text)
            print(f"PID:{os.getpid()} {datetime.datetime.now()} Analyzed emotion saved to {output_text_path}")

        return emotion_scores


def main():
    if len(sys.argv) < 2:
        print("Usage: python emotionizer.py path/to/text1.txt path/to/text2.txt ...")
    else:
        file_paths = sys.argv[1:]
        for file in file_paths:
            print(file)
            emotions = analyze_emotion(file)
            print("Emotion scores:", emotions)


if __name__ == '__main__':
    main()