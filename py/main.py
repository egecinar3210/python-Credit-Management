import tkinter as tk

# Pencereyi oluştur
root = tk.Tk()
root.title("Hoşgeldiniz Penceresi")
root.geometry("600x400")  # Pencere boyutu

# Ortada büyük yazı
label = tk.Label(
    root,
    text="HOŞGELDİNİZ",
    font=("Arial", 48, "bold"),
    fg="blue"
)
label.pack(expand=True)

root.mainloop()  #