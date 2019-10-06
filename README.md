#Tugas Implementasi API
Mata Kuliah Teknologi Sistem Terintegrasi
<br>Author: Vincent / 18217042

#Gambaran Umum _Interface_
API yang akan dibuat adalah API yang memberikan layanan 
<br>pencatatan pengiriman barang logistic yang terintegrasi 
<br>secara real time dengan 3 buah perusahaan pengiriman 
<br>logistik di Indonesia, yaitu JNE, TIKI, dan POS Indonesia. 
<br>API ini akan melayani pengecekan ongkos pengiriman barang, 
<br>serta pencatatan data pengiriman barang.

#Penggunaan
Ubah konfigurasi database mysql Anda pada:<br>
~~~
app.config['MYSQL_DATABASE_USER'] = '{username Anda}'
app.config['MYSQL_DATABASE_PASSWORD'] = '{password Anda}'
app.config['MYSQL_DATABASE_DB'] = '{nama database Anda}'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
~~~


Jalankan `python app.py` pada command line

Server akan berjalan pada URL [http://127.0.0.1:5000](http://127.0.0.1:5000)

# Supported Request Method
+ GET
+ POST
+ PUT
+ DELETE 

