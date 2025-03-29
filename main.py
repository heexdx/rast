import flet as ft

def main(page: ft.Page):
    # Configure your app
    page.title = "Quran App"
    
    # Add your app content here
    page.add(
        ft.Text("Your Quran App Content")
    )

ft.app(target=main)
