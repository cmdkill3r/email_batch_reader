import imaplib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging

# ---------------- CONFIG ----------------
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
MAILBOX = "INBOX"
BATCH_SIZE = 200

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="email_bot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------- FUNCTIONS ----------------
def mark_emails_read(email, app_password, log_callback, status_callback, progress_callback):
    try:
        status_callback("🔄 Connecting to server...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(email, app_password)
        status_callback("📥 Fetching emails...")
        mail.select(MAILBOX)

        status, data = mail.search(None, "ALL")
        email_ids = data[0].split()
        total_emails = len(email_ids)
        log_callback(f"📧 Total emails found: {total_emails}")

        if total_emails == 0:
            status_callback("✅ Done (no emails found)")
            progress_callback(0, 0)
            return

        progress_callback(0, total_emails)

        for start in range(0, total_emails, BATCH_SIZE):
            batch = email_ids[start:start+BATCH_SIZE]
            for eid in batch:
                mail.store(eid, '+FLAGS', '\\Seen')
            log_callback(f"✅ Marked emails {start+1} to {min(start+BATCH_SIZE, total_emails)} as read")
            progress_callback(min(start + BATCH_SIZE, total_emails), total_emails)

        mail.logout()
        log_callback("🎉 All emails marked as read ✅")
        status_callback("✅ Done")

    except Exception as e:
        log_callback(f"❌ Error: {e}")
        status_callback("❌ Error")
        logging.error(f"Error: {e}")

def run_mark_emails(email, app_password, log_callback, status_callback, progress_callback):
    thread = threading.Thread(
        target=mark_emails_read,
        args=(email, app_password, log_callback, status_callback, progress_callback)
    )
    thread.start()

# ---------------- GUI ----------------
class EmailBatchReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Batch Reader - by CMDKILL3R")
        self.root.geometry("700x560")
        self.root.configure(bg="#121212")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", foreground="white", background="#121212", font=("Segoe UI", 10))
        style.configure("TButton", padding=6, relief="flat", background="#1f1f1f", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#333333")])
        style.configure("Horizontal.TProgressbar", troughcolor="#1e1e1e", background="#4CAF50", thickness=15)

        # Title
        title = ttk.Label(root, text="📧 Email Batch Reader", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)

        # Email + Password frame
        frame_inputs = ttk.Frame(root)
        frame_inputs.pack(pady=10)
        ttk.Label(frame_inputs, text="Email:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_email = ttk.Entry(frame_inputs, width=40)
        self.entry_email.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_inputs, text="App Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_password = ttk.Entry(frame_inputs, show="*", width=40)
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)

        # Run button
        self.btn_mark = ttk.Button(root, text="▶ Mark Emails as Read", command=self.start_marking)
        self.btn_mark.pack(pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(root, variable=self.progress_var, maximum=100, style="Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=15, pady=5)

        # Log window
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white", font=("Consolas", 10))
        self.log_area.pack(expand=True, fill="both", padx=10, pady=10)

        # Status bar
        self.status_var = tk.StringVar(value="💤 Idle")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, anchor="w", font=("Segoe UI", 9))
        self.status_bar.pack(fill="x", side="bottom")

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)

    def set_status(self, message):
        self.status_var.set(message)

    def set_progress(self, current, total):
        if total > 0:
            percent = (current / total) * 100
            self.progress_var.set(percent)
        else:
            self.progress_var.set(0)

    def start_marking(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter both email and app password.")
            return
        self.log("▶ Starting process...")
        self.set_status("⏳ Working...")
        self.set_progress(0, 0)
        run_mark_emails(email, password, self.log, self.set_status, self.set_progress)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailBatchReaderApp(root)
    root.mainloop()
