from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Mengizinkan semua domain untuk mengakses API

def detect_marked_answers(image_path):
    # Baca gambar
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur untuk mengurangi noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

# Deteksi lingkaran dengan Hough Circle Transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=2, minDist=11,param1=488, param2=10, minRadius=9, maxRadius=15)

    marked_answers = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle
            if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
                mask = np.zeros_like(gray)
                cv2.circle(mask, (x, y), r, 255, -1)
                filled_area = cv2.countNonZero(cv2.bitwise_and(gray, gray, mask=mask))
                if filled_area > 80:
                    marked_answers.append((x, y))
                    cv2.circle(img, (x, y), r, (0, 255, 0), 2)

    # Fungsi untuk mendeteksi kotak hitam
    def detect_black_squares(gray, img):
        _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        square_coordinates = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = float(w) / h
                    if 0.8 <= aspect_ratio <= 1.2:
                        square_coords = [(int(point[0][0]), int(point[0][1])) for point in approx]
                        square_coordinates.extend(square_coords)
                        cv2.drawContours(img, [approx], -1, (0, 0, 255), 2)

        return len(square_coordinates) // 4, square_coordinates

    # Deteksi kotak hitam
    square_count, square_coordinates = detect_black_squares(gray, img)

    # Fungsi untuk memetakan lingkaran ke grid
    def map_to_grid(start_x, start_y, step_x, step_y, marked_answers):
        mapped_answers = []
        for x, y in marked_answers:
            col = (x - start_x) // step_x
            row = (y - start_y) // step_y
            if 0 <= col < 5 and 0 <= row < 10:
                mapped_answers.append((int(row), int(col)))  # Tambahkan posisi row dan col
        return mapped_answers

    mapped_answers_left = []
    mapped_answers_right = []

    if square_count >= 4:
        # Ambil koordinat kotak kedua
        box_2_x, box_2_y = square_coordinates[4:6][0]
    
        # Ambil koordinat kotak keempat
        box_4_x, box_4_y = square_coordinates[12:14][ 0]

        # Gunakan koordinat kotak kedua untuk tabel kiri
        start_x_left = box_2_x + 53
        start_y_left = box_2_y - 137
        step_x = 25
        step_y = 32

        # Gambar grid di sisi kiri
        for i in range(0, 11):
            cv2.line(img, (start_x_left, start_y_left + i * step_y),
                     (start_x_left + (5 * step_x), start_y_left + i * step_y), (255, 0, 0), 1)
        for j in range(0, 6):
            cv2.line(img, (start_x_left + j * step_x, start_y_left),
                     (start_x_left + j * step_x, start_y_left + (10 * step_y)), (255, 0, 0), 1)

        # Pemetaan lingkaran ke tabel kiri
        mapped_answers_left = map_to_grid(start_x_left, start_y_left, step_x, step_y, marked_answers)

        start_x_right = box_4_x + 229  # Atur offset sesuai dengan grid kanan
        start_y_right = box_4_y + 123

    # Gambar grid di sisi kanan
    for i in range(0, 11):
        cv2.line(img, (start_x_right, start_y_right + i * step_y),
                 (start_x_right + (5 * step_x), start_y_right + i * step_y), (255, 0, 0), 1)
    for j in range(0, 6):
        cv2.line(img, (start_x_right + j * step_x, start_y_right),
                 (start_x_right + j * step_x, start_y_right + (10 * step_y)), (255, 0, 0), 1)

    # Pemetaan lingkaran ke tabel kanan
    mapped_answers_right = map_to_grid(start_x_right, start_y_right, step_x, step_y, marked_answers)

    # Gabungkan pemetaan jawaban
    all_mapped_answers = {
        "left": mapped_answers_left,
        "right": mapped_answers_right
    }

    # Fungsi pemetaan koordinat ke nomor soal dan jawaban
    def map_answer_positions(answers, start_x, start_y, step_x, step_y, num_rows=20, num_cols=5):
        answer_keys = ['A', 'B', 'C', 'D', 'E']
        results = [None] * num_rows  # Inisialisasi daftar dengan None untuk 20 soal

        for x, y in answers:
            col = (x - start_x) // step_x  # Kolom jawaban (A-E)
            row = (y - start_y) // step_y  # Baris (nomor soal)

            if 0 <= row < num_rows and 0 <= col < num_cols:
                question_num = row + 1  # Nomor soal dimulai dari 1
                answer = answer_keys[int(col)]  # Jawaban A, B, C, D, atau E
                
                # Simpan jawaban pada indeks yang sesuai
                if results[row] is None:  # Jika belum ada jawaban untuk soal ini
                    results[row] = (question_num, answer)

        return [result for result in results if result is not None]  # Kembalikan hanya hasil yang tidak None

    # Ganti semua penggunaan start_y dengan start_y_left atau start_y_right sesuai konteks
    mapped_answers_left = map_answer_positions(marked_answers, start_x_left, start_y_left, step_x, step_y)
    mapped_answers_right = map_answer_positions(marked_answers, start_x_right, start_y_right, step_x, step_y)

    # Gabungkan hasil pemetaan jawaban dari kedua sisi
    mapped_answers = mapped_answers_left + mapped_answers_right

    # Cetak hasil jawaban yang terdeteksi
    # print("Hasil Jawaban yang Terdeteksi:")
    # for question, answer in mapped_answers:
    #     print(f"Nomor Soal {question}: Jawaban {answer}")

    # Menambahkan hasil deteksi ke dalam tabel di kotak kedua
    total_answers = len(mapped_answers)
    # Pastikan Anda menggunakan start_y_centered yang benar
    start_y_centered_left = start_y_left + (10 * step_y - len(mapped_answers_left) * step_y) // 2
    start_y_centered_right = start_y_right + (10 * step_y - len(mapped_answers_right) * step_y) // 2

    for i, (question, answer) in enumerate(mapped_answers_left):
        cv2.putText(img, f"{question}: {answer}", (start_x_left - 65, start_y_centered_left + i * 20 - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    for i, (question, answer) in enumerate(mapped_answers_right):
        adjusted_question_num = question + 10
        cv2.putText(img, f"{adjusted_question_num}: {answer}", (start_x_right + 130, start_y_centered_right + (i - 10) * 20 + 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    # # Cetak hasil jawaban yang terdeteksi
    # print("Hasil Jawaban yang Terdeteksi:")
    # for question, answer in mapped_answers_left:
    #     print(f"Nomor Soal {question}: Jawaban {answer}")

    # # Cetak hasil jawaban dari tabel kanan
    # for question, answer in mapped_answers_right:
    #     adjusted_question_num = question + 10  # Tambahkan 10 untuk melanjutkan nomor soal
    #     print(f"Nomor Soal {adjusted_question_num}: Jawaban {answer}")

    # Simpan hasil deteksi
    cv2.imwrite("output_detected_answers.png", img)  # Simpan gambar yang telah ditandai

    # Pastikan untuk mengonversi semua elemen yang relevan ke dalam list
    marked_answers = [(int(x), int(y)) for x, y in marked_answers]  # Konversi ke tuple of int
    square_coordinates = square_coordinates.tolist() if isinstance(square_coordinates, np.ndarray) else square_coordinates

    # Gabungkan hasil pemetaan jawaban
    all_mapped_answers = {
        "left": [(int(q), a) for q, a in mapped_answers_left],
        "right": [(int(q), a) for q, a in mapped_answers_right]
    }

    # Pastikan untuk mengembalikan nilai yang diharapkan
    return marked_answers, square_count, square_coordinates, all_mapped_answers

@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})

    filepath = "uploaded_image.png"
    file.save(filepath)

    try:
        marked_answers, square_count, square_coordinates, mapped_answers = detect_marked_answers(filepath)
        return jsonify({
            "status": "success",
            "message": "Image processed successfully",
            "marked_answers": marked_answers,
            "square_count": square_count,
            "square_coordinates": square_coordinates,
            "mapped_answers": mapped_answers
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
@app.route('/get-image', methods=['GET'])
def get_image():
    # Misalnya, Anda telah menyimpan gambar yang diproses sebagai 'output_detected_answers.png'
    return send_file('output_detected_answers.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)