import flet as ft
from flet import *
import json
import os
from typing import Dict, List
import requests
from concurrent.futures import ThreadPoolExecutor

# --------------------------------------------
# قسم البيانات والخدمات
# --------------------------------------------

class QuranService:
    def __init__(self):
        self.quran_data = self._load_quran_data()
        self.audio_base_url = "https://server.mp3quran.net/afs/"
        self.tafsir_data = self._load_tafsir_data()
        self.bookmarks = self._load_bookmarks()
    
    def _load_quran_data(self) -> Dict:
        """تحميل بيانات القرآن من ملف JSON أو API"""
        try:
            # يمكن استبدال هذا بتحميل من ملف محلي
            response = requests.get("https://api.alquran.cloud/v1/quran/ar.alafasy")
            return response.json()["data"]
        except:
            # بيانات بديلة في حالة فشل الاتصال
            return {
                "surahs": [
                    {
                        "number": 1,
                        "name": "الفاتحة",
                        "englishName": "Al-Fatiha",
                        "ayahs": [
                            {"number": 1, "text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"},
                            {"number": 2, "text": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"},
                            # ... يمكن إضافة بقية الآيات
                        ]
                    }
                ]
            }
    
    def _load_tafsir_data(self) -> Dict:
        """تحميل بيانات التفسير"""
        # يمكن استبدال هذا ببيانات حقيقية
        return {
            "1:1": "تفسير الآية 1 من سورة الفاتحة...",
            "1:2": "تفسير الآية 2 من سورة الفاتحة..."
        }
    
    def _load_bookmarks(self) -> List:
        """تحميل الإشارات المرجعية المحفوظة"""
        try:
            if os.path.exists("bookmarks.json"):
                with open("bookmarks.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_bookmarks(self):
        """حفظ الإشارات المرجعية"""
        with open("bookmarks.json", "w", encoding="utf-8") as f:
            json.dump(self.bookmarks, f, ensure_ascii=False)
    
    def get_audio_url(self, surah: int, ayah: int) -> str:
        """الحصول على رابط التلاوة الصوتية"""
        return f"{self.audio_base_url}{surah:03}{ayah:03}.mp3"
    
    def get_tafsir(self, surah: int, ayah: int) -> str:
        """الحصول على تفسير الآية"""
        return self.tafsir_data.get(f"{surah}:{ayah}", "لا يوجد تفسير متاح حاليًا")

# --------------------------------------------
# قسم واجهة المستخدم
# --------------------------------------------

class QuranApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.quran_service = QuranService()
        self.current_surah = 1
        self.current_ayah = 1
        self.is_playing = False
        self.dark_mode = False
        self.font_size = 24
        
        self._setup_page()
        self._create_ui()
        self._load_last_position()
    
    def _setup_page(self):
        """إعداد إعدادات الصفحة الأساسية"""
        self.page.title = "القرآن الكريم"
        self.page.rtl = True
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 10
        self.page.fonts = {
            "Amiri": "https://fonts.googleapis.com/css2?family=Amiri&display=swap",
            "Uthmani": "https://fonts.googleapis.com/css2?family=Lateef&display=swap"
        }
        self.page.on_disconnect = self._save_last_position
    
    def _create_ui(self):
        """إنشاء واجهة المستخدم"""
        # عناصر التحكم الرئيسية
        self.surah_dropdown = self._create_surah_dropdown()
        self.ayah_text = self._create_ayah_text()
        self.tafsir_text = self._create_tafsir_text()
        self.audio_player = self._create_audio_player()
        
        # شريط الأدوات
        self.toolbar = self._create_toolbar()
        
        # تجميع الواجهة
        self.page.add(
            ft.Column([
                ft.Row([
                    self.surah_dropdown,
                    ft.IconButton(icon=ft.icons.SETTINGS, on_click=self._open_settings)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"سورة {self._get_current_surah_name()} - الآية {self.current_ayah}", 
                                   size=18, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=10),
                            self.ayah_text,
                            ft.Divider(height=20),
                            self.audio_player,
                            self.toolbar
                        ], 
                        spacing=10),
                        padding=20,
                        width=self.page.width - 20
                    )
                ),
                ft.ExpansionTile(
                    title=ft.Text("التفسير"),
                    controls=[self.tafsir_text]
                )
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO)
        )
    
    def _create_surah_dropdown(self) -> ft.Dropdown:
        """إنشاء قائمة اختيار السور"""
        return ft.Dropdown(
            options=[
                ft.dropdown.Option(
                    text=f"{surah['number']}. {surah['name']}",
                    key=str(surah['number'])
                ) for surah in self.quran_service.quran_data["surahs"]
            ],
            value=str(self.current_surah),
            width=300,
            text_size=16,
            label="اختر سورة",
            on_change=self._change_surah
        )
    
    def _create_ayah_text(self) -> ft.Text:
        """إنشاء عنصر عرض الآية"""
        return ft.Text(
            value=self._get_current_ayah_text(),
            size=self.font_size,
            text_align=ft.TextAlign.RIGHT,
            font_family="Uthmani",
            selectable=True
        )
    
    def _create_tafsir_text(self) -> ft.Text:
        """إنشاء عنصر عرض التفسير"""
        return ft.Text(
            value=self.quran_service.get_tafsir(self.current_surah, self.current_ayah),
            size=16,
            text_align=ft.TextAlign.RIGHT
        )
    
    def _create_audio_player(self) -> ft.Row:
        """إنشاء مشغل الصوت"""
        self.audio_status = ft.Text("", size=14)
        return ft.Row([
            ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=self._play_audio),
            ft.IconButton(icon=ft.icons.PAUSE, on_click=self._pause_audio),
            self.audio_status
        ], alignment=ft.MainAxisAlignment.CENTER)
    
    def _create_toolbar(self) -> ft.Row:
        """إنشاء شريط الأدوات"""
        return ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self._prev_ayah),
            ft.IconButton(icon=ft.icons.BOOKMARK, on_click=self._toggle_bookmark),
            ft.IconButton(icon=ft.icons.SHARE, on_click=self._share_ayah),
            ft.IconButton(icon=ft.icons.ARROW_FORWARD, on_click=self._next_ayah),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
    
    # --------------------------------------------
    # وظائف التحكم
    # --------------------------------------------
    
    def _change_surah(self, e):
        """تغيير السورة الحالية"""
        self.current_surah = int(self.surah_dropdown.value)
        self.current_ayah = 1
        self._update_display()
    
    def _next_ayah(self, e):
        """الانتقال إلى الآية التالية"""
        current_surah_data = self._get_current_surah_data()
        if self.current_ayah < len(current_surah_data["ayahs"]):
            self.current_ayah += 1
            self._update_display()
    
    def _prev_ayah(self, e):
        """الانتقال إلى الآية السابقة"""
        if self.current_ayah > 1:
            self.current_ayah -= 1
            self._update_display()
    
    def _play_audio(self, e):
        """تشغيل التلاوة الصوتية"""
        if not self.is_playing:
            self.is_playing = True
            self.audio_status.value = "جاري التشغيل..."
            self.page.update()
            # هنا يمكنك إضافة كود التشغيل الفعلي باستخدام مكتبة مثل pygame
            
    def _pause_audio(self, e):
        """إيقاف التلاوة الصوتية مؤقتًا"""
        if self.is_playing:
            self.is_playing = False
            self.audio_status.value = "متوقف"
            self.page.update()
    
    def _toggle_bookmark(self, e):
        """إضافة/إزالة إشارة مرجعية"""
        bookmark = {"surah": self.current_surah, "ayah": self.current_ayah}
        if bookmark in self.quran_service.bookmarks:
            self.quran_service.bookmarks.remove(bookmark)
            self.page.snack_bar = ft.SnackBar(ft.Text("تمت إزالة الإشارة المرجعية"))
        else:
            self.quran_service.bookmarks.append(bookmark)
            self.page.snack_bar = ft.SnackBar(ft.Text("تمت إضافة إشارة مرجعية"))
        self.page.snack_bar.open = True
        self.quran_service.save_bookmarks()
        self.page.update()
    
    def _share_ayah(self, e):
        """مشاركة الآية"""
        ayah_text = self._get_current_ayah_text()
        self.page.set_clipboard(f"{ayah_text}\nسورة {self._get_current_surah_name()} - الآية {self.current_ayah}")
        self.page.snack_bar = ft.SnackBar(ft.Text("تم نسخ الآية للحافظة"))
        self.page.snack_bar.open = True
        self.page.update()
    
    def _open_settings(self, e):
        """فتح إعدادات التطبيق"""
        def change_font_size(e):
            self.font_size = int(font_slider.value)
            self.ayah_text.size = self.font_size
            self.page.update()
        
        def toggle_dark_mode(e):
            self.dark_mode = not self.dark_mode
            self.page.theme_mode = ft.ThemeMode.DARK if self.dark_mode else ft.ThemeMode.LIGHT
            self.page.update()
        
        font_slider = ft.Slider(
            min=16, max=40, divisions=6,
            value=self.font_size,
            label="{value}px",
            on_change=change_font_size
        )
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("الإعدادات"),
            content=ft.Column([
                ft.Text("حجم الخط:", size=16),
                font_slider,
                ft.Switch(label="الوضع الليلي", value=self.dark_mode, on_change=toggle_dark_mode)
            ], tight=True),
            actions=[ft.TextButton("تم", on_click=lambda e: setattr(self.page.dialog, "open", False))]
        )
        self.page.dialog.open = True
        self.page.update()
    
    # --------------------------------------------
    # وظائف المساعدة
    # --------------------------------------------
    
    def _get_current_surah_data(self):
        """الحصول على بيانات السورة الحالية"""
        return next(
            s for s in self.quran_service.quran_data["surahs"] 
            if s["number"] == self.current_surah
        )
    
    def _get_current_surah_name(self):
        """الحصول على اسم السورة الحالية"""
        return self._get_current_surah_data()["name"]
    
    def _get_current_ayah_text(self):
        """الحصول على نص الآية الحالية"""
        surah = self._get_current_surah_data()
        return next(
            a["text"] for a in surah["ayahs"] 
            if a["number"] == self.current_ayah
        )
    
    def _update_display(self):
        """تحديث واجهة المستخدم"""
        self.ayah_text.value = self._get_current_ayah_text()
        self.tafsir_text.value = self.quran_service.get_tafsir(self.current_surah, self.current_ayah)
        self.page.views[-1].controls[0].controls[0].content.controls[0].value = \
            f"سورة {self._get_current_surah_name()} - الآية {self.current_ayah}"
        self.page.update()
    
    def _load_last_position(self):
        """تحميل آخر موضع تمت قراءته"""
        try:
            if os.path.exists("last_position.json"):
                with open("last_position.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_surah = data["surah"]
                    self.current_ayah = data["ayah"]
                    self.surah_dropdown.value = str(self.current_surah)
                    self._update_display()
        except:
            pass
    
    def _save_last_position(self, e=None):
        """حفظ الموضع الحالي"""
        with open("last_position.json", "w", encoding="utf-8") as f:
            json.dump({
                "surah": self.current_surah,
                "ayah": self.current_ayah
            }, f, ensure_ascii=False)

# --------------------------------------------
# تشغيل التطبيق
# --------------------------------------------

def main(page: ft.Page):
    QuranApp(page)

ft.app(target=main, view=ft.WEB_BROWSER)

# استدعاء الدالة clos عند الضغط على Enter أو الزر Submit
entry.bind("<Return>", clos)

# تشغيل نافذة tkinter
root.mainloop()
