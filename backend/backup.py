from flask import Flask, request, jsonify
import cv2
import numpy as np
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Mengizinkan semua domain untuk mengakses API


# Fungsi untuk mendeteksi lingkaran hitam yang diisi
# def detect_marked_answers(image_path):
#     # Baca gambar
#     img = cv2.imread(image_path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Crop area jawaban secara manual (ROI)
#     roi = gray[100:600, 50:385]  # Sesuaikan dengan koordinat gambar
#     _, thresh = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY_INV)

#     # Cari kontur lingkaran
#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     marked_circles = 0
#     for contour in contours:
#         # Filter kontur berdasarkan ukuran dan bentuk
#         (x, y, w, h) = cv2.boundingRect(contour)
#         aspect_ratio = w / float(h)
#         if 0.8 <= aspect_ratio <= 1.2 and 10 <= w <= 50:  # Bentuk bulat dan ukuran sesuai
#             marked_circles += 1
#             cv2.rectangle(roi, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Opsional: Tandai kotak
        
#     # Simpan hasil untuk debugging
#     cv2.imwrite("detected_answers.png", roi)

#     return marked_circles

import cv2
import numpy as np

def detect_marked_answers(image_path):
    # Baca gambar
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Crop area jawaban secara manual (ROI)
    roi = gray[100:600, 50:385]  # Sesuaikan area lingkaran jawaban
    img_roi = img[100:600, 50:385]  # Simpan gambar asli yang ter-crop untuk output

    # Blur untuk mengurangi noise dan meningkatkan akurasi deteksi lingkaran
    blurred = cv2.GaussianBlur(roi, (9, 9), 2)

    # Hough Circle Transform untuk deteksi lingkaran
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=2, minDist=11,
                               param1=488, param2=10, minRadius=9, maxRadius=15)

    marked_answers = []
    if circles is not None:
        circles = np.uint16(np.around(circles))  # Bulatkan koordinat lingkaran
        for circle in circles[0, :]:
            x, y, r = circle  # Koordinat pusat (x, y) dan radius
            
            # Pastikan koordinat berada dalam batas ROI
            if 0 <= y < roi.shape[0] and 0 <= x < roi.shape[1]:
                # Buat mask untuk lingkaran
                mask = np.zeros_like(roi)
                cv2.circle(mask, (x, y), r, 255, -1)  # Buat lingkaran penuh di mask

                # Hitung jumlah piksel hitam di dalam lingkaran
                # Kita ambil ROI yang terisi hitam
                filled_area = cv2.countNonZero(cv2.bitwise_and(roi, roi, mask=mask))

                # Jika ada piksel hitam di dalam lingkaran, anggap lingkaran terisi
                if filled_area > 80:  # Anda bisa menyesuaikan ambang batas ini
                    marked_answers.append((x, y))
                    # Tandai lingkaran yang terisi
                    cv2.circle(img_roi, (x, y), r, (0, 255, 0), 2)  # Tandai dengan warna hijau

    # Simpan hasil deteksi
    cv2.imwrite("output_detected_answers.png", img_roi)  # Simpan gambar yang telah di-crop dan ditandai

    return len(marked_answers), marked_answers




# Route untuk upload gambar dan deteksi jawaban
@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})

    filepath = "uploaded_image.png"
    file.save(filepath)

    # Panggil fungsi deteksi jawaban
    try:
        marked_answers_count = detect_marked_answers(filepath)
        return jsonify({
            "status": "success",
            "message": "Image processed successfully",
            "marked_answers_count": marked_answers_count
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)