import os
import cv2
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = "model.pkl"


# ---- Utility: extract face crop -> small grayscale vector (embedding) ----
def crop_face_and_embed(bgr_image, detection):
    h, w = bgr_image.shape[:2]
    bbox = detection.location_data.relative_bounding_box
    x1 = int(max(0, bbox.xmin * w))
    y1 = int(max(0, bbox.ymin * h))
    x2 = int(min(w, (bbox.xmin + bbox.width) * w))
    y2 = int(min(h, (bbox.ymin + bbox.height) * h))
    if x2 <= x1 or y2 <= y1:
        return None
    face = bgr_image[y1:y2, x1:x2]
    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(face, (32, 32), interpolation=cv2.INTER_AREA)
    emb = face.flatten().astype(np.float32) / 255.0
    return emb


def extract_embedding_with_opencv(bgr_image):
    """Fallback face detection using OpenCV Haar Cascade"""
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return None

        # Use the largest face
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        face = bgr_image[y : y + h, x : x + w]
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        face = cv2.resize(face, (32, 32), interpolation=cv2.INTER_AREA)
        emb = face.flatten().astype(np.float32) / 255.0
        return emb
    except Exception as e:
        print(f"ERROR in OpenCV face detection: {e}")
        return None


def extract_embedding_for_image(stream_or_bytes):
    # accepts a file-like stream (werkzeug FileStorage.stream)
    # read image from stream into numpy BGR
    data = stream_or_bytes.read()
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None

    try:
        # Try using mediapipe if available
        import mediapipe as mp

        mp_face = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        results = mp_face.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not results.detections:
            return None
        emb = crop_face_and_embed(img, results.detections[0])
        return emb
    except (ImportError, AttributeError) as e:
        # Fallback: use OpenCV cascade if mediapipe not available
        print(
            f"WARNING: MediaPipe not available ({e}). Using OpenCV cascade as fallback."
        )
        return extract_embedding_with_opencv(img)


# ---- Load model helpers ----
def load_model_if_exists():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def predict_with_model(clf, emb):
    # returns label and confidence (max probability)
    proba = clf.predict_proba([emb])[0]
    idx = np.argmax(proba)
    label = clf.classes_[idx]
    conf = float(proba[idx])
    return label, conf


# ---- Training function used in background ----
def train_model_background(dataset_dir, progress_callback=None):
    """
    dataset_dir/
        student_id/
            img1.jpg
            img2.jpg
    progress_callback(progress_percent, message) -> optional
    """
    try:
        import mediapipe as mp

        mp_face = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        use_mediapipe = True
    except (ImportError, AttributeError):
        print("WARNING: MediaPipe not available, using OpenCV fallback")
        mp_face = None
        use_mediapipe = False

    X = []
    y = []
    student_dirs = [
        d
        for d in os.listdir(dataset_dir)
        if os.path.isdir(os.path.join(dataset_dir, d))
    ]
    total_students = max(1, len(student_dirs))
    processed = 0

    for sid in student_dirs:
        folder = os.path.join(dataset_dir, sid)
        files = [
            f
            for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        for fn in files:
            path = os.path.join(folder, fn)
            img = cv2.imread(path)
            if img is None:
                continue

            emb = None
            if use_mediapipe and mp_face:
                results = mp_face.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                if results.detections:
                    emb = crop_face_and_embed(img, results.detections[0])
            else:
                emb = extract_embedding_with_opencv(img)

            if emb is None:
                continue
            X.append(emb)
            y.append(int(sid))
        processed += 1
        if progress_callback:
            pct = int(
                (processed / total_students) * 80
            )  # training progress up to 80% during feature extraction
            progress_callback(pct, f"Processed {processed}/{total_students} students")

    if len(X) == 0:
        if progress_callback:
            progress_callback(0, "No training data found")
        return

    # convert
    X = np.stack(X)
    y = np.array(y)

    # fit RandomForest
    if progress_callback:
        progress_callback(85, "Training RandomForest...")
    clf = RandomForestClassifier(n_estimators=150, n_jobs=-1, random_state=42)
    clf.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    if progress_callback:
        progress_callback(100, "Training complete")
