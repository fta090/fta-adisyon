from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import datetime
import json

menu = {}
loglar = []
ciro = 0.0
kasiyer = None

kasiyerler = {
    "fta1": "fta1",
    "fta2": "fta2"
}
#kasiyerleri burdan ekelye bilrisiniz 

menu_dosyasi = "menu.json"

if not os.path.exists("logs"):
    os.makedirs("logs")

bugun = datetime.datetime.now().strftime("%Y-%m-%d")
log_dosyasi = f"logs/log_{bugun}.txt"
siparis_dosyasi = f"logs/siparis_{bugun}.txt"

def log_yaz(metin):
    zaman = datetime.datetime.now().strftime("[%H:%M:%S]")
    satir = f"{zaman} {metin}\n"
    with open(log_dosyasi, "a", encoding="utf-8") as f:
        f.write(satir)
    loglar.append(satir)


def logdan_satir_sil(urun_adi, fiyat):
    global loglar
    try:
        with open(log_dosyasi, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate() 

            silindi = False
            for i in reversed(range(len(lines))): 
                line = lines[i]
               
                if f"Sipariş: {urun_adi} x1 - {fiyat:.2f} TL" in line:
                    log_yaz(f"LOG: '{line.strip()}' satırı iade nedeniyle silindi.") 
                    del lines[i]
                    silindi = True
                    break 
            
            f.writelines(lines) 
        
      
        if silindi:
           
            for i in reversed(range(len(loglar))):
                if f"Sipariş: {urun_adi} x1 - {fiyat:.2f} TL" in loglar[i]:
                    del loglar[i]
                    break

    except Exception as e:
        log_yaz(f"Log dosyasından satır silinirken hata oluştu: {e}")
        messagebox.showerror("Hata", f"Log dosyasından satır silinirken hata oluştu: {e}")


def siparisi_txt_ye_yaz(siparisler):
    with open(siparis_dosyasi, "a", encoding="utf-8") as f:
        f.write("Sipariş - " + datetime.datetime.now().strftime("%H:%M:%S") + f" - Kasiyer: {kasiyer}\n")
        for satir in siparisler:
            f.write(satir + "\n")
        f.write("=" * 40 + "\n")


def menuyu_kaydet():
    try:
        with open(menu_dosyasi, "w", encoding="utf-8") as f:
            json.dump(menu, f, indent=4, ensure_ascii=False)
        log_yaz("Menu başarıyla kaydedildi.")
    except Exception as e:
        log_yaz(f"Menu kaydedilirken hata oluştu: {e}")

def menuyu_yukle():
    global menu
    if os.path.exists(menu_dosyasi) and os.path.getsize(menu_dosyasi) > 0:
        try:
            with open(menu_dosyasi, "r", encoding="utf-8") as f:
                menu = json.load(f)
            log_yaz("Menu başarıyla yüklendi.")
        except json.JSONDecodeError as e:
            log_yaz(f"Menu dosyası bozuk veya boş: {e}. Yeni bir menü oluşturuluyor.")
            menu = {} 
        except Exception as e:
            log_yaz(f"Menu yüklenirken beklenmeyen hata oluştu: {e}. Yeni bir menü oluşturuluyor.")
            menu = {}
    else:
        log_yaz("Menu dosyası bulunamadı veya boş. Yeni bir menü başlatılıyor.")
        menu = {}


class GirisPenceresi:
    def __init__(self, master):
        self.master = master
        self.master.title("Kasiyer Giriş")
        self.master.geometry("300x200")
        self.master.resizable(False, False) 

        Label(master, text="Kasiyer Adı:", font=("Arial", 10)).pack(pady=5)
        self.entry_kadi = Entry(master, font=("Arial", 10))
        self.entry_kadi.pack(pady=5)

        Label(master, text="Şifre:", font=("Arial", 10)).pack(pady=5)
        self.entry_sifre = Entry(master, show="*", font=("Arial", 10))
        self.entry_sifre.pack(pady=5)

        Button(master, text="Giriş", command=self.giris, font=("Arial", 10), bg="#007acc", fg="white").pack(pady=10)

    def giris(self):
        global kasiyer
        kullanici = self.entry_kadi.get()
        sifre = self.entry_sifre.get()
        if kullanici in kasiyerler and kasiyerler[kullanici] == sifre:
            kasiyer = kullanici
            self.master.destroy()
            root = Tk()
            app = AdisyonUygulamasi(root)
            root.mainloop()
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış.")

class AdisyonUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Adisyon Sistemi - Kasiyer: {kasiyer}") 
        self.root.configure(bg="#1e1e1e")
        self.root.state("zoomed")

        self.sol = Frame(root, bg="#1e1e1e")
        self.sol.pack(side=TOP, padx=10, pady=10, fill=BOTH, expand=True)

        Label(self.sol, text="ÜRÜNLER", font=("Arial", 16, "bold"), fg="white", bg="#1e1e1e").pack(anchor=W)

        self.urun_kapsayici = Canvas(self.sol, bg="#1e1e1e", highlightthickness=0) # Remove border
        self.scrollbar = Scrollbar(self.sol, orient=VERTICAL, command=self.urun_kapsayici.yview)
        self.scrollable_frame = Frame(self.urun_kapsayici, bg="#1e1e1e")

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.urun_kapsayici.configure(scrollregion=self.urun_kapsayici.bbox("all"))
        )

        self.urun_kapsayici.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.urun_kapsayici.configure(yscrollcommand=self.scrollbar.set)

        self.urun_kapsayici.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

       
        self.urun_ekle_button = Button(self.sol, text="Ürün Ekle", command=self.urun_ekle, bg="#007acc", fg="white", font=("Arial", 10, "bold"))
        self.urun_ekle_button.pack(anchor=W, pady=5)

        self.alt = Frame(root, bg="#1e1e1e")
        self.alt.pack(side=BOTTOM, fill=X, padx=10, pady=10)

        Label(self.alt, text="ADİSYON", font=("Arial", 14, "bold"), fg="white", bg="#1e1e1e").pack(anchor=W)
        self.adisyon_listesi = Listbox(self.alt, height=8, bg="#2d2d2d", fg="white", font=("Consolas", 11), selectbackground="#007acc", selectforeground="white")
        self.adisyon_listesi.pack(fill=X, padx=10, pady=5)
        self.adisyon_listesi.bind("<Delete>", self.secili_urunu_sil) 

        kontrol_frame = Frame(self.alt, bg="#1e1e1e")
        kontrol_frame.pack(fill=X, pady=5)
        Button(kontrol_frame, text="Siparişi Gönder", command=self.siparisi_gonder, bg="#28a745", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)
        Button(kontrol_frame, text="Toplam Göster", command=self.toplam_goster, bg="#444", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)
        Button(kontrol_frame, text="Ciro Göster", command=self.ciro_goster, bg="#555", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)
        
    
        Button(kontrol_frame, text="Seçileni Sil", command=self.secili_urunu_sil, bg="#ffc107", fg="black", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)
        Button(kontrol_frame, text="Hepsini Sil", command=self.adisyonu_sil, bg="#dc3545", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)


        Button(kontrol_frame, text="İade Et", command=self.urun_iade_et, bg="#6f42c1", fg="white", font=("Arial", 10, "bold")).pack(side=LEFT, padx=5)


        self.toplam_label = Label(self.alt, text="Toplam: 0.00 TL", font=("Arial", 14, "bold"), fg="lightgreen", bg="#1e1e1e")
        self.toplam_label.pack(anchor=E, padx=10, pady=5)

        
        self.mevcut_urunleri_goster()

    def mevcut_urunleri_goster(self):
       
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        for urun_ad in menu:
            self.urun_kutu_olustur(urun_ad)

    def urun_ekle(self):
        
        if kasiyer != "fta1":
            messagebox.showwarning("Yetkisiz İşlem", "Sadece 'fta1' kullanıcısı menüye ürün ekleyebilir.")
            log_yaz(f"Yetkisiz ürün ekleme denemesi: {kasiyer}")
            return

        urun_ad = simpledialog.askstring("Ürün Ekle", "Ürün adı:", parent=self.root)
        if urun_ad is None or urun_ad.strip() == "":
            return

        fiyat = simpledialog.askfloat("Ürün Ekle", "Fiyat (TL):", parent=self.root)
        if fiyat is None:
            return

        gorsel_yolu = filedialog.askopenfilename(title="Ürün Görseli", filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png"), ("Tüm Dosyalar", "*.*")], parent=self.root)
        
      
        if gorsel_yolu:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if gorsel_yolu.startswith(current_dir):
                gorsel_yolu = os.path.relpath(gorsel_yolu, current_dir)

        menu[urun_ad] = {"fiyat": fiyat, "gorsel": gorsel_yolu}
        self.urun_kutu_olustur(urun_ad)
        log_yaz(f"Ürün eklendi: {urun_ad} - {fiyat} TL (Ekleyen: {kasiyer})")
        menuyu_kaydet() 

    def urun_kutu_olustur(self, urun_ad):
        frame = Frame(self.scrollable_frame, bg="#2d2d2d", padx=5, pady=5, relief=RAISED, bd=1)
        frame.pack(side=TOP, fill=X, pady=2, padx=5)

        img_tk = None
        gorsel_yolu = menu[urun_ad].get("gorsel")
        
       
        if gorsel_yolu and not os.path.isabs(gorsel_yolu):
            gorsel_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), gorsel_yolu)

        if gorsel_yolu and os.path.exists(gorsel_yolu):
            try:
                img = Image.open(gorsel_yolu)
                img = img.resize((50, 50), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                label_img = Label(frame, image=img_tk, bg="#2d2d2d")
                label_img.image = img_tk
                label_img.pack(side=LEFT)
            except Exception as e:
                log_yaz(f"Görsel yüklenirken hata: {gorsel_yolu} - {e}")
                
                Label(frame, text="[Resim Yok]", fg="gray", bg="#2d2d2d").pack(side=LEFT)
        else:
            Label(frame, text="[Resim Yok]", fg="gray", bg="#2d2d2d").pack(side=LEFT)


        info = Frame(frame, bg="#2d2d2d")
        info.pack(side=LEFT, padx=10)

        Label(info, text=urun_ad, font=("Arial", 12, "bold"), fg="white", bg="#2d2d2d").pack(anchor=W)
        Label(info, text=f"{menu[urun_ad]['fiyat']:.2f} TL", font=("Arial", 10), fg="lightgray", bg="#2d2d2d").pack(anchor=W)

       
        frame.bind("<Double-1>", lambda e, ad=urun_ad: self.urun_ekle_direkt(ad))
        for widget in frame.winfo_children():
            widget.bind("<Double-1>", lambda e, ad=urun_ad: self.urun_ekle_direkt(ad))

    def urun_ekle_direkt(self, urun_ad):
        if urun_ad in menu:
            self.adisyon_listesi.insert(END, f"{urun_ad} x1 = {menu[urun_ad]['fiyat']:.2f} TL")
            self.adisyon_listesi.insert(END, "-" * 40) 
            global ciro
            ciro += menu[urun_ad]['fiyat']
            self.toplam_goster() 
            log_yaz(f"Sipariş: {urun_ad} x1 - {menu[urun_ad]['fiyat']:.2f} TL (Kasiyer: {kasiyer})")
        else:
            messagebox.showerror("Hata", f"Ürün '{urun_ad}' menüde bulunamadı.")


    def secili_urunu_sil(self, event=None): 
        try:
            secili_index = self.adisyon_listesi.curselection()
            if not secili_index:
                messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz ürünü seçin.")
                return

            index_to_delete = secili_index[0]
            satir = self.adisyon_listesi.get(index_to_delete)

            if messagebox.askyesno("Ürünü Sil", f"'{satir.split('x1')[0].strip()}' ürününü adisyondan silmek istediğinizden emin misiniz?"):
                if "=" in satir:
                    try:
                        fiyat_str = satir.split("=")[-1].replace("TL", "").strip()
                        fiyat = float(fiyat_str)
                        global ciro
                      
                        log_yaz(f"Adisyondan ürün çıkarıldı: {satir} (Kasiyer: {kasiyer})")
                    except ValueError:
                        pass 
                
                self.adisyon_listesi.delete(index_to_delete)
          
                if self.adisyon_listesi.size() > index_to_delete and self.adisyon_listesi.get(index_to_delete) == "-" * 40:
                    self.adisyon_listesi.delete(index_to_delete)
                elif index_to_delete > 0 and self.adisyon_listesi.get(index_to_delete - 1) == "-" * 40:
                    self.adisyon_listesi.delete(index_to_delete - 1)
                
                self.toplam_goster() 

        except Exception as e:
            messagebox.showerror("Hata", f"Seçili ürünü silerken bir hata oluştu: {e}")
            log_yaz(f"Seçili ürünü silerken hata: {e}")


    def siparisi_gonder(self):
        if self.adisyon_listesi.size() == 0:
            messagebox.showwarning("Uyarı", "Sipariş listesi boş.")
            return
        
    
        self.toplam_goster()
        gonderilen_toplam = float(self.toplam_label.cget("text").split(":")[1].replace("TL", "").strip())
        
        siparis = [self.adisyon_listesi.get(i) for i in range(self.adisyon_listesi.size())]
        siparisi_txt_ye_yaz(siparis)
        log_yaz(f"Sipariş başarıyla gönderildi. Toplam: {gonderilen_toplam:.2f} TL (Kasiyer: {kasiyer})")
        messagebox.showinfo("Başarılı", "Sipariş gönderildi ve kaydedildi.")
        self.adisyon_listesi.delete(0, END)
        self.toplam_label.config(text="Toplam: 0.00 TL")

    def toplam_goster(self):
        toplam = 0
        for i in range(self.adisyon_listesi.size()):
            satir = self.adisyon_listesi.get(i)
            if "=" in satir:
                try:
                    fiyat = float(satir.split("=")[-1].replace("TL", "").strip())
                    toplam += fiyat
                except ValueError: 
                    continue
        self.toplam_label.config(text=f"Toplam: {toplam:.2f} TL")
     

    def ciro_goster(self):
        messagebox.showinfo("Ciro", f"Günlük Ciro: {ciro:.2f} TL")
        log_yaz(f"Ciro görüntülendi: {ciro:.2f} TL (Kasiyer: {kasiyer})")

    def adisyonu_sil(self):
        if messagebox.askyesno("Adisyonu Sil", "Adisyonu tamamen silmek istiyor musunuz? Bu işlem geri alınamaz."):
            self.adisyon_listesi.delete(0, END)
            self.toplam_label.config(text="Toplam: 0.00 TL")
            log_yaz(f"Adisyon tamamen silindi. (Kasiyer: {kasiyer})")

    def urun_iade_et(self):
    
        if kasiyer != "fta1":
            messagebox.showwarning("Yetkisiz İşlem", "Sadece 'fta1' kullanıcısı ürün iade edebilir.")
            log_yaz(f"Yetkisiz iade denemesi: {kasiyer}")
            return

        secili_index = self.adisyon_listesi.curselection()
        if not secili_index:
            messagebox.showwarning("Uyarı", "Lütfen iade etmek istediğiniz ürünü seçin.")
            return

        index = secili_index[0]
        satir = self.adisyon_listesi.get(index)

        if "=" in satir:
            try:
                urun_parcalari = satir.split("x1 =")
                urun_adi_tam = urun_parcalari[0].strip()
                fiyat_str = urun_parcalari[1].replace("TL", "").strip()
                fiyat = float(fiyat_str)

                if messagebox.askyesno("Ürün İade", f"'{urun_adi_tam}' ürününü ({fiyat:.2f} TL) iade etmek istediğinizden emin misiniz?"):
                    global ciro
                    ciro -= fiyat
                    self.toplam_goster() 
                    
                    
                    logdan_satir_sil(urun_adi_tam, fiyat)
                    log_yaz(f"İade edildi: {urun_adi_tam} - {fiyat:.2f} TL (Kasiyer: {kasiyer})")
                    messagebox.showinfo("İade Başarılı", f"'{urun_adi_tam}' ürünü iade edildi. Ciro güncellendi.")
                    
                
                    self.adisyon_listesi.delete(index)
                  
                    if self.adisyon_listesi.size() > index and self.adisyon_listesi.get(index) == "-" * 40:
                        self.adisyon_listesi.delete(index)
                    elif index > 0 and self.adisyon_listesi.get(index - 1) == "-" * 40:
                        self.adisyon_listesi.delete(index - 1)
                        
                    self.toplam_goster() #
                
            except ValueError as e:
                messagebox.showerror("Hata", f"Seçili öğe bir ürün gibi görünmüyor veya fiyatı ayrıştırılamadı: {e}")
                log_yaz(f"İade hatası: Seçili öğe ayrıştırılamadı - {satir} - {e}")
            except Exception as e:
                messagebox.showerror("Hata", f"İade işlemi sırasında bir hata oluştu: {e}")
                log_yaz(f"İade işlemi genel hata: {e}")
        else:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir ürün satırı seçin.")


if __name__ == "__main__":
    menuyu_yukle() 
    giris = Tk()
    app = GirisPenceresi(giris)
    giris.mainloop()