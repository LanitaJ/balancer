import os

BALANCER = bool(os.getenv("BALANCER", True))

# BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))

N_CORES_AVAILABLE = int(os.getenv('N_CORES_AVAILABLE', 12))
N_CORES_DEFAULT = int(os.getenv("N_CORES_DEFAULT", 1))

N_CORES_EMOTION = int(os.getenv('N_CORES_EMOTION', 4))
N_CORES_TRANSCRIPTION = int(os.getenv('N_CORES_TRANSCRIPTION', 4))
N_CORES_SUMMARIZATION = int(os.getenv('N_CORES_SUMMARIZATION', 4))

CLUSTERIZATION = 'clusterization'
TRANSCRIPTION = 'transcription'
SUMMARIZATION = 'summarization'
EMOTION = 'emotion'

DATA_PATH = os.getcwd() + '/data/'
