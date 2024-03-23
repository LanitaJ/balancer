import pyaudio
import wave
import speech_recognition as sr



CHUNK = 1024 # определяет форму ауди сигнала
FRT = pyaudio.paInt16 # шестнадцатибитный формат задает значение амплитуды
CHAN = 1 # канал записи звука
RT = 44100 # частота 
REC_SEC = 5 #длина записи
OUTPUT = "./data/audio/output.wav"

p = pyaudio.PyAudio()

# stream = p.open(format=FRT,channels=CHAN,rate=RT,input=True,frames_per_buffer=CHUNK) # открываем поток для записи
# print("rec")
# frames = [] # формируем выборку данных фреймов
# for i in range(0, int(RT / CHUNK * REC_SEC)):
#     data = stream.read(CHUNK)
#     frames.append(data)
# print("done")
# # и закрываем поток 
# stream.stop_stream() # останавливаем и закрываем поток 
# stream.close()
# p.terminate()


# w = wave.open(OUTPUT, 'wb')
# w.setnchannels(CHAN)
# w.setsampwidth(p.get_sample_size(FRT))
# w.setframerate(RT)
# w.writeframes(b''.join(frames))
# w.close()


# Create an instance of the Recognizer class
recognizer = sr.Recognizer()

# Create audio file instance from the original file
audio_ex = sr.AudioFile('output.wav')
type(audio_ex)

# Create audio data
with audio_ex as source:
    audiodata = recognizer.record(audio_ex)
type(audiodata)

# Extract text
text = recognizer.recognize_google(audio_data=audiodata, language='ru-RU')

print(text)