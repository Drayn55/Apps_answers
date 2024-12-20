"use client";
import CustomAlert from "@/components/CustomAlert";
import { useState, useEffect } from "react";

export default function Home() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [comparisonResults, setComparisonResults] = useState([]);
  const [image, setImage] = useState(null); // Deklarasikan state untuk menyimpan URL gambar
  const [previewImage, setPreviewImage] = useState(null); // State untuk pratinjau gambar
  const [alertMessage, setAlertMessage] = useState(""); // State untuk pesan alert
  const [showAlert, setShowAlert] = useState(false); // State untuk kontrol visibilitas alert

  // Jawaban yang benar untuk 20 soal
  const correctAnswers = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "A",
    "C",
    "B",
    "A",
    "E",
    "B",
    "C",
    "E",
    "A",
    "B",
    "C",
    "E",
    "C",
    "D",
    "A",
  ];

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);

    // Membuat URL untuk pratinjau gambar
    if (selectedFile) {
      const imageUrl = URL.createObjectURL(selectedFile);
      setPreviewImage(imageUrl); // Simpan URL gambar untuk pratinjau
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setAlertMessage("Please upload an image answers");
      setShowAlert(true);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("https://your-project-name.vercel.app/api/process", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("Error uploading file:", err);
    }
  };

  // Menggunakan useEffect untuk memproses jawaban setelah response diperbarui
  useEffect(() => {
    if (response) {
      const leftAnswers = response?.mapped_answers?.left || [];
      const rightAnswers = response?.mapped_answers?.right || [];

      // Mengubah nilai questionNum untuk answers right
      const combinedAnswers = [
        ...leftAnswers,
        ...rightAnswers.map(([num, answer]) => [
          num + leftAnswers.length,
          answer,
        ]), // Menambahkan panjang leftAnswers untuk memulai dari 11
      ];

      // Melakukan perbandingan jawaban
      const results = combinedAnswers.map(
        ([questionNum, userAnswer], index) => {
          const correctAnswer = correctAnswers[index]; // Ambil jawaban yang benar berdasarkan index
          return {
            questionNum,
            userAnswer,
            correctAnswer,
            isCorrect: userAnswer === correctAnswer, // Bandingkan jawaban
          };
        }
      );
      setComparisonResults(results); // Simpan hasil perbandingan
    }
  }, [response]); // Hanya jalankan efek ini ketika response berubah

  // Fungsi untuk mengambil gambar dari backend
  const fetchImage = async () => {
    const response = await fetch("https://your-project-name.vercel.app/api/get-image");
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);
    setImage(imageUrl); // Simpan URL gambar ke state
  };

  // Panggil fetchImage setelah response diperbarui
  useEffect(() => {
    if (response) {
      fetchImage();
    }
  }, [response]);

  const handleCloseAlert = () => {
    setShowAlert(false);
  };

  return (
    <div className="w-full flex flex-wrap justify-center items-center min-h-screen bg-gradient-to-r from-teal-400 to-blue-500 py-8">


      <div className="flex lg:flex-col flex-wrap gap-11 justify-center items-center w-full">
      {showAlert && (
        <CustomAlert message={alertMessage} onClose={handleCloseAlert} />
      )}
        {/* input file */}
        <div className="w-full flex flex-wrap justify-center">
          <div class="w-full max-w-sm bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
            <div class="grid px-4 items-center py-5">
              <h5 class="mb-1 text-xl font-medium text-gray-900 dark:text-white mx-auto">
                Scan your answers
              </h5>
              <div class="grid ">
                <form onSubmit={handleSubmit} class="grid mt-4">
                  <div class="flex items-center justify-center w-full overflow-hidden">
                    <label
                      htmlFor="dropzone-file"
                      className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500"
                    >
                      {previewImage ? (
                        <img
                          src={previewImage}
                          alt="Preview"
                          style={{ maxWidth: "100%", maxHeight: "100%" }}
                        />
                      ) : (
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                          <svg
                            className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400"
                            aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 20 16"
                          >
                            <path
                              stroke="currentColor"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                            />
                          </svg>
                          <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                            <span className="font-semibold">
                              Click to upload
                            </span>{" "}
                            or drag and drop
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            PNG (MAX. 800x400px)
                          </p>
                        </div>
                      )}
                      <input
                        id="dropzone-file"
                        type="file"
                        className="hidden"
                        accept="image/*"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>

                  <button
                    type="submit"
                    class="text-white bg-gradient-to-r from-cyan-500 to-blue-500 mt-4 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-cyan-300 dark:focus:ring-cyan-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center mb-2"
                  >
                    Scanning
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
        {/* end input file */}

        {/* image */}

        <div>
          {image && (
            <div style={{ marginTop: "20px" }}>
              {/* <h3>Processed Image:</h3> */}
              <div
                class="flex items-center p-4 mb-4 text-sm text-green-800 border border-green-300 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400 dark:border-green-800"
                role="alert"
              >
                <svg
                  class="flex-shrink-0 inline w-4 h-4 me-3"
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
                </svg>
                <span class="sr-only">Info</span>
                <div>
                  <span class="font-medium">
                    Success Processed Successfully
                  </span>
                </div>
              </div>
              <img
                src={image}
                alt="Processed"
                class="w-full h-auto max-w-xl rounded-lg"
              />
            </div>
          )}
        </div>

        {/* end image */}

        {/* table */}
        <div className="relative overflow-x-auto lg:w-1/2">
          {response && (
            <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
              <thead className="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-700 dark:text-gray-400">
                <tr>
                  <th scope="col" className="px-6 py-3 rounded-s-lg">
                    Question
                  </th>
                  <th scope="col" className="px-6 py-3">
                    Your Answer
                  </th>
                  <th scope="col" className="px-6 py-3 rounded-e-lg">
                    Result
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisonResults.map(
                  (
                    { questionNum, userAnswer, correctAnswer, isCorrect },
                    index
                  ) => (
                    <tr
                      className="bg-white dark:bg-gray-800"
                      key={`${questionNum}-${index}`}
                    >
                      <th
                        scope="row"
                        className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white"
                      >
                        {questionNum}
                      </th>
                      <td className="px-6 py-4">{userAnswer}</td>
                      <td className="px-6 py-4">
                        {isCorrect ? (
                          <svg
                            className="w-3 h-3 text-green-500"
                            aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 16 12"
                          >
                            <path
                              stroke="currentColor"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M1 5.917 5.724 10.5 15 1.5"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="w-3 h-3 text-red-500"
                            aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 14 14"
                          >
                            <path
                              stroke="currentColor"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                            />
                          </svg>
                        )}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
              <tfoot>
                <tr className="font-semibold text-gray-900 dark:text-white bg-gray-100">
                  <th scope="row" className="px-6 py-3 text-base">
                    Total Correct Answers
                  </th>
                  <td className="px-6 py-3">
                    {" "}
                    {/* Anda bisa menambahkan informasi lain di sini jika perlu */}{" "}
                  </td>
                  <td className="px-6 py-3">
                    {
                      comparisonResults.filter((result) => result.isCorrect)
                        .length
                    }
                  </td>
                </tr>
              </tfoot>
            </table>
          )}
        </div>
        {/* end table */}
      </div>
    </div>
  );
}
