from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            nim INTEGER PRIMARY KEY,
            nama TEXT NOT NULL,
            program_studi TEXT NOT NULL,
            angkatan INTEGER NOT NULL,
            ipk REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# READ - DAFTAR MAHASISWA
# =========================
@app.route("/")
def index():
    conn = get_db_connection()

    mahasiswa = conn.execute(
        "SELECT * FROM mahasiswa ORDER BY nim"
    ).fetchall()

    conn.close()

    tahun_sekarang = datetime.now().year

    return render_template(
        "index.html",
        mahasiswa=mahasiswa,
        tahun_sekarang=tahun_sekarang
    )


# =========================
# READ - DETAIL MAHASISWA
# =========================
@app.route("/detail/<int:nim>")
def detail(nim):
    conn = get_db_connection()

    mahasiswa = conn.execute(
        "SELECT * FROM mahasiswa WHERE nim = ?",
        (nim,)
    ).fetchone()

    conn.close()

    if mahasiswa is None:
        return "Mahasiswa tidak ditemukan", 404

    tahun_sekarang = datetime.now().year
    lama_studi = tahun_sekarang - mahasiswa["angkatan"]

    return render_template(
        "detail.html",
        mahasiswa=mahasiswa,
        lama_studi=lama_studi
    )


# =========================
# CREATE - TAMBAH MAHASISWA
# =========================
@app.route("/tambah", methods=["GET", "POST"])
def tambah():

    if request.method == "POST":

        nim = request.form["nim"].strip()
        nama = request.form["nama"].strip()
        program_studi = request.form["program_studi"].strip()
        angkatan = request.form["angkatan"].strip()
        ipk = request.form["ipk"].strip()

        # Validasi data kosong
        if not nim or not nama or not program_studi or not angkatan or not ipk:
            return render_template(
                "tambah.html",
                error="NIM, nama, program studi, angkatan, dan IPK wajib diisi."
            )

        # Validasi NIM
        try:
            nim = int(nim)
        except ValueError:
            return render_template(
                "tambah.html",
                error="NIM harus berupa angka."
            )

        # Validasi angkatan
        try:
            angkatan = int(angkatan)
        except ValueError:
            return render_template(
                "tambah.html",
                error="Angkatan harus berupa angka."
            )

        # Validasi IPK
        try:
            ipk = float(ipk)
        except ValueError:
            return render_template(
                "tambah.html",
                error="IPK harus berupa angka."
            )

        # Validasi IPK 0 - 4
        if ipk < 0 or ipk > 4:
            return render_template(
                "tambah.html",
                error="IPK harus berada pada rentang 0.00 sampai 4.00."
            )

        conn = get_db_connection()

        # Cek NIM sudah ada
        mahasiswa = conn.execute(
            "SELECT * FROM mahasiswa WHERE nim = ?",
            (nim,)
        ).fetchone()

        if mahasiswa:
            conn.close()

            return render_template(
                "tambah.html",
                error="NIM tersebut sudah terdaftar."
            )

        # Simpan data
        conn.execute(
            """
            INSERT INTO mahasiswa
            (nim, nama, program_studi, angkatan, ipk)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nim, nama, program_studi, angkatan, ipk)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("tambah.html")


# =========================
# UPDATE - EDIT MAHASISWA
# =========================
@app.route("/edit/<int:nim>", methods=["GET", "POST"])
def edit(nim):

    conn = get_db_connection()

    mahasiswa = conn.execute(
        "SELECT * FROM mahasiswa WHERE nim = ?",
        (nim,)
    ).fetchone()

    conn.close()

    if mahasiswa is None:
        return "Mahasiswa tidak ditemukan", 404

    if request.method == "POST":

        nama = request.form["nama"].strip()
        program_studi = request.form["program_studi"].strip()
        angkatan = request.form["angkatan"].strip()
        ipk = request.form["ipk"].strip()

        # Validasi kosong
        if not nama or not program_studi or not angkatan or not ipk:
            return render_template(
                "edit.html",
                mahasiswa=mahasiswa,
                error="Nama, program studi, angkatan, dan IPK wajib diisi."
            )

        # Validasi angkatan
        try:
            angkatan = int(angkatan)
        except ValueError:
            return render_template(
                "edit.html",
                mahasiswa=mahasiswa,
                error="Angkatan harus berupa angka."
            )

        # Validasi IPK
        try:
            ipk = float(ipk)
        except ValueError:
            return render_template(
                "edit.html",
                mahasiswa=mahasiswa,
                error="IPK harus berupa angka."
            )

        # Validasi IPK
        if ipk < 0 or ipk > 4:
            return render_template(
                "edit.html",
                mahasiswa=mahasiswa,
                error="IPK harus berada pada rentang 0.00 sampai 4.00."
            )

        conn = get_db_connection()

        conn.execute(
            """
            UPDATE mahasiswa
            SET nama = ?,
                program_studi = ?,
                angkatan = ?,
                ipk = ?
            WHERE nim = ?
            """,
            (nama, program_studi, angkatan, ipk, nim)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template(
        "edit.html",
        mahasiswa=mahasiswa
    )


# =========================
# DELETE - HAPUS MAHASISWA
# =========================
@app.route("/hapus/<int:nim>", methods=["POST"])
def hapus(nim):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM mahasiswa WHERE nim = ?",
        (nim,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# =========================
# MENJALANKAN APLIKASI
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)