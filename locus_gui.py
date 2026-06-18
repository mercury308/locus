import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import asyncio
import csv
from datetime import datetime
from locus_scanner import (
    scan_ips_bulk,
    parse_ips_from_text,
    parse_ips_from_file,
)


class LocusGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Locus - IP Geolocation Scanner')
        self.root.geometry('1200x700')
        self.root.minsize(1000, 600)

        self.results = []
        self.is_scanning = False

        self._setup_ui()

    def _setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.input_frame = ttk.Frame(notebook)
        self.results_frame = ttk.Frame(notebook)
        notebook.add(self.input_frame, text='Input & Scan')
        notebook.add(self.results_frame, text='Results')

        self._setup_input_tab()
        self._setup_results_tab()
        self._setup_status_bar()

    def _setup_input_tab(self):
        container = ttk.Frame(self.input_frame)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(container, text='Manual IP Input', font=('Arial', 10, 'bold')).pack(
            anchor='w'
        )
        ttk.Label(
            container,
            text='Enter one IP per line (e.g., 8.8.8.8)',
            font=('Arial', 9),
        ).pack(anchor='w')

        text_frame = ttk.Frame(container)
        text_frame.pack(fill='both', expand=True, pady=(5, 10))

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        self.ip_text = tk.Text(
            text_frame,
            height=10,
            wrap='word',
            yscrollcommand=scrollbar.set,
        )
        self.ip_text.pack(fill='both', expand=True)
        scrollbar.config(command=self.ip_text.yview)

        button_frame = ttk.Frame(container)
        button_frame.pack(fill='x', pady=(0, 10))

        ttk.Button(button_frame, text='Load from File', command=self._load_file).pack(
            side='left', padx=5
        )
        ttk.Button(button_frame, text='Clear', command=self._clear_input).pack(
            side='left', padx=5
        )

        ttk.Separator(container, orient='horizontal').pack(fill='x', pady=10)

        scan_frame = ttk.Frame(container)
        scan_frame.pack(fill='x')

        self.scan_btn = ttk.Button(
            scan_frame, text='Start Scan', command=self._start_scan
        )
        self.scan_btn.pack(side='left', padx=5)

        self.progress = ttk.Progressbar(
            scan_frame,
            mode='determinate',
            length=300,
        )
        self.progress.pack(side='left', fill='x', expand=True, padx=5)

        self.progress_label = ttk.Label(scan_frame, text='Ready')
        self.progress_label.pack(side='left', padx=5)

    def _setup_results_tab(self):
        container = ttk.Frame(self.results_frame)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(container)
        button_frame.pack(fill='x', pady=(0, 10))

        ttk.Button(button_frame, text='Export to CSV', command=self._export_csv).pack(
            side='left', padx=5
        )
        ttk.Button(button_frame, text='Clear Results', command=self._clear_results).pack(
            side='left', padx=5
        )

        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill='both', expand=True)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side='right', fill='y')

        scrollbar_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')

        columns = (
            'IP',
            'Status',
            'Country',
            'City',
            'ISP',
            'VPN',
            'Proxy',
            'Tor',
            'Fraud Score',
            'Error',
        )
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            height=20,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        self.tree.column('#0', width=0, stretch='no')
        self.tree.column('IP', anchor='w', width=120)
        self.tree.column('Status', anchor='w', width=80)
        self.tree.column('Country', anchor='w', width=100)
        self.tree.column('City', anchor='w', width=100)
        self.tree.column('ISP', anchor='w', width=150)
        self.tree.column('VPN', anchor='center', width=60)
        self.tree.column('Proxy', anchor='center', width=60)
        self.tree.column('Tor', anchor='center', width=60)
        self.tree.column('Fraud Score', anchor='center', width=100)
        self.tree.column('Error', anchor='w', width=200)

        for col in columns:
            self.tree.heading(col, text=col)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        self.tree.pack(fill='both', expand=True)

    def _setup_status_bar(self):
        self.status_var = tk.StringVar(value='Ready')
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
        )
        status_bar.pack(fill='x', side='bottom')

    def _load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Text Files', '*.txt'), ('CSV Files', '*.csv'), ('All', '*.*')]
        )
        if file_path:
            try:
                ips = parse_ips_from_file(file_path)
                self.ip_text.delete('1.0', 'end')
                self.ip_text.insert('1.0', '\n'.join(ips))
                self.status_var.set(f'Loaded {len(ips)} IPs from file')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to load file: {e}')

    def _clear_input(self):
        self.ip_text.delete('1.0', 'end')

    def _clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results = []

    def _start_scan(self):
        ip_text = self.ip_text.get('1.0', 'end-1c').strip()
        if not ip_text:
            messagebox.showwarning('Warning', 'Please enter or load IPs')
            return

        ips = parse_ips_from_text(ip_text)
        if not ips:
            messagebox.showwarning('Warning', 'No valid IPs found')
            return

        self.is_scanning = True
        self.scan_btn.config(state='disabled')
        self.progress.config(maximum=len(ips), value=0)

        thread = threading.Thread(target=self._run_scan, args=(ips,), daemon=True)
        thread.start()

    def _run_scan(self, ips):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(
                scan_ips_bulk(ips, progress_callback=self._update_progress)
            )
        finally:
            loop.close()

    def _update_progress(self, completed: int, total: int):
        self.progress.config(value=completed)
        self.progress_label.config(text=f'{completed}/{total}')
        self.status_var.set(f'Scanning: {completed}/{total}')
        self.root.update_idletasks()

        if completed == total:
            self._finish_scan()

    def _finish_scan(self):
        def finish():
            self.is_scanning = False
            self.scan_btn.config(state='normal')
            self.status_var.set(f'Scan complete: {self.progress.cget("value")} IPs')

            thread = threading.Thread(target=self._fetch_and_display_results, daemon=True)
            thread.start()

        self.root.after(100, finish)

    def _fetch_and_display_results(self):
        ip_text = self.ip_text.get('1.0', 'end-1c').strip()
        ips = parse_ips_from_text(ip_text)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = loop.run_until_complete(scan_ips_bulk(ips))
            loop.close()

            self.results = results
            self._display_results(results)
        except Exception as e:
            messagebox.showerror('Scan Error', f'Scan failed: {e}')
            self.status_var.set('Scan failed')

    def _display_results(self, results):
        def display():
            self._clear_results()
            for result in results:
                values = (
                    result['ip'],
                    result['status'],
                    result['location'].get('country', 'N/A'),
                    result['location'].get('city', 'N/A'),
                    result.get('isp', 'N/A'),
                    'Yes' if result['security'].get('vpn') else 'No',
                    'Yes' if result['security'].get('proxy') else 'No',
                    'Yes' if result['security'].get('tor') else 'No',
                    str(result['security'].get('fraud_score', 'N/A')),
                    result['error'] or '',
                )
                self.tree.insert('', 'end', values=values)

        self.root.after(0, display)

    def _export_csv(self):
        if not self.results:
            messagebox.showwarning('Warning', 'No results to export')
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Files', '*.csv'), ('All', '*.*')],
            initialfile=f'locus_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = [
                    'IP',
                    'Status',
                    'Country',
                    'City',
                    'Region',
                    'Latitude',
                    'Longitude',
                    'ISP',
                    'VPN',
                    'Proxy',
                    'Tor',
                    'Fraud Score',
                    'Is Bot',
                    'Error',
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for result in self.results:
                    writer.writerow(
                        {
                            'IP': result['ip'],
                            'Status': result['status'],
                            'Country': result['location'].get('country', ''),
                            'City': result['location'].get('city', ''),
                            'Region': result['location'].get('region', ''),
                            'Latitude': result['location'].get('latitude', ''),
                            'Longitude': result['location'].get('longitude', ''),
                            'ISP': result.get('isp', ''),
                            'VPN': result['security'].get('vpn', ''),
                            'Proxy': result['security'].get('proxy', ''),
                            'Tor': result['security'].get('tor', ''),
                            'Fraud Score': result['security'].get('fraud_score', ''),
                            'Is Bot': result['security'].get('is_bot', ''),
                            'Error': result['error'] or '',
                        }
                    )

            messagebox.showinfo('Success', f'Results exported to {file_path}')
            self.status_var.set(f'Results exported: {file_path}')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export: {e}')


def main():
    root = tk.Tk()
    app = LocusGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
