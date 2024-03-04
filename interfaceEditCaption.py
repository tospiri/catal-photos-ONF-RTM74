import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os

class PhotoEditor:
    def __init__(self, root, data_path):
        self.root = root
        self.root.title("Éditeur de Légendes de Photos")

        # Chargement des données depuis le fichier CSV
        self.df = pd.read_csv(data_path, encoding="ansi", sep=';')
        self.current_index = 0

        # Création des widgets
        self.image_label = ttk.Label(root)
        self.image_label.grid(row=0, column=0, padx=10, pady=10, rowspan=2)

        self.caption_text_top = tk.Text(root, width=40, height=20)
        self.caption_text_top.grid(row=0, column=1, pady=10, sticky="nsew")

        self.caption_text_bottom = tk.Text(root, width=40, height=10)
        self.caption_text_bottom.grid(row=1, column=1, pady=10, sticky="nsew")

        self.scroll_counter = 0

        self.height = 700
        self.width = 700

        # Liens pour les touches de clavier
        #root.bind("<Right>", self.on_right_arrow)
        #root.bind("<Left>", self.on_left_arrow)
        root.bind("<MouseWheel>", self.on_mousewheel)
        root.bind("<Down>", self.on_down_arrow)
        root.bind("<Up>", self.on_up_arrow)

        root.bind("<End>", self.on_enter)

        self.image_label.bind("<ButtonRelease-1>", self.open_file)

        # Création de la liste
        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=30, height=10)
        self.listbox.grid(row=0, column=3, rowspan=2, pady=10, padx=10, sticky="nsew")
        # Ajout de la barre de défilement à la liste
        self.listbox_scroll = tk.Scrollbar(root, orient="vertical", command=self.listbox.yview)
        self.listbox_scroll.grid(row=0, column=4, rowspan=2, pady=10, sticky="nse")
        self.listbox['yscrollcommand'] = self.listbox_scroll.set

        # Liens pour la sélection dans la liste
        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)

        # Initialisation de la liste
        self.update_listbox()

        # Affichage de la première photo
        self.show_photo(self.height, self.width)

    def on_right_arrow(self, event):
        self.save_caption()
        self.show_next_photo()


    def on_left_arrow(self, event):
        self.save_caption()
        self.show_prev_photo()

    def on_down_arrow(self, event):
        self.save_caption()
        self.show_next_photo_copy()

    def on_up_arrow(self, event):
        self.caption_text_top.delete('1.0', tk.END)

    def on_enter(self, event):
        self.save_caption()

    def get_image(self):
        image_path = self.df["chemin_jpg"].iloc[self.current_index]
        return image_path

    def show_photo(self, height, width):
        image_path = self.get_image()
        image = Image.open(image_path)
        image = image.resize((height, width))
        photo = ImageTk.PhotoImage(image)

        self.image_label.config(image=photo)
        self.image_label.image = photo

        current_caption = self.df.loc[self.current_index, "ImageCaption"]

        # Mise à jour des deux zones de texte
        self.caption_text_top.delete('1.0', tk.END)
        self.caption_text_top.insert(tk.END, current_caption)

        self.caption_text_bottom.delete('1.0', tk.END)
        self.caption_text_bottom.insert(tk.END, current_caption)


    def show_next_photo_copy(self):
        if self.current_index < len(self.df) - 1:
            self.save_caption()
            current_caption = self.caption_text_top.get('1.0', tk.END)
            self.current_index += 1
            self.show_photo(self.height, self.width)
            self.caption_text_top.delete('1.0', tk.END)
            self.caption_text_top.insert(tk.END, current_caption)
            self.update_listbox()

    def on_mousewheel(self, event):
        # Réguler la vitesse du défilement de la molette
        if event.delta > 0:
            self.scroll_counter += 1
        elif event.delta < 0:
            self.scroll_counter -= 1

        # Attendre que le compteur atteigne un certain seuil
        if self.scroll_counter > 1:
            self.show_next_photo()
            self.scroll_counter = 0  # Réinitialiser le compteur après chaque défilement
        elif self.scroll_counter < -1:
            self.show_prev_photo()
            self.scroll_counter = 0  # Réinitialiser le compteur après chaque défilement

    def show_next_photo(self):
        if self.current_index < len(self.df) - 1:
            self.save_caption()
            self.current_index += 1
            self.show_photo(self.height, self.width)
            self.update_listbox()

    def show_prev_photo(self):
        if self.current_index > 0:
            self.save_caption()
            self.current_index -= 1
            self.show_photo(self.height, self.width)
            self.update_listbox()

    def save_caption(self):
        new_caption = self.caption_text_top.get('1.0', 'end-1c')
        self.df.at[self.current_index, "ImageCaption"] = new_caption.replace("\n", "")
        self.df.to_csv("donnees_photos.csv", index=False, sep=";", encoding='ansi')
        print("Légende enregistrée avec succès.")

    def update_listbox(self):
        # Effacer la liste actuelle
        self.listbox.delete(0, tk.END)

        # Ajouter les légendes des images à la liste
        for index, caption in enumerate(self.df["ImageCaption"]):
            self.listbox.insert(tk.END, f"Photo {index + 1}: {caption}")

    def on_listbox_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.current_index = selected_index[0]
            self.show_photo(self.height, self.width)

    def open_file(self, event):
        os.startfile(self.get_image())


if __name__ == "__main__":
    data_path = "donnees_photos.csv"
    root = tk.Tk()
    app = PhotoEditor(root, data_path)
    root.mainloop()