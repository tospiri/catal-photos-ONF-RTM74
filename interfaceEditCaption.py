import pandas as pd
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PhotoEditor:
    def __init__(self, root, data_path):
        self.root = root
        self.root.title("Éditeur de Légendes de Photos")

        # Chargement des données depuis le fichier CSV
        self.df = pd.read_csv(data_path, encoding="ansi", sep=';')
        self.current_index = 0

        # Création des widgets
        self.image_label = ttk.Label(root)
        self.image_label.grid(row=0, column=0, padx=10, pady=10)

        self.caption_text = tk.Text(root, width=50, height=10)  # Ajustez la largeur et la hauteur du Text
        self.caption_text.grid(row=0, column=1, pady=10, sticky="nsew")

        self.caption_text_scroll = ttk.Scrollbar(root, command=self.caption_text.yview)
        self.caption_text_scroll.grid(row=0, column=2, pady=10, sticky="nsew")
        self.caption_text['yscrollcommand'] = self.caption_text_scroll.set

        self.prev_button = ttk.Button(root, text="Précédent", command=self.show_prev_photo)
        self.prev_button.grid(row=1, column=1, pady=10)
        self.caption_text.delete('1.0', tk.END)
        self.next_button = ttk.Button(root, text="Suivant", command=self.show_next_photo)
        self.next_button.grid(row=1, column=2, pady=10)

        # Liens pour les touches de clavier
        root.bind("<Right>", self.on_right_arrow)
        root.bind("<Left>", self.on_left_arrow)

        root.bind("<End>", self.on_enter)

        self.save_button = ttk.Button(root, text="Enregistrer", command=self.save_caption)
        self.save_button.grid(row=2, column=1, columnspan=2, pady=10)

        # Affichage de la première photo
        self.show_photo()

    def on_right_arrow(self, event):
        self.show_next_photo()

    def on_left_arrow(self, event):
        self.show_prev_photo()

    def on_enter(self, event):
        self.save_caption()

    def show_photo(self):
        image_path = self.df.at[self.current_index, "chemin_jpg"]
        image = Image.open(image_path)
        image = image.resize((500, 500))
        photo = ImageTk.PhotoImage(image)

        self.image_label.config(image=photo)
        self.image_label.image = photo

        current_caption = self.df.loc[self.current_index, "ImageCaption"]
        self.caption_text.delete('1.0', tk.END)
        self.caption_text.insert(tk.END, current_caption)

    def show_prev_photo(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_photo()

    def show_next_photo(self):
        if self.current_index < len(self.df) - 1:
            self.current_index += 1
            self.show_photo()

    def save_caption(self):
        new_caption = self.caption_text.get('1.0', 'end-1c')
        self.df.at[self.current_index, "ImageCaption"] = new_caption
        self.df.to_csv("donnees_photos.csv", index=False, sep=";", encoding='ansi')
        print("Légende enregistrée avec succès.")

if __name__ == "__main__":
    data_path = "donnees_photos.csv"

    root = tk.Tk()
    app = PhotoEditor(root, data_path)
    root.mainloop()