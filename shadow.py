import tkinter as tk
from tkinter import ttk, messagebox
import requests, threading, os, json, random, time, subprocess, re

# --- 1. GİZLİLİK VE GLOBAL AYARLAR (Madde 7, 11) ---
class ShadowGlobals:
    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen 7.0) SamsungBrowser/6.4 TV Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15"
    ]
    HEADERS = {"User-Agent": random.choice(UA_LIST), "Accept": "*/*"}

# --- 2. ANA MOTOR (Madde 2, 5, 16) ---
class ShadowEngine:
    @staticmethod
    def is_youtube(url):
        return any(x in url for x in ["youtube.com", "youtu.be"])

    @staticmethod
    def parse_xtream(url):
        """Xtream Codes linkini analiz eder (Madde 2)"""
        # Örnek: http://url:port/get.php?username=X&password=Y&type=m3u_plus
        if "get.php" in url and "username" in url:
            return "XTREAM_PLAYLIST"
        return "DIRECT"

# --- 3. PROFESYONEL ARAYÜZ (Madde 4, 6, 12) ---
class ShadowStreamUltimate:
    def __init__(self, root):
        self.root = root
        self.root.title("ShadowStream Ultimate v4.0 - PRO")
        self.root.geometry("1150x750")
        self.root.configure(bg='#0A0A0A')
        
        self.tasks = []
        self.night_mode = False
        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # Yan Menü (Dark Sidebar)
        self.side = tk.Frame(self.root, bg='#111', width=240)
        self.side.pack(side='left', fill='y')
        
        tk.Label(self.side, text="SHADOW STREAM", fg='#00A2FF', bg='#111', font=('Impact', 22)).pack(pady=30)
        
        # Sekmeler
        for icon, name in [("⬇", "İndirmeler"), ("📺", "IPTV Paneli"), ("⭐", "Favoriler"), ("🌙", "Gece Modu")]:
            cmd = self.toggle_night if name == "Gece Modu" else None
            tk.Button(self.side, text=f"{icon} {name}", fg='#888', bg='#111', relief='flat', font=('Segoe UI', 11), 
                      anchor='w', padx=30, pady=15, command=cmd).pack(fill='x')

        # Ana Panel
        self.container = tk.Frame(self.root, bg='#0A0A0A')
        self.container.pack(side='right', fill='both', expand=True, padx=20, pady=20)

        # Link Giriş Alanı
        self.url_var = tk.StringVar()
        entry_frame = tk.Frame(self.container, bg='#1A1A1A', pady=15, padx=15)
        entry_frame.pack(fill='x')
        
        tk.Entry(entry_frame, textvariable=self.url_var, bg='#222', fg='white', border=0, font=('Arial', 12)).pack(side='left', fill='x', expand=True, padx=(0, 15))
        tk.Button(entry_frame, text="ANALİZ ET VE BAŞLAT", bg='#0078D4', fg='white', relief='flat', font=('Arial', 10, 'bold'), padx=20, command=self.process_link).pack(side='right')

        # İndirme Listesi (Treeview)
        cols = ("ID", "Dosya/Kanal Adı", "Boyut", "İlerleme", "Hız", "Durum")
        self.tree = ttk.Treeview(self.container, columns=cols, show='headings')
        for col in cols: 
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("Dosya/Kanal Adı", width=350)
        self.tree.pack(fill='both', expand=True, pady=20)

    def process_link(self):
        url = self.url_var.get().strip()
        if not url: return

        # Akıllı Algılama Sistemi
        if ShadowEngine.is_youtube(url):
            self.add_task(url, "YouTube Video", "YouTube")
        elif ShadowEngine.parse_xtream(url) == "XTREAM_PLAYLIST":
            self.handle_playlist(url)
        else:
            name = url.split('/')[-1].split('?')[0] or "Video_Stream"
            self.add_task(url, name, "Direct")
        
        self.url_var.set("")

    def handle_playlist(self, url):
        """M3U Playlistini parçalara böler (Madde 2)"""
        messagebox.showinfo("IPTV", "Xtream Playlist algılandı! İçerik analiz ediliyor...")
        try:
            res = requests.get(url, headers=ShadowGlobals.HEADERS, timeout=10)
            lines = res.text.split('\n')
            count = 0
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF") and i+1 < len(lines):
                    name = line.split(',')[-1].strip()
                    stream_url = lines[i+1].strip()
                    if count < 5: # Test için ilk 5 kanalı ekle
                        self.add_task(stream_url, name, "IPTV")
                        count += 1
            messagebox.showinfo("Başarılı", f"{count} kanal indirme kuyruğuna alındı!")
        except:
            messagebox.showerror("Hata", "Playlist çözülemedi!")

    def add_task(self, url, name, cat):
        task = {"id": random.randint(100, 999), "url": url, "name": name, "cat": cat, 
                "prog": 0, "speed": "0 MB/s", "status": "Bekliyor", "size": "Hesaplanıyor"}
        self.tasks.append(task)
        threading.Thread(target=self.download_logic, args=(task,), daemon=True).start()

    def download_logic(self, task):
        # Madde 16: YouTube için yt-dlp.exe kontrolü
        if task['cat'] == "YouTube":
            ytdl_path = os.path.join(os.getcwd(), "Tools", "yt-dlp.exe")
            if os.path.exists(ytdl_path):
                task['status'] = "Motor: yt-dlp"
                subprocess.run([ytdl_path, "-o", f"./Downloads/{task['name']}.mp4", task['url']], creationflags=subprocess.CREATE_NO_WINDOW)
                task['prog'] = 100; task['status'] = "TAMAMLANDI"
                return
            else:
                task['status'] = "Hata: yt-dlp.exe Yok"
                return

        # Madde 5 & 11: Standart ve IPTV İndirme
        try:
            res = requests.get(task['url'], headers=ShadowGlobals.HEADERS, stream=True, timeout=15)
            total = int(res.headers.get('content-length', 0))
            task['size'] = f"{total/1024/1024:.1f} MB" if total > 0 else "Live Stream"
            
            save_path = f"./Downloads/{task['name'].replace(' ', '_')}.ts"
            with open(save_path, 'wb') as f:
                start_time = time.time()
                downloaded = 0
                for chunk in res.iter_content(chunk_size=1024*256):
                    if chunk:
                        # Madde 4: Gece Modu (Hız Sınırlama)
                        if self.night_mode: time.sleep(0.05)
                        
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            task['speed'] = f"{(downloaded/1024/1024)/elapsed:.1f} MB/s"
                            task['prog'] = int((downloaded/total)*100) if total > 0 else 50
                            task['status'] = "İndiriliyor"
            task['status'] = "TAMAMLANDI"
        except:
            task['status'] = "Hata: Bağlantı Kesildi"

    def toggle_night(self):
        self.night_mode = not self.night_mode
        state = "AKTİF" if self.night_mode else "KAPALI"
        messagebox.showinfo("Gece Modu", f"Hız sınırlayıcı (Madde 4): {state}")

    def update_loop(self):
        self.tree.delete(*self.tree.get_children())
        for t in self.tasks:
            self.tree.insert("", "end", values=(t['id'], t['name'], t['size'], f"%{t['prog']}", t['speed'], t['status']))
        self.root.after(1000, self.update_loop)

if __name__ == "__main__":
    if not os.path.exists("./Downloads"): os.makedirs("./Downloads")
    root = tk.Tk()
    app = ShadowStreamUltimate(root)
    root.mainloop()
