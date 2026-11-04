"""Verilen dosyaları FTPS ile hosting'e yükler.
Bilgiler ortam değişkenlerinden okunur (GitHub Secrets): FTP_HOST, FTP_USER, FTP_PASS, FTP_DIR (isteğe bağlı).
Şifre koda veya depoya YAZILMAZ."""
import ftplib, os, sys

host, user, pw = os.environ['FTP_HOST'], os.environ['FTP_USER'], os.environ['FTP_PASS']
hedef = os.environ.get('FTP_DIR') or '/public_html/veri'

ftp = ftplib.FTP_TLS(host, timeout=60)
ftp.login(user, pw)
ftp.prot_p()
parts = [p for p in hedef.strip('/').split('/') if p]
ftp.cwd('/')
for p in parts:
    try:
        ftp.cwd(p)
    except ftplib.error_perm:
        ftp.mkd(p); ftp.cwd(p)
for yol in sys.argv[1:]:
    with open(yol, 'rb') as f:
        ftp.storbinary('STOR ' + os.path.basename(yol), f)
    print('yüklendi:', os.path.basename(yol), '->', hedef)
ftp.quit()
