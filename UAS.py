import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
import os
import matplotlib
matplotlib.use('TkAgg') 

# OOP CLASSES 
# Encapsulation 
class Workout:
    def __init__(self, date, workout_type, duration, intensity="-"):
        self._date = date
        self._type = workout_type
        self._duration = duration
        self._intensity = intensity

    def get_date(self): return self._date
    def get_type(self): return self._type
    def get_duration(self): return self._duration
    def get_intensity(self): return self._intensity
    
    #polymorphism
    def calculate_calories(self):
        faktor = {
            "Lari": 6, "Jalan Santai": 3, "Bersepeda": 5, "Renang": 7,
            "Yoga": 4, "Skipping": 10, "HIIT": 12
        }
        return self._duration * faktor.get(self._type, 5)

# Inheritance
class StrengthWorkout(Workout):
    def calculate_calories(self):
        faktor = {"Ringan": 3, "Sedang": 5, "Berat": 7}
        return self.get_duration() * faktor.get(self.get_intensity(), 0)

#(Tkinter GUI) 
class WorkoutApp:
    def __init__(self, root):
        self.root = root
        self.workouts = []  #list

        self.setup_style()
        self.build_scroll_container()

        self.build_header()
        self.build_form()
        self.build_table()
        self.build_stat_cards()
        self.build_ranking()
        self.build_filter()
        self.build_graph()
        self.build_footer()

        self.load_csv()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) 

    def setup_style(self):
        style = ttk.Style() 
        style.theme_use("clam")

        BG = "#F4F6F8"
        PRIMARY = "#374151"
        CARD = "#FFFFFF"
        
        # Warna Header 
        HEADER_BG = "#062B5F" 
        HEADER_TEXT = "white"
        
        self.root.configure(bg=BG)

        style.configure(".", font=("Segoe UI", 10), background=BG)
        
        # Gaya untuk Header Frame (Background Biru Gelap)
        style.configure("Header.TFrame", background=HEADER_BG)
        
        # Gaya untuk Judul di Header 
        style.configure("HeaderTitle.TLabel", 
                        font=("Segoe UI", 20, "bold"), 
                        background=HEADER_BG, 
                        foreground=HEADER_TEXT)
        
        # Gaya untuk Sub-judul di Header 
        style.configure("HeaderSubtitle.TLabel", 
                        font=("Segoe UI", 10), 
                        background=HEADER_BG, 
                        foreground="#9CA3AF") 
                        
        style.configure("Card.TFrame",
            background=CARD,
            relief="solid",
            borderwidth=1
        )

        style.configure("CardTitle.TLabel", foreground="#6B7280", background=CARD)
        style.configure("CardValue.TLabel", foreground="#111827", background=CARD, font=("Segoe UI", 18, "bold"))
        style.configure("Primary.TButton", background=PRIMARY, foreground="white", padding=8)
        style.map("Primary.TButton", background=[("active", "#1F2937")])
        style.configure("Success.TButton", background="#22C55E", foreground="white", padding=8)
        style.map("Success.TButton", background=[("active", "#27DA3F")])
        style.configure("Treeview", rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


    def build_scroll_container(self):
        self.canvas = tk.Canvas(self.root, bg="#F4F6F8")
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=2)
    
