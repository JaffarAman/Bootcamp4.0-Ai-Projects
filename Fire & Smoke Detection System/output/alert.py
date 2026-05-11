import time
import os
import ctypes
import threading
import smtplib
import cv2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import config


class AlertManager:
    def __init__(self, alarm_file="alarm.wav"):
        self.alarm_file = alarm_file
        self.is_alarming = False
        self._last_email_time = 0   # epoch seconds of last sent email

    # ── Public API ────────────────────────────────────────────────────────────

    def trigger(self, alert_type, frame=None):
        """
        Trigger audio alarm and (optionally) send an email alert.

        Parameters
        ----------
        alert_type : str
            Label shown in the alert message, e.g. "fire/smoke".
        frame : numpy.ndarray or None
            The current BGR video frame. When provided and email is enabled,
            it is JPEG-encoded and attached to the alert email.
        """
        if not self.is_alarming:
            self.is_alarming = True
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{timestamp}] ALERT: {alert_type.upper()} DETECTED! Waiting for User OK..."
            print(msg)

            # --- AUDIO ALARM (Windows MCI) ---
            self._play_audio()

            # --- EMAIL ALERT (non-blocking) ---
            if config.EMAIL_ENABLED:
                self._send_email_async(alert_type, timestamp, frame)

    def acknowledge(self):
        """Called when user presses 'A' to stop the alarm."""
        print("Alarm Acknowledged and Stopped by User.")
        self.is_alarming = False
        self._stop_audio()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _play_audio(self):
        if os.path.exists(self.alarm_file):
            abs_path = os.path.abspath(self.alarm_file)
            mci_path = f'"{abs_path}"'
            ctypes.windll.winmm.mciSendStringW("close myalarm", None, 0, None)
            ctypes.windll.winmm.mciSendStringW(
                f"open {mci_path} type mpegvideo alias myalarm", None, 0, None
            )
            ctypes.windll.winmm.mciSendStringW("play myalarm repeat", None, 0, None)
        else:
            print(f"Bhai '{self.alarm_file}' folder me nahi mili!")

    def _stop_audio(self):
        ctypes.windll.winmm.mciSendStringW("stop myalarm", None, 0, None)
        ctypes.windll.winmm.mciSendStringW("close myalarm", None, 0, None)

    def _send_email_async(self, alert_type, timestamp, frame):
        """Fire-and-forget: send email on a background thread so it never blocks the camera loop."""
        now = time.time()
        if now - self._last_email_time < config.EMAIL_COOLDOWN_SEC:
            remaining = int(config.EMAIL_COOLDOWN_SEC - (now - self._last_email_time))
            print(f"[Email] Cooldown active — next email in {remaining}s")
            return

        self._last_email_time = now  # update *before* spawning to prevent race conditions

        t = threading.Thread(
            target=self._send_email,
            args=(alert_type, timestamp, frame),
            daemon=True,
        )
        t.start()

    def _send_email(self, alert_type, timestamp, frame):
        """Build and send the MIME email with an optional screenshot attachment."""
        try:
            # ── Build message ─────────────────────────────────────────────────
            msg = MIMEMultipart("related")
            msg["Subject"] = config.EMAIL_SUBJECT
            msg["From"]    = config.SMTP_USER
            msg["To"]      = config.EMAIL_RECIPIENT

            # HTML body — inline image uses cid:screenshot
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #222;">
                <h2 style="color: #cc0000;">🔥 Fire / Smoke Detected!</h2>
                <table style="border-collapse: collapse;">
                    <tr><td><b>Alert Type</b></td><td>{alert_type.upper()}</td></tr>
                    <tr><td><b>Timestamp</b></td><td>{timestamp}</td></tr>
                    <tr><td><b>Source</b></td><td>Live Webcam</td></tr>
                </table>
                <br>
                <p>Screenshot captured at the moment of detection:</p>
                <img src="cid:screenshot" style="max-width:640px; border:2px solid #cc0000;" />
                <br><br>
                <p style="color: #888; font-size: 12px;">
                    This is an automated alert from the Fire &amp; Smoke Detection System.
                </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, "html"))

            # ── Attach screenshot ─────────────────────────────────────────────
            if frame is not None:
                success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if success:
                    img_bytes = buffer.tobytes()
                    image_part = MIMEImage(img_bytes, name="screenshot.jpg")
                    image_part.add_header("Content-ID", "<screenshot>")
                    image_part.add_header(
                        "Content-Disposition", "attachment", filename="screenshot.jpg"
                    )
                    msg.attach(image_part)
                else:
                    print("[Email] Warning: could not encode frame as JPEG.")

            # ── Send via SMTP ─────────────────────────────────────────────────
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.sendmail(config.SMTP_USER, config.EMAIL_RECIPIENT, msg.as_string())

            print(f"[Email] Alert sent to {config.EMAIL_RECIPIENT} at {timestamp}")

        except smtplib.SMTPAuthenticationError:
            print("[Email] ERROR: Authentication failed. Check SMTP_USER and SMTP_PASSWORD in config.py.")
            print("[Email] For Gmail, use an App Password: https://myaccount.google.com/apppasswords")
        except smtplib.SMTPException as e:
            print(f"[Email] SMTP error: {e}")
        except Exception as e:
            print(f"[Email] Unexpected error: {e}")