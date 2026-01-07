import tkinter as tk
from tkinter import ttk, messagebox
import requests, threading, os, json, random, time, subprocess, re

class ShadowStreamPro:
    def __init__(self, root):
        self.root = root
        self.root.title("ShadowStream Ultimate v3.0")
        self.root.geometry("1100x700")
        self.root.configure(bg='#0A0A0A')
        self.queue = []
        self.settings = {"night_mode": False, "save_path": "./Downloads"}
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (SMART-TV; Linux; Tizen 7.0) SamsungBrowser/6.4 TV Safari/537.36",
            "Mozilla/5.0 (PlayStation 5 8.20) AppleWebKit/605.1.15 Safari/605.1.15"
        ]
        if not os.path.exists("./Downloads"): os.makedirs("./Downloads")
        self.setup_ui()
        self.refresh_loop()

    def setup_ui(self):
        # Sol Menü
        side = tk.Frame(self.root, bg='#111', width=220)
        side.pack(side='left', fill='y')
        tk.Label(side, text="SHADOW STREAM", fg='#00A2FF', bg='#111', font=('Impact', 18)).pack(pady=25)
        
        btns = [("⬇ İndirmeler", None), ("📺 IPTV Yönetimi", self.parse_iptv), ("🌙 Gece Modu", self.toggle_night)]
        for t, c in btns:
            tk.Button(side, text=t, fg='white', bg='#111', relief='flat', font=('Arial', 10), anchor='w', padx=25, pady=10, command=c).pack(fill='x')

        # Ana Alan
        main = tk.Frame(self.root, bg='#0A0A0A')
        main.pack(side='right', fill='both', expand=True, padx=15, pady=15)

        # Link Girişi
        top = tk.Frame(main, bg='#181818', pady=15, padx=15)
        top.pack(fill='x', pady=(0, 15))
        self.url_var = tk.StringVar()
        tk.Entry(top, textvariable=self.url_var, bg='#222', fg='white', border=0, font=('Arial', 12)).pack(side='left', fill='x', expand=True, padx=(0, 10))
        tk.Button(top, text="ANALİZ ET VE İNDİR", bg='#007ACC', fg='white', relief='flat', command=self.process_link, padx=15).pack(side='right')

        # Liste
        self.tree = ttk.Treeview(main, columns=("Ad", "Boyut", "İlerleme", "Hız", "Durum"), show='headings')
        for c in ("Ad", "Boyut", "İlerleme", "Hız", "Durum"): self.tree.heading(c, text=c); self.tree.column(c, width=120)
        self.tree.column("Ad", width=350)
        self.tree.pack(fill='both', expand=True)

    def process_link(self):
        url = self.url_var.get().strip()
        if not url: return
        
        # YouTube Algılama
        if "youtube.com" in url or "youtu.be" in url:
            name = "YouTube_Video_" + str(random.randint(100,999))
            self.add_task(url, name, "YouTube")
        # M3U/HLS Algılama
        elif ".m3u" in url:
            self.add_task(url, "IPTV_Stream", "HLS")
        else:
            self.add_task(url, url.split('/')[-1] or "Video", "Direct")
        self.url_var.set("")

    def add_task(self, url, name, cat):
        task = {"url": url, "name": name, "cat": cat, "prog": 0, "speed": "0 MB/s", "status": "Bekliyor", "size": "..."}
        self.queue.append(task)
        threading.Thread(target=self.downloader, args=(task,), daemon=True).start()

    def downloader(self, task):
        headers = {"User-Agent": random.choice(self.user_agents), "Referer": "https://google.com"}
        try:
            # YouTube Motoru (yt-dlp)
            if task['cat'] == "YouTube":
                ytdl = os.path.join(os.getcwd(), "Tools", "yt-dlp.exe")
                if os.path.exists(ytdl):
                    task['status'] = "YT-DLP Aktif"
                    cmd = [ytdl, "-o", f"./Downloads/%(title)s.%(ext)s", task['url']]
                    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                    task['status'] = "TAMAMLANDI"; task['prog'] = 100
                    return

            # Standart HTTP / HLS Motoru
            res = requests.get(task['url'], headers=headers, stream=True, timeout=15)
            total = int(res.headers.get('content-length', 0))
            task['size'] = f"{total/(1024*1024):.1f} MB" if total > 0 else "Stream"
            
            dest = os.path.join("./Downloads", task['name'])
            with open(dest, 'wb') as f:
                start = time.time()
                downloaded = 0
                for chunk in res.iter_content(chunk_size=1024*128):
                    if chunk:
                        if self.settings['night_mode']: time.sleep(0.02)
                        f.write(chunk); downloaded += len(chunk)
                        elapsed = time.time() - start
                        if elapsed > 0:
                            task['speed'] = f"{(downloaded/1024/1024)/elapsed:.1f} MB/s"
                            task['prog'] = int((downloaded/total)*100) if total > 0 else 50
                            task['status'] = "İndiriliyor"
            task['status'] = "TAMAMLANDI"
        except: task['status'] = "Hata!"

    def toggle_night(self):
        self.settings['night_mode'] = not self.settings['night_mode']
        messagebox.showinfo("ShadowStream", f"Gece Modu: {'AKTİF' if self.settings['night_mode'] else 'KAPALI'}")

    def parse_iptv(self): messagebox.showinfo("IPTV", "M3U Parser Hazır. URL girildiğinde otomatik ayrıştırılır.")
    def refresh_loop(self):
        self.tree.delete(*self.tree.get_children())
        for t in self.queue: self.tree.insert("", "end", values=(t['name'], t['size'], f"%{t['prog']}", t['speed'], t['status']))
        self.root.after(1000, self.refresh_loop)

if __name__ == "__main__":
    app = ShadowStreamPro(tk.Tk()); app.root.mainloop()
