import tkinter as tk
from tkinter import ttk, messagebox
import requests
import random
import threading
import os

# 15 Yıllık Tecrübe - Anti-Detection Stealth Engine
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Smart-TV; Linux; Tizen 7.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/6.4 Chrome/94.0.4606.81 TV Safari/537.36"
]

class ShadowDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("ShadowStream Downloader v1.0 - Portable")
        self.root.geometry("500x400")
        self.root.configure(bg='#1e1e1e')

        # Stil Ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", foreground="white", background="#1e1e1e")
        style.configure("TButton", foreground="white", background="#007ACC")

        # Arayüz Elemanları
        ttk.Label(root, text="Xtream / M3U8 / Video URL:", font=('Segoe UI', 10, 'bold')).pack(pady=10)
        self.url_entry = ttk.Entry(root, width=60)
        self.url_entry.pack(pady=5)

        ttk.Label(root, text="Dosya Adı (uzantı ile):").pack(pady=5)
        self.name_entry = ttk.Entry(root, width=40)
        self.name_entry.insert(0, "video_indirildi.mp4")
        self.name_entry.pack(pady=5)

        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=20)

        self.status_label = ttk.Label(root, text="Durum: Hazır")
        self.status_label.pack(pady=5)

        ttk.Button(root, text="GİZLİ İNDİRMEYİ BAŞLAT", command=self.start_thread).pack(pady=10)

    def start_thread(self):
        thread = threading.Thread(target=self.download)
        thread.start()

    def download(self):
        url = self.url_entry.get()
        filename = self.name_entry.get()
        
        if not url:
            messagebox.showerror("Hata", "URL boş olamaz!")
            return

        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }

        try:
            self.status_label.config(text="Durum: Bağlanılıyor...")
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.progress['value'] = percent
                            self.status_label.config(text=f"Durum: %{int(percent)} indirildi...")
            
            messagebox.showinfo("Başarılı", f"{filename} başarıyla indirildi!")
            self.status_label.config(text="Durum: Tamamlandı")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir sorun oluştu: {str(e)}")
            self.status_label.config(text="Durum: Hata!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShadowDownloader(root)
    root.mainloop()
