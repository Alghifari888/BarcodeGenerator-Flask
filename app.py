import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash

# Import library barcode
import barcode
from barcode.writer import ImageWriter, SVGWriter 
import qrcode

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.secret_key = 'kunci_rahasia_untuk_flash_messages'

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
    output_format = request.form.get('output_format', 'png')

    # --- Validasi Input ---
    if not data:
        flash('Data tidak boleh kosong!', 'error')
        return redirect(url_for('index'))
    
    if barcode_type == 'ean13' and (not data.isdigit() or len(data) != 12):
        flash('Untuk EAN-13, data harus terdiri dari 12 digit angka.', 'error')
        return render_template('index.html', last_data=data)
    
    if barcode_type == 'upca' and (not data.isdigit() or len(data) != 11):
        flash('Untuk UPC-A, data harus terdiri dari 11 digit angka.', 'error')
        return render_template('index.html', last_data=data)
    
    # --- LOGIKA PINTAR UNTUK MENGATASI QR CODE + SVG ---
    if barcode_type == 'qrcode' and output_format == 'svg':
        # Beri pesan peringatan yang jelas
        flash('QR Code tidak mendukung SVG, hasilnya otomatis di-generate sebagai PNG.', 'warning')
        # Paksa format menjadi PNG dan lanjutkan proses
        output_format = 'png'

    try:
        filename = f"{uuid.uuid4()}"
        final_filename = f"{filename}.{output_format}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if barcode_type == 'qrcode':
            fill_color = request.form.get('fill_color', 'black')
            back_color = request.form.get('back_color', 'white')

            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], final_filename))
        else:
            CODE = barcode.get_barcode_class(barcode_type)
            writer = SVGWriter() if output_format == 'svg' else ImageWriter()
            my_barcode = CODE(data, writer=writer)
            my_barcode.save(filepath) 

        # Tampilkan halaman hasil
        return render_template(
            'result.html', 
            barcode_image=final_filename, 
            data=data, 
            barcode_type=barcode_type.upper(),
            output_format=output_format
        )

    except Exception as e:
        # Menangani jika ada error lain yang tak terduga
        flash(f'Terjadi kesalahan saat membuat barcode: {e}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
