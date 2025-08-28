import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash

# Import library barcode
import barcode
from barcode.writer import ImageWriter
import qrcode

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.secret_key = 'kunci_rahasia_untuk_flash_messages' # Diperlukan untuk flash message

# Konfigurasi folder untuk menyimpan gambar barcode
BARCODE_FOLDER = os.path.join('static', 'barcodes')
app.config['UPLOAD_FOLDER'] = BARCODE_FOLDER

# Pastikan folder 'static/barcodes' ada
os.makedirs(BARCODE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Menampilkan halaman utama dengan form input."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Menangani proses pembuatan barcode."""
    data = request.form.get('data')
    barcode_type = request.form.get('barcode_type')

    # --- Validasi Input ---
    if not data:
        flash('Data tidak boleh kosong!', 'error')
        return redirect(url_for('index'))

    # Validasi spesifik untuk EAN-13 dan UPC-A
    if barcode_type == 'ean13':
        if not data.isdigit() or len(data) != 12:
            flash('Untuk EAN-13, data harus terdiri dari 12 digit angka.', 'error')
            return render_template('index.html', last_data=data)
    
    if barcode_type == 'upca':
        if not data.isdigit() or len(data) != 11:
            flash('Untuk UPC-A, data harus terdiri dari 11 digit angka.', 'error')
            return render_template('index.html', last_data=data)

    try:
        # Membuat nama file yang unik untuk menghindari tumpukan
        filename = f"{uuid.uuid4()}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        final_filename = ""

        # --- Logika Pembuatan Barcode ---
        if barcode_type == 'qrcode':
            # Generate QR Code
            img = qrcode.make(data)
            final_filename = filename + '.png'
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], final_filename))
        else:
            # Generate barcode linear (Code128, EAN-13, UPC-A)
            CODE = barcode.get_barcode_class(barcode_type)
            # Membuat barcode dengan writer ImageWriter untuk output PNG
            my_barcode = CODE(data, writer=ImageWriter())
            # Simpan barcode (tanpa ekstensi, akan ditambahkan oleh library)
            my_barcode.save(filepath)
            final_filename = filename + '.png'

        # Mengarahkan ke halaman hasil
        return render_template(
            'result.html', 
            barcode_image=final_filename, 
            data=data, 
            barcode_type=barcode_type.upper()
        )

    except Exception as e:
        # Menangani jika ada error saat pembuatan barcode
        flash(f'Terjadi kesalahan saat membuat barcode: {e}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
