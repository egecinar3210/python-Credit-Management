import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tracker import DebtTracker
from datetime import datetime

class LoginScreen(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Giriş Ekranı")
        self.geometry("300x180")
        self.configure(bg="#F5F6FA")
        self.resizable(False, False)
        self.on_success = on_success

        tk.Label(self, text="Kullanıcı Adı:", bg="#F5F6FA", font=("Arial", 12)).pack(pady=8)
        self.username_entry = ttk.Entry(self, width=25)
        self.username_entry.pack()
        self.username_entry.insert(0, "admin")
        self.username_entry.config(state="readonly")

        tk.Label(self, text="Şifre:", bg="#F5F6FA", font=("Arial", 12)).pack(pady=8)
        self.password_entry = ttk.Entry(self, width=25, show="*")
        self.password_entry.pack()

        ttk.Button(self, text="Giriş Yap", command=self.check_login).pack(pady=15)
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
        self.withdraw()  # Ana pencereyi gizle
        LoginScreen(self, self.start_app)

    def start_app(self):
        self.deiconify()  # Ana pencereyi göster
        self.title("Bakkal Borç Takip")
        self.geometry("850x550")
        self.configure(bg="#F5F6FA")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Arial", 14, "bold"), padding=[20, 10])
        style.configure("TButton", font=("Arial", 12), padding=10)
        style.configure("TEntry", font=("Arial", 12), padding=10)
        style.configure("TLabel", font=("Arial", 12), background="#F5F6FA")
        style.configure("Treeview", font=("Arial", 12), rowheight=28)
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        style.map("Treeview", background=[("selected", "#D6EAF8")])

        self.debt_tracker = DebtTracker()

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both", padx=30, pady=30)

        # Borç Listesi Sekmesi
        self.customer_frame = tk.Frame(notebook, bg="#F5F6FA")
        notebook.add(self.customer_frame, text="Borç Listesi")
        self.setup_debt_list_ui()

        # Borç Ekle Sekmesi
        self.add_frame = tk.Frame(notebook, bg="#F5F6FA")
        notebook.add(self.add_frame, text="Borç Ekle")
        self.setup_add_debt_ui()

        # Raporlar Sekmesi
        self.report_frame = tk.Frame(notebook, bg="#F5F6FA")
        notebook.add(self.report_frame, text="Raporlar")
        self.setup_report_ui()
        self.list_debts() # borçları başlangıçta listele

    def setup_debt_list_ui(self):
        tk.Label(self.customer_frame, text="Borçlar", font=("Arial", 20, "bold"), bg="#F5F6FA").pack(pady=10)
        columns = ("name", "amount", "desc", "date")
        self.tree = ttk.Treeview(self.customer_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Borçlu Adı")
        self.tree.heading("amount", text="Miktar (TL)")
        self.tree.heading("desc", text="Açıklama")
        self.tree.heading("date", text="Tarih")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("amount", width=100, anchor="center")
        self.tree.column("desc", width=250, anchor="w")
        self.tree.column("date", width=180, anchor="e")
        self.tree.pack(pady=10, fill="x", padx=10)

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        btn_frame = tk.Frame(self.customer_frame, bg="#F5F6FA")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Borçları Listele", command=self.list_debts).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Borç Ara", command=self.search_debt).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Seçili Borcu Sil", command=self.delete_debt).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Seçili Borcu Düzenle", command=self.edit_debt).grid(row=0, column=3, padx=5)

    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if item_id and col == "#3":  # "#3" açıklama sütunu
            idx = self.tree.index(item_id)
            debts = self.debt_tracker.get_debts()
            debt = debts[idx]
            self.open_desc_window(debt)

    def open_desc_window(self, debt):
        desc_win = tk.Toplevel(self)
        desc_win.title("Açıklama")
        desc_win.geometry("425x275")  # Bakkal ekranının yarısı kadar
        desc_win.configure(bg="#F5F6FA")
        desc_win.resizable(False, False)  # Boyut değiştirme kapalı
        desc_win.attributes("-toolwindow", True)  # Sadece kapatma tuşu (Windows)

        text_box = tk.Text(desc_win, font=("Courier New", 14), bg="#FDFDFD", wrap="word")
        text_box.pack(expand=True, fill="both", padx=20, pady=(20,20))
        text_box.insert("1.0", debt[3])

        tk.Label(desc_win, text="Kapatınca otomatik kaydedilir.", bg="#F5F6FA", font=("Arial", 10)).pack(pady=(5,0))

        def on_close():
            new_desc = text_box.get("1.0", "end-1c")
            self.debt_tracker.edit_debt(debt[0], debt[1], debt[2], new_desc, debt[4])
            self.list_debts()
            self.logs.append(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Açıklama güncellendi: {debt[1]}")
            desc_win.destroy()

        desc_win.protocol("WM_DELETE_WINDOW", on_close)

    def setup_add_debt_ui(self):
        tk.Label(self.add_frame, text="Yeni Borç Ekle", font=("Arial", 20, "bold"), bg="#F5F6FA").pack(pady=10)
        form_frame = tk.Frame(self.add_frame, bg="#F5F6FA")
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Borçlu Adı:").grid(row=0, column=0, sticky="e", pady=8)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=8)

        ttk.Label(form_frame, text="Borç Miktarı:").grid(row=1, column=0, sticky="e", pady=8)
        self.amount_entry = ttk.Entry(form_frame, width=30)
        self.amount_entry.grid(row=1, column=1, pady=8)

        ttk.Label(form_frame, text="Açıklama:").grid(row=2, column=0, sticky="e", pady=8)
        self.desc_entry = ttk.Entry(form_frame, width=30)
        self.desc_entry.grid(row=2, column=1, pady=8)

        ttk.Button(self.add_frame, text="Borç Ekle", command=self.add_debt).pack(pady=15)

    def setup_report_ui(self):
        tk.Label(self.report_frame, text="Raporlar", font=("Arial", 20, "bold"), bg="#F5F6FA").pack(pady=10)
        ttk.Button(self.report_frame, text="Toplam Borç", command=self.show_total_debt).pack(pady=10)
        ttk.Button(self.report_frame, text="Tarihe Göre Borçlar", command=self.show_debt_by_date).pack(pady=10)
        ttk.Button(self.report_frame, text="Borçları Dışa Aktar (TXT)", command=self.export_debts).pack(pady=10)
        ttk.Button(self.report_frame, text="Teknik Detaylar", command=self.show_logs).pack(pady=10)
        ttk.Button(self.report_frame, text="Tüm Kayıtları Sil", command=self.delete_all_data).pack(pady=10)

    def add_debt(self):
        name = self.name_entry.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Hata", "Borç miktarı sayı olmalı!")
            return
        desc = self.desc_entry.get()
        date = datetime.now().strftime("%d.%m.%Y %H:%M")  # Otomatik tarih ve saat
        self.debt_tracker.add_debt(name, amount, desc, date)
        self.list_debts()
        messagebox.showinfo("Başarılı", "Borç eklendi!")
        self.logs.append(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Borç eklendi: {name}, {amount} TL")
        self.name_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def list_debts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for debt in self.debt_tracker.get_debts():
            # Açıklamanın sadece ilk satırını göster
            first_line = debt[3].split('\n')[0]
            self.tree.insert("", "end", values=(debt[1], f"{debt[2]:.2f}", first_line, debt[4]))

    def show_total_debt(self):
        total = self.debt_tracker.calculate_total_debt()
        messagebox.showinfo("Toplam Borç", f"Toplam Borç: {total} TL")

    def search_debt(self):
        query = simpledialog.askstring("Borç Ara", "Borçlu adı veya açıklama girin:")
        results = self.debt_tracker.search_debt(query)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for debt in results:
            self.tree.insert("", "end", values=(debt[1], f"{debt[2]:.2f}", debt[3], debt[4]))

    def delete_debt(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Onay", "Seçili borcu silmek istediğinize emin misiniz?"):
                idx = self.tree.index(selected[0])
                debts = self.debt_tracker.get_debts()
                debt_id = debts[idx][0]
                self.logs.append(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Borç silindi: {debts[idx][1]}, {debts[idx][2]} TL")
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
            edit_win.geometry("400x300")
            edit_win.configure(bg="#F5F6FA")

            tk.Label(edit_win, text="Borçlu Adı:", bg="#F5F6FA", font=("Arial", 12)).pack(pady=5)
            name_entry = ttk.Entry(edit_win, width=30)
            name_entry.pack()
            name_entry.insert(0, debt[1])

            tk.Label(edit_win, text="Borç Miktarı:", bg="#F5F6FA", font=("Arial", 12)).pack(pady=5)
            amount_entry = ttk.Entry(edit_win, width=30)
            amount_entry.pack()
            amount_entry.insert(0, str(debt[2]))

            tk.Label(edit_win, text="Açıklama:", bg="#F5F6FA", font=("Arial", 12)).pack(pady=5)
            desc_entry = ttk.Entry(edit_win, width=30)
            desc_entry.pack()
            desc_entry.insert(0, debt[3])

            tk.Label(edit_win, text="Tarih:", bg="#F5F6FA", font=("Arial", 12)).pack(pady=5)
            date_entry = ttk.Entry(edit_win, width=30)
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
                self.logs.append(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Borç düzenlendi: {name}, {amount} TL")
                edit_win.destroy()

            ttk.Button(edit_win, text="Kaydet", command=save_changes).pack(pady=15)

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
        if not hasattr(self, "logs") or not self.logs:
            messagebox.showinfo("Teknik Detaylar", "Henüz işlem kaydı yok.")
        else:
            log_text = "\n".join(self.logs)
            log_win = tk.Toplevel(self)
            log_win.title("Teknik Detaylar")
            log_win.geometry("500x400")
            log_win.configure(bg="#F5F6FA")
            text_box = tk.Text(log_win, font=("Courier New", 11), bg="#FDFDFD", wrap="word")
            text_box.pack(expand=True, fill="both", padx=10, pady=10)
            text_box.insert("1.0", log_text)
            text_box.config(state="disabled")

    def delete_all_data(self):
        if messagebox.askyesno("Dikkat!", "Tüm borç ve işlem kayıtlarını silmek istediğinize emin misiniz?"):
            self.debt_tracker.delete_all_debts()  # tracker.py'de bu fonksiyon olmalı!
            if hasattr(self, "logs"):
                self.logs.append(f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - Tüm kayıtlar silindi.")
            self.list_debts()
            messagebox.showinfo("Silindi", "Tüm veriler silindi.")

if __name__ == "__main__":
    app = DebtTrackerApp()
    app.mainloop()