# header
    def build_header(self):
        header = ttk.Frame(self.scrollable_frame, style="Header.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        padding_frame = ttk.Frame(header, style="Header.TFrame")
        padding_frame.pack(fill="both", padx=20, pady=15)

        ttk.Label(padding_frame, text="🏋️ My Workout", style="HeaderTitle.TLabel").pack(side="left")
        
        ttk.Label(padding_frame, text="Pantau aktivitas & kalori olahraga",
                  style="HeaderSubtitle.TLabel").pack(side="left", padx=15)

    def build_form(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Input Workout", padding=15)
        frame.grid(row=1, column=0, padx=20, pady=10, sticky="nw")

        labels = ["Tanggal", "Jenis Olahraga", "Durasi (menit)", "Intensitas"]
        for i, lbl in enumerate(labels):
            ttk.Label(frame, text=lbl).grid(row=i, column=0, sticky="w", pady=6)

        self.entry_date = ttk.Entry(frame)
        self.entry_date.grid(row=0, column=1)
        self.entry_date.insert(0, datetime.now().strftime("%d-%m-%Y"))

        self.combo_type = ttk.Combobox(
            frame,
            values=["Lari", "Jalan Santai", "Bersepeda", "Renang", "Yoga",
                    "Skipping", "Angkat Beban", "HIIT"],
            state="readonly"
        )
        self.combo_type.grid(row=1, column=1)
        self.combo_type.set("Lari")
        self.combo_type.bind("<<ComboboxSelected>>", self.toggle_intensity)

        self.entry_duration = ttk.Entry(frame)
        self.entry_duration.grid(row=2, column=1)

        self.combo_intensity = ttk.Combobox(
            frame, values=["Ringan", "Sedang", "Berat"], state="disabled"
        )
        self.combo_intensity.set("-")
        self.combo_intensity.grid(row=3, column=1)

        ttk.Button(frame, text="➕ Tambah Workout",
                   style="Success.TButton",
                   command=self.add_workout)\
            .grid(row=4, columnspan=2, pady=12, sticky="ew")

    def build_table(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Riwayat Workout")
        frame.grid(row=1, column=1, padx=20, pady=10, sticky="nw")

        columns = ("Tanggal", "Jenis", "Durasi", "Intensitas", "Kalori")        # tree
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        self.table.pack(fill="both", expand=True)

    def build_stat_cards(self):
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=2, column=0, columnspan=2, padx=20, pady=15, sticky="ew")

        self.card_sesi = self.create_card(frame, "TOTAL SESI", 0)
        self.card_kalori = self.create_card(frame, "TOTAL KALORI", 1)
        self.card_rata = self.create_card(frame, "RATA-RATA", 2)

    def create_card(self, parent, title, col):
        f = ttk.Frame(parent, style="Card.TFrame", padding=15)
        f.grid(row=0, column=col, padx=10)

        ttk.Label(f, text=title, style="CardTitle.TLabel").pack(anchor="w")
        val = ttk.Label(f, text="0", style="CardValue.TLabel")
        val.pack(anchor="w", pady=5)
        return val

    def build_ranking(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Ranking Boros Kalori")
        frame.grid(row=3, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        self.rank_box = tk.Listbox(frame, height=5)
        self.rank_box.pack(fill="both", expand=True)

    def build_filter(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Filter Data")
        frame.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.combo_filter = ttk.Combobox(
            frame, values=["Semua", "Mingguan", "Bulanan"], state="readonly"
        )
        self.combo_filter.set("Semua")
        self.combo_filter.grid(row=0, column=0, padx=5)

        ttk.Button(frame, text="Terapkan",
                   style="Primary.TButton",
                   command=self.apply_filter)\
            .grid(row=0, column=1, padx=5)

    def build_graph(self):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        frame = ttk.LabelFrame(self.scrollable_frame, text="Grafik Kalori")
        frame.grid(row=5, column=0, columnspan=2, padx=20, pady=10)

        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas_graph = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas_graph.get_tk_widget().pack(fill="both", expand=True)

    def build_footer(self):
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(frame, text="Simpan ke CSV",
                   style="Primary.TButton",
                   command=self.save_data_to_file).pack(side="left", padx=10)

        ttk.Button(frame, text="Hapus Terpilih",
                   command=self.delete_selected).pack(side="left")

    # ... (LOGIC & DATA HANDLING tidak berubah) ...
    def toggle_intensity(self, event=None):
        if self.combo_type.get() == "Angkat Beban":
            self.combo_intensity.config(state="readonly")
            self.combo_intensity.set("Sedang")
        else:
            self.combo_intensity.set("-")
            self.combo_intensity.config(state="disabled")

    def add_workout(self):
        try:
            durasi = int(self.entry_duration.get())
            jenis = self.combo_type.get()
            intensitas = self.combo_intensity.get()
            
            w = StrengthWorkout(self.entry_date.get(), jenis, durasi, intensitas)\
                if jenis == "Angkat Beban" else Workout(self.entry_date.get(), jenis, durasi, intensitas)

            self.workouts.append(w)
            
            self.table.insert("", tk.END, values=(
                w.get_date(), w.get_type(), w.get_duration(),
                w.get_intensity(), w.calculate_calories()
            ))

            self.entry_duration.delete(0, tk.END)
            self.update_all()

        except ValueError:
            messagebox.showerror("Error", "Durasi harus angka")

    def delete_selected(self):
        for item in self.table.selection():
            idx = self.table.index(item)
            self.table.delete(item)
            try:
                self.workouts.pop(idx)
            except IndexError:
                pass 
                
        self.update_all()

    def update_all(self):
        total = len(self.workouts)
        kalori = sum(w.calculate_calories() for w in self.workouts)
        rata = kalori // total if total else 0

        self.card_sesi.config(text=str(total))
        self.card_kalori.config(text=str(kalori))
        self.card_rata.config(text=str(rata))

        self.update_ranking()
        self.update_graph()

    def update_ranking(self):
        self.rank_box.delete(0, tk.END)
        data = {}
        for w in self.workouts:
            data[w.get_type()] = data.get(w.get_type(), 0) + w.calculate_calories()

        for i, (j, k) in enumerate(sorted(data.items(), key=lambda x: x[1], reverse=True), 1):
            self.rank_box.insert(tk.END, f"{i}. {j} - {k} kalori")

    def apply_filter(self):
        self.table.delete(*self.table.get_children())
        periode = self.combo_filter.get()
        now = datetime.now()

        import datetime 
        if periode == "Mingguan":
            batas_waktu = now - datetime.timedelta(days=7)
        elif periode == "Bulanan":
            batas_waktu = datetime.datetime(now.year, now.month, 1)

        for w in self.workouts:
            try:
                w_date = datetime.datetime.strptime(w.get_date(), "%d-%m-%Y")
                tampil = True
            except ValueError:
                continue 
            
            if periode == "Mingguan":
                tampil = w_date >= batas_waktu
            elif periode == "Bulanan":
                tampil = w_date >= batas_waktu

            if tampil:
                self.table.insert("", tk.END, values=(
                    w.get_date(), w.get_type(), w.get_duration(),
                    w.get_intensity(), w.calculate_calories()
                ))

    def update_graph(self):
        self.ax.clear()
        data = {}
        for w in self.workouts:
            data[w.get_type()] = data.get(w.get_type(), 0) + w.calculate_calories()

        if data:
            self.ax.bar(data.keys(), data.values(), color="#3B84F8")
            self.ax.set_title("Total Kalori per Olahraga", fontsize=10)
            self.ax.tick_params(axis='x', rotation=30, labelsize=8)
            self.ax.tick_params(axis='y', labelsize=8)
            self.fig.tight_layout() 

        self.canvas_graph.draw()

    def save_data_to_file(self):
        with open("workout_data.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Tanggal", "Jenis", "Durasi", "Intensitas", "Kalori"])
            for w in self.workouts:
                writer.writerow([
                    w.get_date(), w.get_type(),
                    w.get_duration(), w.get_intensity(),
                    w.calculate_calories()
                ])

    def load_csv(self):
        if not os.path.exists("workout_data.csv"):
            return
        with open("workout_data.csv", "r", newline="") as f:
            reader = csv.reader(f)
            try:
                next(reader) 
            except StopIteration:
                return 

            for r in reader:
                if len(r) < 4:
                    continue 
                    
                d, j, du, i, _ = r 
                try:
                    du = int(du)
                except ValueError:
                    continue 
                    
                w = StrengthWorkout(d, j, du, i) if j == "Angkat Beban" else Workout(d, j, du, i)
                self.workouts.append(w)
                
                self.table.insert("", tk.END, values=(
                    w.get_date(), w.get_type(), w.get_duration(), 
                    w.get_intensity(), w.calculate_calories()
                ))
                
        self.update_all()

    def on_closing(self):
        try:
            self.save_data_to_file() 
        except Exception as e:
            messagebox.showerror("Error Save", f"Gagal menyimpan data: {e}")
        finally:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Workout Tracker Pro")
    root.geometry("1100x650")
    app = WorkoutApp(root)
    root.mainloop()