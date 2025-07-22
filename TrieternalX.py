import tkinter as tk
from tkinter import messagebox, Menu
import requests
import os
import socket
import sys
import threading
import subprocess
import speedtest
from inference import InferencePipeline
from inference.core.interfaces.stream.sinks import render_boxes
from PIL import Image, ImageTk
import keyboard
import cv2
import mediapipe as mp
from math import hypot
import screen_brightness_control as sbc
import numpy as np

class ControlSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrieternalX")
        self.root.configure(bg="#2c3e50")

        self.set_window_icon()

        self.gif_index = 0
        self.gif_frames = []
        self.load_gif_from_file("src/TrieternalX.gif")

        self.header_frame = tk.Frame(root, bg="black", height=100)
        self.header_frame.pack(fill=tk.X)

        self.header_label = tk.Label(self.header_frame, bg="black")
        self.header_label.pack()
        self.update_gif()

        self.label = tk.Label(root, text="Welcome to TrieternalX", font=("Arial", 24, "bold"), fg="white", bg="#2c3e50")
        self.label.pack(pady=20)

        self.button_frame = tk.Frame(root, bg="#2c3e50")
        self.button_frame.pack(pady=20)

        self.scan_button = tk.Button(
            self.button_frame, text="Artificial Intelligence\n Object Detection", command=self.simulate_scan,
            font=("Arial", 12, "bold"), bg="#3498db", fg="white", bd=0, relief="ridge", padx=10, pady=5
        )
        self.scan_button.pack(side=tk.LEFT, padx=10)

        self.network_button = tk.Button(
            self.button_frame, text="WI-FI Network Check", command=self.display_network_info,
            font=("Arial", 12, "bold"), bg="#e74c3c", fg="white", bd=0, relief="ridge", padx=20, pady=15
        )
        self.network_button.pack(side=tk.LEFT, padx=10)

        self.control_button = tk.Button(
            self.button_frame, text="Track IP & Phone", command=self.track_ip_phone,
            font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", bd=0, relief="ridge", padx=20, pady=15
        )
        self.control_button.pack(side=tk.LEFT, padx=10)

        self.brightness_button = tk.Button(
            self.button_frame, text="Artificial Intelligence\n Brightness Control", command=self.control_brightness,
            font=("Arial", 12, "bold"), bg="#9b59b6", fg="white", bd=0, relief="ridge", padx=10, pady=5
        )
        self.brightness_button.pack(side=tk.LEFT, padx=10)

        self.menu = Menu(root)
        root.config(menu=self.menu)

        file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Menu", menu=file_menu)
        file_menu.add_command(label="Keluar", command=self.exit_program)

        help_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Setting", menu=help_menu)
        help_menu.add_command(label="Version", command=lambda: messagebox.showinfo("Version", "TrieternalX version 3.1"))
        help_menu.add_command(label="Pencipta", command=lambda: messagebox.showinfo("Pencipta", "TrieternalX dibuat oleh Ariel Aprielyullah"))
        help_menu.add_command(label="Social Media", command=lambda: messagebox.showinfo("Social Media", "Website :https://arielaprielyullah.vercel.app\nInstagram :@lemzhr\nGithub :https://github.com/lemzhr"))
        help_menu.add_command(label="Warning", command=lambda: messagebox.showinfo("Warning", "di Kelola oleh TrieternalX."))
        
        self.root.bind("<Control-q>", self.exit_program)

        self.center_window()

    def set_window_icon(self):
        try:
            self.root.iconbitmap("src/TrieternalX.ico")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set window icon: {e}")

    def load_gif_from_file(self, filepath):
        try:
            gif = Image.open(filepath)
            while True:
                self.gif_frames.append(ImageTk.PhotoImage(gif.copy()))
                try:
                    gif.seek(gif.tell() + 1)
                except EOFError:
                    break
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {e}")

    def update_gif(self):
        if self.gif_frames:
            self.header_label.config(image=self.gif_frames[self.gif_index])
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.root.after(100, self.update_gif)

    def simulate_scan(self):
        try:
            self.root.iconbitmap("src/TrieternalX.ico")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set window icon: {e}")
        
        try:
            pipeline = InferencePipeline.init(
                model_id="yolov8n-640",
                video_reference=0,
                on_prediction=render_boxes
            )

            def stop_pipeline_after_keypress():
                print("Press Ctrl+Q to stop the program.")
                keyboard.wait("ctrl+q")
                pipeline.stop()

            thread = threading.Thread(target=pipeline.start)
            thread.start()

            stop_thread = threading.Thread(target=stop_pipeline_after_keypress)
            stop_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start detection: {e}")

    def control_brightness(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Kamera tidak terdeteksi.")
            return

        mpHands = mp.solutions.hands
        hands = mpHands.Hands()
        mpDraw = mp.solutions.drawing_utils

        while True:
            success, img = cap.read()
            if not success:
                break

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)
            lmList = []

            if results.multi_hand_landmarks:
                for handlandmark in results.multi_hand_landmarks:
                    for id, lm in enumerate(handlandmark.landmark):
                        h, w, _ = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])
                    mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

            if lmList:
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]

                length = hypot(x2 - x1, y2 - y1)
                bright = np.interp(length, [15, 220], [0, 100])
                sbc.set_brightness(int(bright))

            cv2.imshow('Brightness Control', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def track_ip_phone(self):
        def get_public_ip():
            try:
                response = requests.get("https://api.ipify.org?format=json")
                data = response.json()
                return data["ip"]
            except Exception as e:
                return f"Error: {str(e)}"

        def get_location(ip_address):
            try:
                response = requests.get(f"http://ip-api.com/json/{ip_address}")
                data = response.json()

                if data['status'] == 'success':
                    location_info = (
                        f"IP Address: {data['query']}\n"
                        f"Country: {data['country']}\n"
                        f"Region: {data['regionName']}\n"
                        f"City: {data['city']}\n"
                        f"ZIP: {data.get('zip', 'N/A')}\n"
                        f"Latitude: {data['lat']}\n"
                        f"Longitude: {data['lon']}\n"
                        f"ISP: {data['isp']}"
                    )
                    return location_info
                else:
                    return "Error: Could not retrieve location information."
            except Exception as e:
                return f"Error: {str(e)}"

        def track_ip():
            ip_address = ip_entry.get()
            if not ip_address:
                messagebox.showerror("Error", "Masukkan IP Address terlebih dahulu.")
                return

            location_info = get_location(ip_address)
            result_label.config(text=location_info)

        def track_gateway():
            gateway_ip = get_public_ip()
            if gateway_ip.startswith("Error"):
                messagebox.showerror("Error", gateway_ip)
                return

            location_info = get_location(gateway_ip)
            result_label.config(text=f"IP Gateway Publik: {gateway_ip}\n\n{location_info}")

        def track_phone():
            phone_number = phone_entry.get()
            if not phone_number:
                messagebox.showerror("Error", "Masukkan nomor telepon terlebih dahulu.")
                return

            prefix_data = {
                "+6281": "Jawa Barat",
                "+6282": "Jawa Tengah",
                "+6283": "Jawa Timur",
                "+6285": "Sumatera Utara",
                "+6286": "Sumatera Selatan",
                "+6287": "Bali dan Nusa Tenggara",
                "+6288": "Kalimantan",
                "+6289": "Sulawesi",
            }

            prefix = phone_number[:5]
            location = prefix_data.get(prefix, "Lokasi tidak diketahui atau nomor salah.")

            result_label.config(text=f"Nomor Telepon: {phone_number}\nLokasi: {location}")

        ip_phone_window = tk.Toplevel(self.root)
        ip_phone_window.title("IP & Phone Tracker")
        ip_phone_window.geometry("500x700")
        ip_phone_window.configure(bg="black")

        header_label = tk.Label(ip_phone_window, text="IP & Phone Tracker", font=("Arial", 18, "bold"), fg="white", bg="black")
        header_label.pack(pady=10)

        ip_frame = tk.Frame(ip_phone_window, bg="black")
        ip_frame.pack(pady=10)

        ip_label = tk.Label(ip_frame, text="Masukkan IP Address:", font=("Arial", 12), fg="white", bg="black")
        ip_label.grid(row=0, column=0, padx=5)

        ip_entry = tk.Entry(ip_frame, font=("Arial", 12), width=30)
        ip_entry.grid(row=0, column=1, padx=5)

        track_button = tk.Button(ip_phone_window, text="Lacak IP Address", font=("Arial", 12), command=track_ip, bg="blue", fg="white")
        track_button.pack(pady=10)

        gateway_button = tk.Button(ip_phone_window, text="Lacak IP Gateway Publik", font=("Arial", 12), command=track_gateway, bg="green", fg="white")
        gateway_button.pack(pady=10)

        phone_frame = tk.Frame(ip_phone_window, bg="black")
        phone_frame.pack(pady=10)

        phone_label = tk.Label(phone_frame, text="Masukkan Nomor Telepon:", font=("Arial", 12), fg="white", bg="black")
        phone_label.grid(row=0, column=0, padx=5)

        phone_entry = tk.Entry(phone_frame, font=("Arial", 12), width=30)
        phone_entry.grid(row=0, column=1, padx=5)

        phone_button = tk.Button(ip_phone_window, text="Lacak Nomor Telepon", font=("Arial", 12), command=track_phone, bg="orange", fg="white")
        phone_button.pack(pady=10)

        result_label = tk.Label(ip_phone_window, text="", font=("Arial", 12), fg="white", bg="black", justify="left", wraplength=450)
        result_label.pack(pady=20)

        exit_button = tk.Button(ip_phone_window, text="Keluar", font=("Arial", 12), command=ip_phone_window.destroy, bg="red", fg="white")
        exit_button.pack(pady=10)

    def exit_program(self, event=None):
        sys.exit()

    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
        x = screen_width // 2 - size[0] // 2
        y = screen_height // 2 - size[1] // 2
        self.root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

    def display_network_info(self):
        try:
            self.root.iconbitmap("src/TrieternalX.ico")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set window icon: {e}")
        
        ip_address, gateway = self.get_ip_and_gateway()
        network_type = self.get_network_type()
        download_speed, upload_speed = self.get_network_speed()

        info_text = (
            f"Informasi Jaringan:\n"
            f"IP Address: {ip_address if ip_address else 'Tidak dapat mendeteksi IP Address'}\n"
            f"Gateway: {gateway if gateway else 'Tidak dapat mendeteksi Gateway'}\n"
            f"Jenis Koneksi: {network_type}\n"
            f"Kecepatan Download: {download_speed if download_speed else 'Tidak dapat mendeteksi'} Mbps\n"
            f"Kecepatan Upload: {upload_speed if upload_speed else 'Tidak dapat mendeteksi'} Mbps"
        )

        messagebox.showinfo("Informasi Jaringan", info_text)

    def get_ip_and_gateway(self):
        try:
            if os.name == "nt":
                result = subprocess.check_output("ipconfig", shell=True).decode()
                ip_line = gateway_line = ""
                for line in result.splitlines():
                    if "IPv4 Address" in line:
                        ip_line = line
                    if "Default Gateway" in line:
                        gateway_line = line
                ip_address = ip_line.split(":")[-1].strip()
                gateway = gateway_line.split(":")[-1].strip()
            else:
                result = subprocess.check_output("ip route", shell=True).decode()
                ip_address = socket.gethostbyname(socket.gethostname())
                gateway = None
                for line in result.splitlines():
                    if "default via" in line:
                        gateway = line.split()[2]
            return ip_address, gateway
        except Exception as e:
            return None, None

    def get_network_type(self):
        try:
            if os.name == "nt":
                result = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
                if "SSID" in result:
                    return "Wi-Fi"
                else:
                    return "Data Seluler (atau koneksi lainnya)"
            else:
                result = subprocess.check_output("nmcli dev status", shell=True).decode()
                if "wifi" in result:
                    return "Wi-Fi"
                else:
                    return "Data Seluler (atau koneksi lainnya)"
        except Exception as e:
            return "Tidak dapat mendeteksi tipe koneksi"

    def get_network_speed(self):
        try:
            st = speedtest.Speedtest()
            download_speed = st.download() / 1_000_000
            upload_speed = st.upload() / 1_000_000
            return round(download_speed, 2), round(upload_speed, 2)
        except Exception as e:
            return None, None

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlSimulatorApp(root)
    root.mainloop()
