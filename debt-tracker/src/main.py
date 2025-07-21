import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tracker import DebtTracker
from datetime import datetime

class LoginScreen(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Giriş Ekranı")
        self.geometry("340x220")
        self.configure(bg="#F0F4F8")
        self.resizable(False, False)
        self.on_success = on_success

        tk.Label(self, text="Kullanıcı Adı:", bg="#F0F4F8", font=("Segoe UI", 13)).pack(pady=(18,6))
        self.username_entry = ttk.Entry(self, width=25, font=("Segoe UI", 13))
        self.username_entry.pack()
        self.username_entry.insert(0, "admin")
        self.username_entry.config(state="readonly")

        tk.Label(self, text="Şifre:", bg="#F0F4F8", font=("Segoe UI", 13)).pack(pady=6)
        self.password_entry = ttk.Entry(self, width=25, show="*", font=("Segoe UI", 13))
        self.password_entry.pack()

        ttk.Button(self, text="Giriş Yap", command=self.check_login).pack(pady=22)
        self.password_entry.bind("<Return>", lambda event: self.check_login())

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "admin" and password == "1":
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış!", parent=self)

class DebtTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logs = []
        self.load_logs()
        self.withdraw()
        LoginScreen(self, self.start_app)
        self.bind("<Configure>", self.on_resize)

    def load_logs(self):
        try:
            with open("teknik_detaylar.log", "r", encoding="utf-8") as f:
                self.logs = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.logs = []

    def add_log(self, text):
        self.logs.append(text)
        with open("teknik_detaylar.log", "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def start_app(self):
        self.deiconify()
        self.title("Bakkal Borç Takip")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.configure(bg="#F0F4F8")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Segoe UI", 15, "bold"), padding=[24, 12], background="#E3EAF2")
        style.configure("TButton", font=("Segoe UI", 13), padding=10, background="#E3EAF2")
        style.configure("TEntry", font=("Segoe UI", 13), padding=8)
        style.configure("TLabel", font=("Segoe UI", 13), background="#F0F4F8")
        style.configure("Treeview", font=("Segoe UI", 13), rowheight=32, background="#F8FAFC", fieldbackground="#F8FAFC")
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"), background="#E3EAF2")
        style.map("Treeview", background=[("selected", "#D6EAF8")])

        self.debt_tracker = DebtTracker()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=40, pady=30)

        self.customer_frame = tk.Frame(self.notebook, bg="#F0F4F8")
        self.notebook.add(self.customer_frame, text="Borç Listesi")
        self.setup_debt_list_ui()

        self.add_frame = tk.Frame(self.notebook, bg="#F0F4F8")
        self.notebook.add(self.add_frame, text="Borç Ekle")
        self.setup_add_debt_ui()

        self.report_frame = tk.Frame(self.notebook, bg="#F0F4F8")
        self.notebook.add(self.report_frame, text="Raporlar")
        self.setup_report_ui()
        self.list_debts()

    def on_resize(self, event):
        w, h = self.winfo_width(), self.winfo_height()
        scale = max(min(w / 1000, h / 700), 0.8)
        font_size = int(13 * scale)
        heading_size = int(22 * scale)
        row_height = int(32 * scale)
        pad = int(12 * scale)
        style = ttk.Style(self)
        style.configure("TNotebook.Tab", font=("Segoe UI", max(13, int(15*scale)), "bold"), padding=[int(24*scale), pad])
        style.configure("TButton", font=("Segoe UI", font_size), padding=pad)
        style.configure("TEntry", font=("Segoe UI", font_size), padding=int(8*scale))
        style.configure("TLabel", font=("Segoe UI", font_size), background="#F0F4F8")
        style.configure("Treeview", font=("Segoe UI", font_size), rowheight=row_height)
        style.configure("Treeview.Heading", font=("Segoe UI", max(13, int(14*scale)), "bold"), background="#E3EAF2")

    def time_ago(self, date_str):
        now = datetime.now()
        try:
            debt_time = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
        except Exception:
            return ""
        diff = now - debt_time
        minutes = int(diff.total_seconds() // 60)
        hours = int(minutes // 60)
        days = int(hours // 24)
        weeks = int(days // 7)
        months = int(days // 30)

        if minutes < 60:
            return f"{minutes} dakika önce"
        elif hours < 24:
            return f"{hours} saat önce"
        elif days < 7:
            return f"{days} gün önce"
        elif weeks < 4:
            return f"{weeks} hafta önce"
        else:
            return f"{months} ay önce"

    def setup_debt_list_ui(self):
        self.debt_label = tk.Label(self.customer_frame, text="Borçlar", font=("Segoe UI", 22, "bold"), bg="#F0F4F8")
        self.debt_label.pack(pady=12)
        columns = ("name", "amount", "desc", "date", "zaman")
        self.tree = ttk.Treeview(self.customer_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Borçlu Adı")
        self.tree.heading("amount", text="Miktar (TL)")
        self.tree.heading("desc", text="Açıklama")
        self.tree.heading("date", text="Tarih")
        self.tree.heading("zaman", text="Eklenme Süresi")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("amount", width=120, anchor="center")
        self.tree.column("desc", width=300, anchor="w")
        self.tree.column("date", width=200, anchor="e")
        self.tree.column("zaman", width=140, anchor="center")
        self.tree.pack(pady=10, fill="x", padx=20)

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.btn_frame = tk.Frame(self.customer_frame, bg="#F0F4F8")
        self.btn_frame.pack(pady=18)
        ttk.Button(self.btn_frame, text="Borçları Listele", command=self.list_debts).grid(row=0, column=0, padx=8)
        ttk.Button(self.btn_frame, text="Borç Ara", command=self.search_debt).grid(row=0, column=1, padx=8)
        ttk.Button(self.btn_frame, text="Seçili Borcu Sil", command=self.delete_debt).grid(row=0, column=2, padx=8)
        ttk.Button(self.btn_frame, text="Seçili Borcu Düzenle", command=self.edit_debt).grid(row=0, column=3, padx=8)

    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if item_id and col == "#3":
            idx = self.tree.index(item_id)
            debts = self.debt_tracker.get_debts()
            debt = debts[idx]
            self.open_desc_window(debt)

    def open_desc_window(self, debt):
        desc_win = tk.Toplevel(self)
        desc_win.title("Açıklama")
        desc_win.geometry("450x280")
        desc_win.configure(bg="#F0F4F8")
        desc_win.resizable(False, False)
        desc_win.attributes("-toolwindow", True)

        tk.Label(desc_win, text="Açıklama (Kapatınca otomatik kaydedilir)", bg="#F0F4F8", font=("Segoe UI", 11)).pack(pady=(12,0))
        text_box = tk.Text(desc_win, font=("Segoe UI", 14), bg="#F8FAFC", wrap="word", height=8)
        text_box.pack(expand=True, fill="both", padx=18, pady=(8,18))
        text_box.insert("1.0", debt[3])

        def on_close():
            new_desc = text_box.get("1.0", "end-1c")
            self.debt_tracker.edit_debt(debt[0], debt[1], debt[2], new_desc, debt[4])
            self.list_debts()
            desc_win.destroy()

        desc_win.protocol("WM_DELETE_WINDOW", on_close)

    def setup_add_debt_ui(self):
        tk.Label(self.add_frame, text="Yeni Borç Ekle", font=("Segoe UI", 22, "bold"), bg="#F0F4F8").pack(pady=12)
        form_frame = tk.Frame(self.add_frame, bg="#F0F4F8")
        form_frame.pack(pady=24)

        ttk.Label(form_frame, text="Borçlu Adı:", font=("Segoe UI", 13)).grid(row=0, column=0, sticky="e", pady=10)
        self.name_entry = ttk.Entry(form_frame, width=32, font=("Segoe UI", 13))
        self.name_entry.grid(row=0, column=1, pady=10)

        ttk.Label(form_frame, text="Borç Miktarı:", font=("Segoe UI", 13)).grid(row=1, column=0, sticky="e", pady=10)
        self.amount_entry = ttk.Entry(form_frame, width=32, font=("Segoe UI", 13))
        self.amount_entry.grid(row=1, column=1, pady=10)

        ttk.Label(form_frame, text="Açıklama:", font=("Segoe UI", 13)).grid(row=2, column=0, sticky="e", pady=10)
        self.desc_entry = ttk.Entry(form_frame, width=32, font=("Segoe UI", 13))
        self.desc_entry.grid(row=2, column=1, pady=10)

        ttk.Button(self.add_frame, text="Borç Ekle", command=self.add_debt).pack(pady=18)

    def setup_report_ui(self):
        tk.Label(self.report_frame, text="Raporlar", font=("Segoe UI", 22, "bold"), bg="#F0F4F8").pack(pady=12)
        ttk.Button(self.report_frame, text="Toplam Borç", command=self.show_total_debt).pack(pady=12)
        ttk.Button(self.report_frame, text="Tarihe Göre Borçlar", command=self.show_debt_by_date).pack(pady=12)
        ttk.Button(self.report_frame, text="Borçları Dışa Aktar (TXT)", command=self.export_debts).pack(pady=12)
        ttk.Button(self.report_frame, text="Teknik Detaylar", command=self.show_logs).pack(pady=12)
        ttk.Button(self.report_frame, text="Tüm Kayıtları Sil", command=self.delete_all_data).pack(pady=12)
        ttk.Button(self.report_frame, text="Borçlu Listesi Sıralama", command=self.show_sorted_debtors).pack(pady=12)

    def add_debt(self):
        name = self.name_entry.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Hata", "Borç miktarı sayı olmalı!")
            return
        desc = self.desc_entry.get()
        date = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.debt_tracker.add_debt(name, amount, desc, date)
        self.list_debts()
        messagebox.showinfo("Başarılı", "Borç eklendi!")
        self.add_log(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Borç eklendi: {name}, {amount} TL")
        self.name_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def list_debts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for debt in self.debt_tracker.get_debts():
            first_line = debt[3].split('\n')[0]
            zaman = self.time_ago(debt[4])
            self.tree.insert("", "end", values=(debt[1], f"{debt[2]:.2f}", first_line, debt[4], zaman))

    def show_total_debt(self):
        debts = self.debt_tracker.get_debts()
        total = sum(d[2] for d in debts)
        borclu_sayisi = len(set(d[1] for d in debts))
        en_buyuk = max(debts, key=lambda x: x[2], default=None)
        en_kucuk = min(debts, key=lambda x: x[2], default=None)
        ortalama = total / len(debts) if debts else 0
        msg = f"Toplam Borç: {total:.2f} TL\nBorçlu Sayısı: {borclu_sayisi}\n"
        if en_buyuk:
            msg += f"En Büyük Borç: {en_buyuk[1]} - {en_buyuk[2]:.2f} TL\n"
        if en_kucuk:
            msg += f"En Küçük Borç: {en_kucuk[1]} - {en_kucuk[2]:.2f} TL\n"
        msg += f"Ortalama Borç: {ortalama:.2f} TL"
        messagebox.showinfo("Toplam Borç", msg)

    def search_debt(self):
        query = simpledialog.askstring("Borç Ara", "Borçlu adı veya açıklama girin:")
        results = self.debt_tracker.search_debt(query)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for debt in results:
            zaman = self.time_ago(debt[4])
            self.tree.insert("", "end", values=(debt[1], f"{debt[2]:.2f}", debt[3], debt[4], zaman))

    def delete_debt(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Onay", "Seçili borcu silmek istediğinize emin misiniz?"):
                idx = self.tree.index(selected[0])
                debts = self.debt_tracker.get_debts()
                debt_id = debts[idx][0]
                self.add_log(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Borç silindi: {debts[idx][1]}, {debts[idx][2]} TL")
                self.debt_tracker.delete_debt(debt_id)
                self.list_debts()
    
    def edit_debt(self):
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            debts = self.debt_tracker.get_debts()
            debt = debts[idx]

            edit_win = tk.Toplevel(self)
            edit_win.title("Borcu Düzenle")
            edit_win.geometry("420x320")
            edit_win.configure(bg="#F0F4F8")

            tk.Label(edit_win, text="Borçlu Adı:", bg="#F0F4F8", font=("Segoe UI", 13)).pack(pady=8)
            name_entry = ttk.Entry(edit_win, width=32, font=("Segoe UI", 13))
            name_entry.pack()
            name_entry.insert(0, debt[1])

            tk.Label(edit_win, text="Borç Miktarı:", bg="#F0F4F8", font=("Segoe UI", 13)).pack(pady=8)
            amount_entry = ttk.Entry(edit_win, width=32, font=("Segoe UI", 13))
            amount_entry.pack()
            amount_entry.insert(0, str(debt[2]))

            tk.Label(edit_win, text="Açıklama:", bg="#F0F4F8", font=("Segoe UI", 13)).pack(pady=8)
            desc_entry = ttk.Entry(edit_win, width=32, font=("Segoe UI", 13))
            desc_entry.pack()
            desc_entry.insert(0, debt[3])

            tk.Label(edit_win, text="Tarih:", bg="#F0F4F8", font=("Segoe UI", 13)).pack(pady=8)
            date_entry = ttk.Entry(edit_win, width=32, font=("Segoe UI", 13))
            date_entry.pack()
            date_entry.insert(0, debt[4])

            def save_changes():
                name = name_entry.get()
                try:
                    amount = float(amount_entry.get())
                except ValueError:
                    messagebox.showerror("Hata", "Borç miktarı sayı olmalı!", parent=edit_win)
                    return
                desc = desc_entry.get()
                date = date_entry.get()
                self.debt_tracker.edit_debt(debt[0], name, amount, desc, date)
                self.list_debts()
                self.add_log(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Borç düzenlendi: {name}, {amount} TL")
                edit_win.destroy()

            ttk.Button(edit_win, text="Kaydet", command=save_changes).pack(pady=18)

    def show_debt_by_date(self):
        debts = self.debt_tracker.get_debts()
        dates = {}
        for debt in debts:
            date = debt[4].split(" ")[0]
            dates.setdefault(date, []).append(debt)
        msg = ""
        for date, items in dates.items():
            msg += f"{date}:\n"
            for d in items:
                msg += f"  {d[1]} - {d[2]:.2f} TL\n"
        messagebox.showinfo("Tarihe Göre Borçlar", msg if msg else "Kayıt yok.")

    def export_debts(self):
        debts = self.debt_tracker.get_debts()
        try:
            with open("borclar.txt", "w", encoding="utf-8") as f:
                for debt in debts:
                    f.write(f"{debt[1]} | {debt[2]:.2f} TL | {debt[3]} | {debt[4]}\n")
            messagebox.showinfo("Dışa Aktarma", "Borçlar borclar.txt dosyasına kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dışa aktarma başarısız: {e}")

    def show_logs(self):
        if not self.logs:
            messagebox.showinfo("Teknik Detaylar", "Henüz işlem kaydı yok.")
        else:
            log_text = "\n".join(self.logs)
            log_win = tk.Toplevel(self)
            log_win.title("Teknik Detaylar")
            log_win.geometry("520x420")
            log_win.configure(bg="#F0F4F8")
            text_box = tk.Text(log_win, font=("Segoe UI", 12), bg="#F8FAFC", wrap="word")
            text_box.pack(expand=True, fill="both", padx=16, pady=16)
            text_box.insert("1.0", log_text)
            text_box.config(state="disabled")

    def delete_all_data(self):
        if messagebox.askyesno("Dikkat!", "Tüm borç ve işlem kayıtlarını silmek istediğinize emin misiniz?"):
            self.debt_tracker.delete_all_debts()
            self.logs = []
            with open("teknik_detaylar.log", "w", encoding="utf-8") as f:
                f.write("")
            self.load_logs()
            self.list_debts()
            messagebox.showinfo("Silindi", "Tüm veriler silindi.")

    def show_sorted_debtors(self):
        debts = self.debt_tracker.get_debts()
        borc_dict = {}
        for d in debts:
            borc_dict[d[1]] = borc_dict.get(d[1], 0) + d[2]

        sort_win = tk.Toplevel(self)
        sort_win.title("Sıralama Seç")
        sort_win.geometry("320x180")
        sort_win.configure(bg="#F0F4F8")
        tk.Label(sort_win, text="Sıralama Türü Seçin:", font=("Segoe UI", 13), bg="#F0F4F8").pack(pady=12)

        def show_result(sort_type):
            sort_win.destroy()
            if sort_type == "azdan çoka":
                sorted_borclular = sorted(borc_dict.items(), key=lambda x: x[1])
            elif sort_type == "çoktan aza":
                sorted_borclular = sorted(borc_dict.items(), key=lambda x: x[1], reverse=True)
            elif sort_type == "tarihe göre":
                last_dates = {d[1]: d[4] for d in debts}
                sorted_borclular = sorted(last_dates.items(), key=lambda x: datetime.strptime(x[1], "%d.%m.%Y %H:%M"), reverse=True)
            msg = ""
            if sort_type in ["azdan çoka", "çoktan aza"]:
                for i, (isim, toplam) in enumerate(sorted_borclular, 1):
                    msg += f"{i}. {isim}: {toplam:.2f} TL\n"
            else:
                for i, (isim, tarih) in enumerate(sorted_borclular, 1):
                    msg += f"{i}. {isim}: Son borç tarihi {tarih}\n"
            messagebox.showinfo("Borçlu Listesi", msg if msg else "Kayıt yok.")

        ttk.Button(sort_win, text="Azdan Çoka", command=lambda: show_result("azdan çoka")).pack(pady=8)
        ttk.Button(sort_win, text="Çoktan Aza", command=lambda: show_result("çoktan aza")).pack(pady=8)
        ttk.Button(sort_win, text="Tarihe Göre", command=lambda: show_result("tarihe göre")).pack(pady=8)

if __name__ == "__main__":
    app = DebtTrackerApp()
    app.mainloop()