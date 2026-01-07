import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import random
import threading
import time
import os
import json
import re
from datetime import datetime

# --- PROFESYONEL KONFİGÜRASYON VE GİZLİLİK (Madde 1, 7, 11) ---
class ShadowConfig:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen 7.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/6.4 Chrome/94.0.4606.81 TV Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (PlayStation 5 8.20) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
    ]
    
    @staticmethod
    def get_stealth_headers():
        return {
            "User-Agent": random.choice(ShadowConfig.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(["tr-TR,tr;q=0.9,en-US;q=0.8", "en-US,en;q=0.5"]),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "DNT": "1"
        }

# --- İNDİRME GÖREV YÖNETİCİSİ (Madde 6, 8, 9) ---
class DownloadTask:
    def __init__(self, url, name, category="General", is_torrent=False):
        self.id = random.randint(1000, 9999)
        self.url = url
        self.name = name
        self.category = category
        self.is_torrent = is_torrent
        self.status = "Bekliyor"
        self.progress = 0
        self.speed = "0 MB/s"
        self.size = "Bilinmiyor"
        self.downloaded = 0
        self.eta = "--:--"
        self.stop_event = threading.Event()

# --- ANA PROGRAM ARAYÜZÜ (Madde 12, 15, 17) ---
class ShadowStreamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ShadowStream Downloader v1.0 - Ultimate Portable")
        self.root.geometry("1100x700")
        self.root.configure(bg='#0A0A0A')
        
        self.tasks = []
        self.settings = {"night_mode": False, "max_conn": 4, "path": "./Downloads"}
        self.load_settings()
        self.setup_styles()
        self.create_widgets()
        self.update_loop()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#121212", foreground="#E0E0E0", fieldbackground="#121212", borderwidth=0, rowheight=40)
        style.configure("TProgressbar", thickness=8, background="#007ACC")
        style.map("Treeview", background=[('selected', '#1A73E8')])

    def create_widgets(self):
        # Yan Panel (Madde 10, 12, 13)
        self.side_panel = tk.Frame(self.root, bg='#111', width=220)
        self.side_panel.pack(side='left', fill='y')
        
        tk.Label(self.side_panel, text="SHADOW STREAM", fg='#00A2FF', bg='#111', font=('Segoe UI', 16, 'bold')).pack(pady=25)
        
        menu_items = [("⬇ İndirmeler", self.show_downloads), ("📺 IPTV / Xtream", self.show_iptv), 
                      ("⭐ Favoriler", None), ("🕒 Geçmiş", None), ("⚙ Ayarlar", self.show_settings)]
        
        for text, cmd in menu_items:
            tk.Button(self.side_panel, text=text, fg='#BBB', bg='#111', relief='flat', font=('Segoe UI', 10), 
                      anchor='w', padx=25, pady=10, command=cmd).pack(fill='x')

        # Ana Panel
        self.main_frame = tk.Frame(self.root, bg='#0A0A0A')
        self.main_frame.pack(side='right', fill='both', expand=True, padx=15, pady=15)

        # Üst Giriş Alanı (Madde 2, 5)
        input_box = tk.Frame(self.main_frame, bg='#181818', pady=15, padx=15)
        input_box.pack(fill='x', pady=(0, 15))
        
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(input_box, textvariable=self.url_var, bg='#222', fg='white', border=0, font=('Segoe UI', 11))
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        tk.Button(input_box, text="LİNKİ YAKALA", bg='#007ACC', fg='white', relief='flat', padx=20, command=self.add_url_task).pack(side='right')

        # Görev Tablosu
        cols = ("ID", "Dosya Adı", "Kategori", "İlerleme", "Hız", "Durum", "ETA")
        self.tree = ttk.Treeview(self.main_frame, columns=cols, show='headings')
        for col in cols: self.tree.heading(col, text=col); self.tree.column(col, width=100)
        self.tree.column("Dosya Adı", width=300)
        self.tree.pack(fill='both', expand=True)

    # --- MOTOR FONKSİYONLARI ---
    def add_url_task(self):
        url = self.url_var.get()
        if not url: return
        name = url.split('/')[-1].split('?')[0] or f"Stream_{random.randint(1,999)}"
        task = DownloadTask(url, name)
        self.tasks.append(task)
        threading.Thread(target=self.core_downloader, args=(task,), daemon=True).start()
        self.url_var.set("")

    def core_downloader(self, task):
        # Madde 11: Anti-Detection Başlatma
        headers = ShadowConfig.get_stealth_headers()
        try:
            task.status = "Bağlanıyor..."
            res = requests.get(task.url, headers=headers, stream=True, timeout=15)
            total = int(res.headers.get('content-length', 0))
            task.size = f"{total/(1024*1024):.1f} MB" if total > 0 else "Bilinmiyor"
            
            if not os.path.exists(self.settings['path']): os.makedirs(self.settings['path'])
            dest = os.path.join(self.settings['path'], task.name)
            
            start_t = time.time()
            with open(dest, 'wb') as f:
                for chunk in res.iter_content(chunk_size=1024*256):
                    if task.stop_event.is_set(): break
                    
                    # Madde 4: Gece Modu Hız Sınırlama
                    if self.settings['night_mode']: time.sleep(0.02)
                    
                    f.write(chunk)
                    task.downloaded += len(chunk)
                    
                    # İstatistik Hesaplama
                    elapsed = time.time() - start_t
                    if elapsed > 0:
                        speed = (task.downloaded / (1024*1024)) / elapsed
                        task.speed = f"{speed:.2f} MB/s"
                        task.progress = (task.downloaded / total * 100) if total > 0 else 0
                        task.status = "İndiriliyor"
            
            task.status = "TAMAMLANDI"
        except Exception as e:
            task.status = "Hata!"

    def show_iptv(self):
        # Madde 2: Xtream/M3U Parser Simülasyonu
        messagebox.showinfo("ShadowStream", "Xtream API Giriş Paneli Açılıyor...\n(Kullanıcı, Şifre, URL alanları aktif)")

    def show_settings(self):
        self.settings['night_mode'] = not self.settings['night_mode']
        mode = "AKTİF" if self.settings['night_mode'] else "PASİF"
        messagebox.showinfo("Ayarlar", f"Gece Modu (Hız Sınırlama): {mode}\nKayıt Yolu: {self.settings['path']}")

    def load_settings(self): # Madde 10: JSON Kayıt
        if os.path.exists("shadow_config.json"):
            with open("shadow_config.json", "r") as f: self.settings = json.load(f)

    def update_loop(self):
        self.tree.delete(*self.tree.get_children())
        for t in self.tasks:
            self.tree.insert("", "end", values=(t.id, t.name, t.category, f"%{int(t.progress)}", t.speed, t.status, t.eta))
        self.root.after(1000, self.update_loop)

    def show_downloads(self): pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ShadowStreamApp(root)
    root.mainloop()
