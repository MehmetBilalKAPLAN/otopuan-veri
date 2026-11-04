# otopuan-veri

Oto Puan için veri toplama hattı. İlk aşama: Wikipedia'dan model ve nesil yıllarını toplamak.

## Windows'ta ilk deneme

1. Açık olan Python penceresindeysen (`>>>` görüyorsan) `exit()` yaz ve kapat. Komutlar bu pencerede değil, Komut İstemi'nde çalışır.
2. Bu klasörü bilgisayarında bir yere çıkar (ör. `C:\otopuan-veri`).
3. Klasörün içinde adres çubuğuna `cmd` yaz ve Enter'a bas.
4. Önce test: `python test_wiki.py` (internet gerektirmez, "tümü geçti" yazmalı).
5. Sonra: `python ilk_test.py` ya da `calistir.bat` dosyasına çift tıkla.
6. Çıkan yazıyı (`cikti\ekran_ciktisi.txt`) Claude'a yapıştır.

Hata alırsan hata metnini olduğu gibi yapıştır.

## Notlar
- Yalnızca Python'un standart kütüphanesi kullanılır, `pip install` gerekmez.
- Her istek arasında 1 saniye beklenir (Wikipedia'ya nazik davranmak için).
- Veri Wikipedia'dan (CC BY-SA) gelir; çıktıdaki her kayıt sayfa bağlantısıyla birlikte saklanır.
- Bu ilk sürüm sonuçları henüz canlı olarak doğrulanmadı. İlk çıktıya göre ayrıştırıcıyı düzelteceğiz.

## GitHub Actions ile otomatik çalışma

1. Depoya bu dosyaların hepsini yükle (özellikle `.github/workflows/haftalik.yml`).
2. Depo sayfasında **Actions** sekmesi, **Haftalik veri guncelleme**, **Run workflow** ile elle çalıştır.
3. Çalışma bitince işin sayfasındaki **Summary** bölümünde özet görünür.
4. Hosting'e otomatik yükleme istersen: **Settings, Secrets and variables, Actions, New repository secret** ile şunları ekle:
   `FTP_HOST`, `FTP_USER`, `FTP_PASS` ve isteğe bağlı `FTP_DIR` (varsayılan `/public_html/veri`).
   Şifreyi sohbete veya koda yazma; yalnızca bu Secrets bölümüne gir.
   Önerilen: cPanel'de **FTP Accounts** bölümünden yalnızca `veri` klasörüne yetkili ayrı bir FTP hesabı aç.
