import flet as ft

def main(page: ft.Page):
    page.title = "Quran App"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_width = 400
    page.window_height = 850
    page.window_resizable = False
    
    # Add your app content here
    page.add(
        ft.Text(
            "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            size=24,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.BOLD
        )
    )

ft.app(target=main)
