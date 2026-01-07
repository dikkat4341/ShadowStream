import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import random
import threading
import time
import os
import json
from datetime import datetime

# --- GİZLİLİK VE ANTI-DETECTION MOTORU ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (SMART-TV; Linux; Tizen 7.0) SamsungBrowser/6.4 TV Safari/537.36",
    "Mozilla/5.0 (PlayStation 5 8.20) AppleWebKit/605.1.15 Safari/605.1.15"
]

class DownloadTask:
    def __init__(self, url, filename, save_path, user_agent):
        self.url = url
        self.filename = filename
        self.save_path = save_path
        self.user_agent = user_agent
        self.status = "Bekliyor"
        self.progress = 0
        self.speed = "0 MB/s"
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.stop_event = threading.Event()

class ShadowStreamPro:
    def __init__(self, root):
        self.root = root
        self.root.title("ShadowStream Downloader v1.0 - Professional Portable")
        self.root.geometry("1000x600")
        self.root.configure(bg='#0f0f0f')
        
        self.tasks = []
        self.night_mode = False
        self.setup_ui()
        self.update_ui_loop()

    def setup_ui(self):
        # Sol Menü (Side Panel)
        side_panel = tk.Frame(self.root, bg='#1a1a1a', width=200)
        side_panel.pack(side='left', fill='y')
        
        tk.Label(side_panel, text="SHADOW STREAM", fg='#00d4ff', bg='#1a1a1a', font=('Impact', 18)).pack(pady=20)
        
        menu_items = ["İndirmeler", "M3U/Xtream", "Favoriler", "Geçmiş", "Ayarlar"]
        for item in menu_items:
            btn = tk.Button(side_panel, text=item, fg='white', bg='#1a1a1a', relief='flat', font=('Arial', 10, 'bold'), anchor='w', padx=20)
            btn.pack(fill='x', pady=5)

        # Ana İçerik Alanı
        main_container = tk.Frame(self.root, bg='#0f0f0f')
        main_container.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Üst Bar (URL Ekleme)
        top_bar = tk.Frame(main_container, bg='#1a1a1a', pady=15, padx=15)
        top_bar.pack(fill='x')
        
        self.url_var = tk.StringVar()
        tk.Entry(top_bar, textvariable=self.url_var, bg='#262626', fg='white', border=0, font=('Arial', 11)).pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        tk.Button(top_bar, text="+ KUYRUĞA EKLE", bg='#00d4ff', fg='black', font=('Arial', 9, 'bold'), command=self.add_task, relief='flat', padx=15).pack(side='right')

        # İndirme Tablosu (Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="white", fieldbackground="#1a1a1a", borderwidth=0, rowheight=35)
        style.map("Treeview", background=[('selected', '#00d4ff')], foreground=[('selected', 'black')])

        self.tree = ttk.Treeview(main_container, columns=("Dosya", "Boyut", "İlerleme", "Hız", "Durum"), show='headings')
        self.tree.heading("Dosya", text="DOSYA ADI")
        self.tree.heading("Boyut", text="BOYUT")
        self.tree.heading("İlerleme", text="İLERLEME")
        self.tree.heading("Hız", text="HIZ")
        self.tree.heading("Durum", text="DURUM")
        
        self.tree.column("Dosya", width=250)
        self.tree.column("İlerleme", width=150)
        self.tree.pack(fill='both', expand=True, pady=10)

        # Alt Bar (İstatistikler & Gece Modu)
        status_bar = tk.Frame(main_container, bg='#1a1a1a', height=30)
        status_bar.pack(fill='x', side='bottom')
        
        self.night_btn = tk.Button(status_bar, text="GECE MODU: KAPALI", bg='#333', fg='white', font=('Arial', 8), command=self.toggle_night_mode)
        self.night_btn.pack(side='right', padx=10)

    def toggle_night_mode(self):
        self.night_mode = not self.night_mode
        text = "GECE MODU: AKTİF" if self.night_mode else "GECE MODU: KAPALI"
        color = "#ff8c00" if self.night_mode else "#333"
        self.night_btn.config(text=text, bg=color)

    def add_task(self):
        url = self.url_var.get()
        if not url: return
        
        filename = url.split('/')[-1].split('?')[0] or f"stream_{int(time.time())}.ts"
        ua = random.choice(USER_AGENTS)
        
        task = DownloadTask(url, filename, "./Downloads", ua)
        self.tasks.append(task)
        
        # Tabloya ekle
        item_id = self.tree.insert("", "end", values=(filename, "0 MB", "0%", "0 MB/s", "Hazır"))
        
        # İndirmeyi başlat
        threading.Thread(target=self.download_process, args=(task, item_id), daemon=True).start()
        self.url_var.set("")

    def download_process(self, task, item_id):
        task.status = "İndiriliyor"
        start_time = time.time()
        
        headers = {
            "User-Agent": task.user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }

        try:
            r = requests.get(task.url, headers=headers, stream=True, timeout=20)
            task.total_bytes = int(r.headers.get('content-length', 0))
            
            if not os.path.exists("./Downloads"): os.makedirs("./Downloads")
            path = os.path.join("./Downloads", task.filename)

            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*64):
                    if task.stop_event.is_set(): break
                    
                    # Gece Modu Hız Sınırlama (Throttle)
                    if self.night_mode:
                        time.sleep(0.05) # Yapay gecikme ile hızı düşürür

                    f.write(chunk)
                    task.downloaded_bytes += len(chunk)
                    
                    # İstatistik Güncelleme
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        speed_mb = (task.downloaded_bytes / 1024 / 1024) / elapsed
                        task.speed = f"{speed_mb:.2f} MB/s"
                        task.progress = (task.downloaded_bytes / task.total_bytes) * 100 if task.total_bytes > 0 else 0

            task.status = "Tamamlandı"
        except Exception as e:
            task.status = f"Hata: {str(e)[:15]}"

    def update_ui_loop(self):
        # Tabloyu her 500ms'de bir güncelle
        for i, task in enumerate(self.tasks):
            item_id = self.tree.get_children()[i]
            size_mb = f"{task.total_bytes / 1024 / 1024:.1f} MB"
            self.tree.item(item_id, values=(task.filename, size_mb, f"%{int(task.progress)}", task.speed, task.status))
        
        self.root.after(500, self.update_ui_loop)

if __name__ == "__main__":
    root = tk.Tk()
    # Downloads klasörü yoksa oluştur
    if not os.path.exists("./Downloads"): os.makedirs("./Downloads")
    app = ShadowStreamPro(root)
    root.mainloop()
