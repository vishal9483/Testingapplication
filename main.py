#!/usr/bin/env python3
import os
import time
import threading
import logging
import traceback
import csv
from datetime import datetime
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class TextHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)


class BatchTesterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Batch Testing Utility")
        self.geometry("800x600")
        self.input_folder_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()
        self.current_module_var = tk.StringVar()
        self.current_file_var = tk.StringVar()
        self.progress_var = tk.StringVar()
        self.failure_var = tk.StringVar()
        self.module_vars = {
            "Test Data Extraction": tk.StringVar(),
            "Test JSON Output (Windows DLL)": tk.StringVar(),
            "Test JSON Output (Linux DLL)": tk.StringVar(),
            "Test Automatic Drawing": tk.StringVar(),
        }
        self.summary_data = []
        self.log_queue = queue.Queue()
        self.logger = logging.getLogger("BatchTester")
        self.logger.setLevel(logging.DEBUG)
        self._setup_logging()
        self._create_widgets()
        self.after(100, self._process_log_queue)

    def _setup_logging(self):
        handler = TextHandler(self.log_queue)
        handler.setLevel(logging.INFO)
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(fmt)
        self.logger.addHandler(handler)

    def _create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top = ttk.LabelFrame(frame, text="Global Folders")
        top.pack(fill=tk.X, pady=5)
        ttk.Label(top, text="Input Folder:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(top, textvariable=self.input_folder_var, width=50).grid(row=0, column=1, sticky=tk.W)
        ttk.Button(top, text="Browse", command=self._browse_input).grid(row=0, column=2, padx=5)
        ttk.Label(top, text="Output Folder:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(top, textvariable=self.output_folder_var, width=50).grid(row=1, column=1, sticky=tk.W)
        ttk.Button(top, text="Browse", command=self._browse_output).grid(row=1, column=2, padx=5)
        ttk.Button(top, text="Open", command=self._open_output_folder).grid(row=1, column=3, padx=5)

        mod_frame = ttk.LabelFrame(frame, text="Modules")
        mod_frame.pack(fill=tk.X, pady=5)
        for idx, (name, var) in enumerate(self.module_vars.items()):
            ttk.Label(mod_frame, text=name).grid(row=idx, column=0, sticky=tk.W)
            ttk.Entry(mod_frame, textvariable=var, width=40).grid(row=idx, column=1, sticky=tk.W)
            ttk.Button(mod_frame, text="Browse", command=lambda n=name, v=var: self._browse_module(n, v)).grid(row=idx, column=2, padx=5)
            ttk.Button(mod_frame, text="Run", command=lambda n=name: self._run_module(n)).grid(row=idx, column=3, padx=5)

        ctl_frame = ttk.Frame(frame)
        ctl_frame.pack(fill=tk.X, pady=5)
        ttk.Button(ctl_frame, text="▶️ Run All", command=self._run_all).pack(side=tk.LEFT)

        status = ttk.LabelFrame(frame, text="Status")
        status.pack(fill=tk.BOTH, expand=True, pady=5)
        lbls = ttk.Frame(status)
        lbls.pack(fill=tk.X)
        ttk.Label(lbls, text="Module:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(lbls, textvariable=self.current_module_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(lbls, text="File:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        ttk.Label(lbls, textvariable=self.current_file_var).grid(row=0, column=3, sticky=tk.W)
        ttk.Label(lbls, text="Progress:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
        ttk.Label(lbls, textvariable=self.progress_var).grid(row=0, column=5, sticky=tk.W)
        ttk.Label(lbls, text="Failures:").grid(row=0, column=6, sticky=tk.W, padx=(10, 0))
        ttk.Label(lbls, textvariable=self.failure_var).grid(row=0, column=7, sticky=tk.W)
        self.text_log = ScrolledText(status, height=15)
        self.text_log.pack(fill=tk.BOTH, expand=True)

    def _browse_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_folder_var.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_folder_var.set(path)

    def _browse_module(self, module_name, var):
        if "DLL" in module_name:
            path = filedialog.askopenfilename(
                title=f"Select {module_name}",
                filetypes=[("DLL files", "*.dll"), ("All files", "*.*")]
            )
        else:
            path = filedialog.askdirectory()
        if path:
            var.set(path)

    def _open_output_folder(self):
        path = self.output_folder_var.get()
        if path and os.path.isdir(path):
            try:
                os.startfile(path)
            except Exception:
                messagebox.showerror("Error", f"Cannot open folder: {path}")

    def _process_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.text_log.insert(tk.END, msg + "\n")
                self.text_log.see(tk.END)
        except queue.Empty:
            pass
        self.after(100, self._process_log_queue)

    def _log(self, message, level=logging.INFO):
        if level == logging.ERROR:
            self.logger.error(message)
        else:
            self.logger.info(message)

    def _setup_file_logging(self, timestamp):
        out = self.output_folder_var.get()
        if not out:
            return
        fn = os.path.join(out, f"run_{timestamp}.log")
        fh = logging.FileHandler(fn, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

    def _run_module(self, module_name):
        inp = self.module_vars[module_name].get()
        out = self.output_folder_var.get()
        if not inp or not out:
            messagebox.showwarning("Missing Paths", "Select module input and global output folders.")
            return
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.summary_data = []
        self._setup_file_logging(timestamp)
        thread = threading.Thread(target=self._worker_module, args=(module_name, inp, timestamp), daemon=True)
        thread.start()

    def _worker_module(self, module_name, inp, timestamp):
        self.current_module_var.set(module_name)
        total = sum(len(files) for _, _, files in os.walk(inp))
        processed = failures = 0
        for root, _, files in os.walk(inp):
            for fname in files:
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(root, inp)
                out_dir = os.path.join(self.output_folder_var.get(), module_name, rel)
                os.makedirs(out_dir, exist_ok=True)
                self.current_file_var.set(fname)
                processed += 1
                self.progress_var.set(f"{processed} of {total}")
                try:
                    self._log(f"Processing file: {fpath}")
                    time.sleep(0.1)
                    status = "Success"
                    reason = ""
                    self.logger.info(f"{module_name} processed {fpath}")
                except Exception:
                    failures += 1
                    status = "Failed"
                    reason = traceback.format_exc()
                    self.logger.error(f"Error on {fpath}:\n{reason}")
                self.summary_data.append({"module": module_name, "file": fpath, "status": status, "reason": reason.strip()})
                self.failure_var.set(str(failures))
        summary = os.path.join(self.output_folder_var.get(), f"summary_{module_name}_{timestamp}.csv")
        with open(summary, 'w', newline='', encoding='utf-8') as csvf:
            writer = csv.DictWriter(csvf, fieldnames=["module", "file", "status", "reason"])
            writer.writeheader()
            for row in self.summary_data:
                writer.writerow(row)
        messagebox.showinfo("Summary", f"Module {module_name} completed: {processed} files, {failures} failures.\nSummary: {summary}")

    def _run_all(self):
        if not self.input_folder_var.get() or not self.output_folder_var.get():
            messagebox.showwarning("Missing Paths", "Select global input and output folders.")
            return
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.summary_data = []
        self._setup_file_logging(timestamp)
        thread = threading.Thread(target=self._worker_all, args=(timestamp,), daemon=True)
        thread.start()

    def _worker_all(self, timestamp):
        modules = [(m, v.get()) for m, v in self.module_vars.items() if v.get()]
        if not modules:
            self._log("No modules selected.")
            return
        for m, inp in modules:
            self._log(f"Starting module {m}")
            self.current_module_var.set(m)
            total = sum(len(files) for _, _, files in os.walk(inp))
            processed = failures = 0
            for root, _, files in os.walk(inp):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    rel = os.path.relpath(root, inp)
                    out_dir = os.path.join(self.output_folder_var.get(), m, rel)
                    os.makedirs(out_dir, exist_ok=True)
                    self.current_file_var.set(fname)
                    processed += 1
                    self.progress_var.set(f"{processed} of {total}")
                    try:
                        self._log(f"Processing file: {fpath}")
                        time.sleep(0.1)
                        status = "Success"
                        reason = ""
                        self.logger.info(f"{m} processed {fpath}")
                    except Exception:
                        failures += 1
                        status = "Failed"
                        reason = traceback.format_exc()
                        self.logger.error(f"Error on {fpath}:\n{reason}")
                    self.summary_data.append({"module": m, "file": fpath, "status": status, "reason": reason.strip()})
                    self.failure_var.set(str(failures))
            self._log(f"Module {m} done: {processed} files, {failures} failures.")
        summary = os.path.join(self.output_folder_var.get(), f"summary_{timestamp}.csv")
        with open(summary, 'w', newline='', encoding='utf-8') as csvf:
            writer = csv.DictWriter(csvf, fieldnames=["module", "file", "status", "reason"])
            writer.writeheader()
            for row in self.summary_data:
                writer.writerow(row)
        messagebox.showinfo("Summary", f"All modules completed. Summary: {summary}")


def main():
    app = BatchTesterApp()
    app.mainloop()


if __name__ == '__main__':
    main()