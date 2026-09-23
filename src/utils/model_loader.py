import joblib

def load_model(file_path):
    model = joblib.load(file_path)
    return file_path