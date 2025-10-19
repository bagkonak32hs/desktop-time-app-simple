# desktop-time-app-simple

# SimpleDesk (Python + Tkinter)
Zero-dependency masaüstü uygulaması. **Ekstra kurulum yok**: Python 3 kuruluysa direkt çalışır.

## Özellikler
- 📝 Notlar (otomatik kaydetme)
- ✅ Yapılacaklar (tamamla/sil, TXT dışa aktar)
- ⏱️ Zamanlayıcı/Pomodoro (25/15/5 dk)
- 📂 Hızlı Dosyalar (listeye ekle, çift tıkla aç)

## Çalıştırma
1) VS Code'da klasörü açın.
2) `app.py` dosyasını çalıştırın (Run ▶).  
   - Terminalden: `python app.py`

> Not: Harici paket gerekmez; yalnızca Python 3.9+ yeterli.

## Yapı
```
simpledesk/
 ├─ app.py
 ├─ data/               # ilk çalıştırmada otomatik oluşur
 ├─ assets/
 │   ├─ icon.ico
 ├─ .vscode/
 │   └─ launch.json     # F5 ile çalıştırma
 ├─ run.bat             # Windows hızlı başlat
 └─ run.sh              # macOS/Linux hızlı başlat
```

## İsteğe Bağlı
- `run.bat` veya `run.sh` ile tek tık.
- Veriler `data/` klasöründe JSON olarak saklanır.
