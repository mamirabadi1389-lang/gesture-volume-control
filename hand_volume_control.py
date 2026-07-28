
import threading
import time

import cv2
import mediapipe as mp
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# ---------------------------------------------------------------------------
#  کنترل‌کننده‌ی صدای سیستم (ویندوز)
# ---------------------------------------------------------------------------
class SystemVolume:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = interface.QueryInterface(IAudioEndpointVolume)

    def set_percent(self, percent: float):
        """percent بین 0 تا 100"""
        percent = max(0.0, min(100.0, percent))
        self.volume.SetMasterVolumeLevelScalar(percent / 100.0, None)

    def get_percent(self) -> float:
        return self.volume.GetMasterVolumeLevelScalar() * 100.0

    def set_mute(self, mute: bool):
        self.volume.SetMute(1 if mute else 0, None)


# ---------------------------------------------------------------------------
#  ترد پردازش دوربین + تشخیص دست (این بخش هرگز مستقیم UI را لمس نمی‌کند)
# ---------------------------------------------------------------------------
class HandTrackerThread(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        self.running = False
        self.cap = None
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self.smoothed_vol = None

    def start_camera(self, cam_index: int):
        self.cap = cv2.VideoCapture(cam_index)
        if not self.cap.isOpened():
            self.app.report_error(f"دوربین شماره {cam_index} باز نشد.")
            return False
        self.running = True
        return True

    def stop_camera(self):
        self.running = False
        time.sleep(0.1)
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def run(self):
        prev_time = time.time()

        while True:
            if not self.running or self.cap is None:
                time.sleep(0.05)
                continue

            success, img = self.cap.read()
            if not success:
                continue

            img = cv2.flip(img, 1)  # حالت آینه‌ای، طبیعی‌تره
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            fist_locked = False

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                mp.solutions.drawing_utils.draw_landmarks(
                    img, hand, self.mpHands.HAND_CONNECTIONS
                )

                h, w, _ = img.shape
                lmList = [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]

                x1, y1 = lmList[4]
                x2, y2 = lmList[8]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # تشخیص مشت: اگر نوک انگشتان به کف دست نزدیک باشند، یعنی مشت کرده
                # (برای قفل کردن صدا و جلوگیری از تغییر ناخواسته)
                wrist = lmList[0]
                tip_ids = [8, 12, 16, 20]
                avg_tip_dist = np.mean(
                    [math_dist(lmList[t], wrist) for t in tip_ids]
                )
                fist_locked = avg_tip_dist < self.app.get_fist_threshold()

                cv2.circle(img, (x1, y1), 10, (255, 255, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 255, 0), cv2.FILLED)
                cv2.circle(img, (cx, cy), 10, (255, 255, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 255, 0), 3)

                length = math_dist((x1, y1), (x2, y2))
                min_r, max_r = self.app.get_hand_range()
                raw_percent = np.interp(length, [min_r, max_r], [0, 100])
                raw_percent = float(np.clip(raw_percent, 0, 100))

                # هموارسازی (Exponential Smoothing) تا صدا نپره
                alpha = self.app.get_smoothing()
                if self.smoothed_vol is None:
                    self.smoothed_vol = raw_percent
                else:
                    self.smoothed_vol = (
                        alpha * raw_percent + (1 - alpha) * self.smoothed_vol
                    )

                if not fist_locked:
                    self.app.sys_volume.set_percent(self.smoothed_vol)

                bar_color = (0, 255, 0) if not fist_locked else (0, 0, 255)
                cv2.putText(
                    img,
                    f"{int(self.smoothed_vol)}%",
                    (x2 + 15, y2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    bar_color,
                    2,
                )
                if fist_locked:
                    cv2.putText(
                        img, "LOCKED", (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2
                    )

            # FPS
            now = time.time()
            fps = 1 / (now - prev_time) if now != prev_time else 0
            prev_time = now
            cv2.putText(
                img, f"FPS: {int(fps)}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )

            self.app.update_preview(img, fist_locked)


def math_dist(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


# ---------------------------------------------------------------------------
#  رابط گرافیکی
# ---------------------------------------------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("کنترل صدا با دست")
        self.geometry("980x640")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.sys_volume = SystemVolume()
        self.tracker = HandTrackerThread(self)
        self.tracker.start()

        self.camera_running = False

        self._build_ui()
        self._refresh_volume_label()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # --- ستون چپ: پیش‌نمایش دوربین ---
        self.video_frame = ctk.CTkFrame(self, width=640, height=480)
        self.video_frame.pack(side="left", padx=15, pady=15)
        self.video_frame.pack_propagate(False)

        self.video_label = ctk.CTkLabel(self.video_frame, text="دوربین خاموش است")
        self.video_label.pack(expand=True, fill="both")

        # --- ستون راست: پنل تنظیمات ---
        panel = ctk.CTkFrame(self, width=280)
        panel.pack(side="right", fill="y", padx=10, pady=15)

        ctk.CTkLabel(
            panel, text="⚙ تنظیمات کنترل صدا با دست",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        # دکمه شروع/توقف
        self.toggle_btn = ctk.CTkButton(
            panel, text="▶ شروع دوربین", command=self.toggle_camera,
            fg_color="#2fa572"
        )
        self.toggle_btn.pack(pady=10, padx=15, fill="x")

        # انتخاب دوربین
        ctk.CTkLabel(panel, text="شماره دوربین:").pack(pady=(10, 0))
        self.cam_index_var = ctk.StringVar(value="0")
        self.cam_menu = ctk.CTkOptionMenu(
            panel, values=["0", "1", "2"], variable=self.cam_index_var
        )
        self.cam_menu.pack(pady=5, padx=15, fill="x")

        # نوار صدا
        ctk.CTkLabel(panel, text="میزان صدا:").pack(pady=(20, 0))
        self.volume_label = ctk.CTkLabel(panel, text="0%", font=ctk.CTkFont(size=22))
        self.volume_label.pack(pady=5)
        self.volume_bar = ctk.CTkProgressBar(panel, width=220)
        self.volume_bar.pack(pady=5)
        self.volume_bar.set(0)

        # بازه‌ی فاصله (Min / Max)
        ctk.CTkLabel(panel, text="حداقل فاصله (صدای خاموش):").pack(pady=(20, 0))
        self.min_range_slider = ctk.CTkSlider(
            panel, from_=10, to=150, number_of_steps=140,
            command=lambda v: self.min_range_label.configure(text=f"{int(v)} px")
        )
        self.min_range_slider.set(30)
        self.min_range_slider.pack(pady=5, padx=15, fill="x")
        self.min_range_label = ctk.CTkLabel(panel, text="30 px")
        self.min_range_label.pack()

        ctk.CTkLabel(panel, text="حداکثر فاصله (صدای کامل):").pack(pady=(15, 0))
        self.max_range_slider = ctk.CTkSlider(
            panel, from_=100, to=400, number_of_steps=300,
            command=lambda v: self.max_range_label.configure(text=f"{int(v)} px")
        )
        self.max_range_slider.set(250)
        self.max_range_slider.pack(pady=5, padx=15, fill="x")
        self.max_range_label = ctk.CTkLabel(panel, text="250 px")
        self.max_range_label.pack()

        # هموارسازی
        ctk.CTkLabel(panel, text="نرمی حرکت صدا (Smoothing):").pack(pady=(20, 0))
        self.smoothing_slider = ctk.CTkSlider(panel, from_=0.05, to=1.0)
        self.smoothing_slider.set(0.3)
        self.smoothing_slider.pack(pady=5, padx=15, fill="x")

        # آستانه‌ی مشت (قفل صدا)
        ctk.CTkLabel(panel, text="حساسیت قفل با مشت:").pack(pady=(20, 0))
        self.fist_slider = ctk.CTkSlider(panel, from_=40, to=150)
        self.fist_slider.set(80)
        self.fist_slider.pack(pady=5, padx=15, fill="x")

        # وضعیت
        self.status_label = ctk.CTkLabel(panel, text="", text_color="orange")
        self.status_label.pack(pady=15)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------
    def toggle_camera(self):
        if not self.camera_running:
            cam_index = int(self.cam_index_var.get())
            ok = self.tracker.start_camera(cam_index)
            if ok:
                self.camera_running = True
                self.toggle_btn.configure(text="⏹ توقف دوربین", fg_color="#c0392b")
                self.status_label.configure(text="")
        else:
            self.tracker.stop_camera()
            self.camera_running = False
            self.toggle_btn.configure(text="▶ شروع دوربین", fg_color="#2fa572")
            self.video_label.configure(image=None, text="دوربین خاموش است")

    def report_error(self, msg: str):
        self.status_label.configure(text=msg)
        self.camera_running = False
        self.toggle_btn.configure(text="▶ شروع دوربین", fg_color="#2fa572")

    # این تابع از ترد دیگری صدا زده می‌شود؛ فقط داده رو داخل after می‌ذاریم
    def update_preview(self, img_bgr, fist_locked):
        self.after(0, self._render_frame, img_bgr)

    def _render_frame(self, img_bgr):
        if not self.camera_running:
            return
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb).resize((640, 480))
        imgtk = ImageTk.PhotoImage(image=pil_img)
        self.video_label.imgtk = imgtk  # جلوگیری از garbage collection
        self.video_label.configure(image=imgtk, text="")
        self._refresh_volume_label()

    def _refresh_volume_label(self):
        try:
            percent = self.sys_volume.get_percent()
            self.volume_label.configure(text=f"{int(percent)}%")
            self.volume_bar.set(percent / 100.0)
        except Exception:
            pass
        self.after(300, self._refresh_volume_label)

    # ------------------------------------------------------------------
    def get_hand_range(self):
        return self.min_range_slider.get(), self.max_range_slider.get()

    def get_smoothing(self):
        return self.smoothing_slider.get()

    def get_fist_threshold(self):
        return self.fist_slider.get()

    def on_close(self):
        self.tracker.stop_camera()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
