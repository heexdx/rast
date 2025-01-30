from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from pyzbar.pyzbar import decode
from PIL import Image as PILImage
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import cv2
import numpy as np
import os

# مفتاح التشفير - يجب أن يكون 32 بايت
key = b'12345678901234567890123456789012'  

def decrypt_data(encrypted_data, key):
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes[16:]), AES.block_size)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        return f"خطأ في فك التشفير: {str(e)}"

class QRReaderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.image = Image()
        self.layout.add_widget(self.image)
        
        self.label = Label(text="يرجى اختيار صورة تحتوي على رمز QR أو مسحها بالكاميرا", font_name='arial')
        self.layout.add_widget(self.label)
        
        self.file_chooser = FileChooserListView(path=os.path.expanduser("~/Desktop"), filters=['*.png', '*.jpg', '*.jpeg'])
        self.file_chooser.bind(on_selection=self.load_qr_from_file)
        self.layout.add_widget(self.file_chooser)
        
        self.add_file_button = Button(text="📂 اختيار صورة من الجهاز")
        self.add_file_button.bind(on_press=self.open_file_dialog)
        self.layout.add_widget(self.add_file_button)
        
        self.scan_button = Button(text="📷 مسح QR بالكاميرا")
        self.scan_button.bind(on_press=self.scan_qr_from_camera)
        self.layout.add_widget(self.scan_button)
        
        return self.layout
    
    def open_file_dialog(self, instance):
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("ملفات الصور", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image.source = file_path
            decoded_data = self.decode_qr(file_path)
            self.label.text = f"🔍 المحتوى المستخرج: {decoded_data}"
    
    def load_qr_from_file(self, chooser, selection):
        if selection:
            file_path = selection[0]
            self.image.source = file_path
            decoded_data = self.decode_qr(file_path)
            self.label.text = f"🔍 المحتوى المستخرج: {decoded_data}"
    
    def decode_qr(self, file_path):
        try:
            image = PILImage.open(file_path)
            decoded_objects = decode(image)
            if decoded_objects:
                encrypted_text = decoded_objects[0].data.decode('utf-8')
                return decrypt_data(encrypted_text, key)
            return "⚠️ لم يتم العثور على رمز QR في الصورة"
        except Exception as e:
            return f"⚠️ خطأ في قراءة الصورة: {str(e)}"
    
    def scan_qr_from_camera(self, instance):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.label.text = "⚠️ فشل في فتح الكاميرا"
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            decoded_objects = decode(frame)
            if decoded_objects:
                encrypted_text = decoded_objects[0].data.decode('utf-8')
                cap.release()
                cv2.destroyAllWindows()
                self.label.text = f"🔍 المحتوى المستخرج: {decrypt_data(encrypted_text, key)}"
                return
            cv2.imshow("📷 مسح رمز QR", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        self.label.text = "⚠️ لم يتم العثور على رمز QR عبر الكاميرا"

if __name__ == "__main__":
    QRReaderApp().run()
