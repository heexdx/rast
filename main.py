import flet as ft
from flet import *
import json
import os
import requests
from datetime import datetime

class QuranApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.load_data()
        self.create_ui()
        self.load_last_read()

    def setup_page(self):
        self.page.title = "القرآن الكريم"
        self.page.rtl = True
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 10
        self.page.fonts = {
            "Uthmanic": "https://fonts.googleapis.com/css2?family=Lateef&display=swap"
        }
        self.page.window_min_width = 400
        self.page.window_min_height = 600

    def load_data(self):
        try:
            self.surahs = requests.get(
                "https://api.alquran.cloud/v1/surah"
            ).json()["data"]
            self.current_surah = 1
            self.current_ayah = 1
        except:
            # Fallback data if API fails
            self.surahs = [
                {"number": 1, "name": "الفاتحة", "englishName": "Al-Fatiha"},
                {"number": 2, "name": "البقرة", "englishName": "Al-Baqarah"}
            ]
            self.current_surah = 1
            self.current_ayah = 1

    def create_ui(self):
        # Surah selection dropdown
        self.surah_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(
                f"{surah['number']}. {surah['name']}",
                key=str(surah['number'])
            ) for surah in self.surahs],
            value="1",
            width=300,
            on_change=self.change_surah
        )

        # Ayah display
        self.ayah_text = ft.Text(
            size=24,
            font_family="Uthmanic",
            text_align=ft.TextAlign.RIGHT,
            selectable=True
        )

        # Navigation controls
        self.prev_btn = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            on_click=self.prev_ayah
        )
        self.next_btn = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD,
            on_click=self.next_ayah
        )

        # Assemble UI
        self.page.add(
            ft.Column([
                ft.Row([self.surah_dropdown]),
                ft.Divider(),
                ft.Card(
                    ft.Container(
                        ft.Column([
                            self.ayah_text,
                            ft.Row(
                                [self.prev_btn, self.next_btn],
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ], spacing=20),
                        padding=20
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
        self.update_display()

    def change_surah(self, e):
        self.current_surah = int(self.surah_dropdown.value)
        self.current_ayah = 1
        self.update_display()
        self.save_last_read()

    def next_ayah(self, e):
        self.current_ayah += 1
        self.update_display()
        self.save_last_read()

    def prev_ayah(self, e):
        if self.current_ayah > 1:
            self.current_ayah -= 1
            self.update_display()
            self.save_last_read()

    def update_display(self):
        try:
            ayah = requests.get(
                f"https://api.alquran.cloud/v1/ayah/{self.current_surah}:{self.current_ayah}/ar.alafasy"
            ).json()["data"]
            self.ayah_text.value = ayah["text"]
        except:
            self.ayah_text.value = "حدث خطأ في تحميل الآية"
        self.page.update()

    def save_last_read(self):
        with open("last_read.json", "w") as f:
            json.dump({
                "surah": self.current_surah,
                "ayah": self.current_ayah,
                "date": datetime.now().isoformat()
            }, f)

    def load_last_read(self):
        try:
            if os.path.exists("last_read.json"):
                with open("last_read.json", "r") as f:
                    last = json.load(f)
                    self.current_surah = last["surah"]
                    self.current_ayah = last["ayah"]
                    self.surah_dropdown.value = str(self.current_surah)
                    self.update_display()
        except:
            pass

def main(page: ft.Page):
    QuranApp(page)

ft.app(target=main)

def main(page: ft.Page):
    QuranApp(page)

ft.app(target=main, view=ft.WEB_BROWSER)

# استدعاء الدالة clos عند الضغط على Enter أو الزر Submit
entry.bind("<Return>", clos)

# تشغيل نافذة tkinter
root.mainloop()
