import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import os
import threading
from pathlib import Path
import sys



class VisioTempFileRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Visio Temp File Remover")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.directory_var = tk.StringVar(value="Z:\\ENGINEERING TEMPLATES\\VISIO SHAPES 2025")
        self.found_files = []
        self.selected_files = []
        
        # Create UI
        self.create_widgets()
        
        # Check if PowerShell is available
        print("Checking if PowerShell is available...")
        ps_available = self.is_powershell_available()
        print(f"PowerShell available: {ps_available}")
        if not ps_available:
            print("PowerShell is not available on this system. This tool requires PowerShell to run.")
            messagebox.showerror("Error", "PowerShell is not available on this system. This tool requires PowerShell to run.")
            self.root.destroy()
            return

                
    def is_powershell_available(self):
        """Check if PowerShell is available on the system"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Write-Output 'PowerShell Test'"],
                capture_output=True,
                text=True,
                timeout=10, # Increased timeout for robustness
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
            
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="10")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Scan Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(dir_frame, textvariable=self.directory_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).grid(row=0, column=2)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        self.scan_button = ttk.Button(button_frame, text="Scan for Files", command=self.scan_files)
        self.scan_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected Files", command=self.delete_files, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))

        self.select_all_button = ttk.Button(button_frame, text="Select All", command=self.select_all_files, state=tk.DISABLED)
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Treeview for files
        self.tree = ttk.Treeview(results_frame, columns=('Name', 'Path', 'Size', 'Modified'), show='headings')
        self.tree.heading('Name', text='File Name')
        self.tree.heading('Path', text='Path')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Last Modified')
        
        # Adjusted column widths
        self.tree.column('Name', width=200)  # Wider for file name
        self.tree.column('Path', width=250)  # Smaller but still readable
        self.tree.column('Size', width=75)   # Half of previous width
        self.tree.column('Modified', width=175)  # Wider for date/time
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory()
        if directory:
            self.directory_var.set(directory)
            
    def on_tree_select(self, event):
        """Handle tree selection changes"""
        selected_items = self.tree.selection()
        if selected_items:
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.delete_button.config(state=tk.DISABLED)

    def select_all_files(self):
        """Select all items in the treeview"""
        all_items = self.tree.get_children()
        if all_items:
            self.tree.selection_set(all_items)
            # The on_tree_select method will automatically enable the delete button
            
    def scan_files(self):
        """Scan for Visio temp files"""
        directory = self.directory_var.get().strip()
        if not directory:
            messagebox.showerror("Error", "Please specify a directory to scan.")
            return
            
        if not os.path.isdir(directory):
            messagebox.showerror("Error", f"The directory '{directory}' does not exist.")
            return
            
        # Start scanning in a separate thread to prevent UI freezing
        self.scan_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.select_all_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Scanning for Visio temp files...")
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Start scanning thread
        scan_thread = threading.Thread(target=self._scan_files_thread, args=(directory,))
        scan_thread.daemon = True
        scan_thread.start()
        
    def _scan_files_thread(self, directory):
        """Thread function to scan for files"""
        try:
            # Escape directory path for PowerShell
            escaped_dir = directory.replace("'", "''")

            # Build PowerShell command
            ps_command = f"Get-ChildItem -Path '{escaped_dir}' -Recurse -File -Force -Include \"~$$*.*\" | Select-Object -Property FullName,Name,DirectoryName,@{Name=\"LastModified\";Expression={{\$_.LastWriteTime.ToString(\"yyyy-MM-dd HH:mm:ss\")}}},@{Name=\"Size\";Expression={{\$_.Length}}} | ConvertTo-Json"

            # Execute PowerShell command
            ps_cmd_list = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", ps_command
            ]

            print(f"Executing PowerShell command: {ps_command}")

            result = subprocess.run(
                ps_cmd_list,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60,  # 60 second timeout
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            print(f"PowerShell return code: {result.returncode}")
            print(f"PowerShell stdout: {result.stdout}")
            print(f"PowerShell stderr: {result.stderr}")

            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error scanning files: {error_msg}"))
                return
                
            if not result.stdout or result.stdout.strip() == "":
                self.root.after(0, self._scan_complete, [])
                return
                
            # Parse JSON results
            try:
                files_data = json.loads(result.stdout.strip())
                # Handle both single object and array cases
                if isinstance(files_data, dict):
                    files_data = [files_data]
                elif not isinstance(files_data, list):
                    files_data = []
                self.root.after(0, self._scan_complete, files_data)
            except json.JSONDecodeError as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error parsing scan results: {str(e)}"))
                print(f"JSON parsing error: {e}")
                print(f"Raw output: {result.stdout}")
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: messagebox.showerror("Error", "Scan timed out after 60 seconds."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Unexpected error during scan: {str(e)}"))
        finally:
            self.root.after(0, self._scan_finished)
            
    def _scan_complete(self, files_data):
        """Called when scan is complete"""
        self.found_files = files_data if isinstance(files_data, list) else []
        
        if not self.found_files:
            self.status_var.set("No matching Visio temp files found.")
            messagebox.showinfo("Scan Complete", "No matching Visio temp files were found.")
            self.select_all_button.config(state=tk.DISABLED)
            return

        # Enable select all button when files are found
        self.select_all_button.config(state=tk.NORMAL)
            
        # Populate treeview
        for file_info in self.found_files:
            try:
                size = file_info.get('Size', 0)
                size_str = self.format_file_size(size) if size else "Unknown"
                
                # Get full path and relative path for display
                full_path = file_info.get('FullName', 'Unknown')
                scan_directory = self.directory_var.get().strip()
                
                # Calculate relative path for display
                if full_path != 'Unknown' and scan_directory:
                    try:
                        # Normalize paths for comparison
                        import os
                        full_path_norm = os.path.normpath(full_path)
                        scan_dir_norm = os.path.normpath(scan_directory)
                        
                        # Get relative path
                        if full_path_norm.startswith(scan_dir_norm):
                            relative_path = os.path.relpath(full_path_norm, scan_dir_norm)
                            # Get the directory part only (exclude filename)
                            relative_dir = os.path.dirname(relative_path)
                            # If it's in the root of scan directory, show "."
                            path_display = relative_dir if relative_dir else "."
                        else:
                            # Fallback to full path if not under scan directory
                            path_display = full_path
                    except Exception:
                        # Fallback to full path if there's any error
                        path_display = full_path
                else:
                    path_display = full_path
                
                # Insert item with full path as tags so we can retrieve it later for deletion
                item_id = self.tree.insert('', tk.END, values=(
                    file_info.get('Name', 'Unknown'),
                    path_display,
                    size_str,
                    file_info.get('LastModified', 'Unknown')
                ), tags=(full_path,))  # Store full path in tags
            except Exception as e:
                print(f"Error inserting file into tree: {e}")
                
        self.status_var.set(f"Found {len(self.found_files)} Visio temp files.")
        messagebox.showinfo("Scan Complete", f"Found {len(self.found_files)} Visio temp files.")
        
    def _scan_finished(self):
        """Called when scan thread finishes"""
        self.scan_button.config(state=tk.NORMAL)
        self.progress.stop()
        # Re-enable select all button if files were found
        if self.found_files:
            self.select_all_button.config(state=tk.NORMAL)
        
    def delete_files(self):
        """Delete selected files"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select files to delete.")
            return
            
        # Get selected file paths (full paths from tags)
        selected_paths = []
        for item in selected_items:
            # Get full path from tags instead of displayed path
            tags = self.tree.item(item, 'tags')
            if tags and len(tags) > 0:
                selected_paths.append(tags[0])  # Full path is stored in first tag
            else:
                # Fallback to displayed path if tags not available
                values = self.tree.item(item, 'values')
                if values and len(values) > 1:
                    selected_paths.append(values[1])  # Path is in the second column
                
        if not selected_paths:
            messagebox.showinfo("Info", "No valid files selected for deletion.")
            return
            
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_paths)} selected file(s)?\n\nThis action cannot be undone."
        )
        
        if not result:
            return
            
        # Start deletion in a separate thread
        self.scan_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.select_all_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Deleting selected files...")
        
        delete_thread = threading.Thread(target=self._delete_files_thread, args=(selected_paths,))
        delete_thread.daemon = True
        delete_thread.start()
        
    def _delete_files_thread(self, file_paths):
        """Thread function to delete files using direct PowerShell approach"""
        try:
            deleted_count = 0
            failed_count = 0
            
            # Perform safety checks in Python before deleting
            safe_to_delete = []
            for path in file_paths:
                # 1. Check if file exists
                if not os.path.exists(path) or not os.path.isfile(path):
                    failed_count += 1
                    print(f"File not found or is not a regular file: {path}")
                    continue

                # 2. Check if file is in a system directory
                is_protected_location = False
                invalid_paths = [
                    os.environ.get("windir", ""),
                    os.path.join(os.environ.get("windir", ""), "System32"),
                    os.path.join(os.environ.get("windir", ""), "System"),
                    os.environ.get("ProgramFiles", ""),
                    os.environ.get("ProgramFiles(x86)", ""),
                    os.environ.get("ProgramData", ""),
                ]
                for protected_path in invalid_paths:
                    if protected_path and os.path.normpath(path).startswith(os.path.normpath(protected_path)):
                        is_protected_location = True
                        break
                
                if is_protected_location:
                    failed_count += 1
                    print(f"Cannot delete file in system directory: {path}")
                    continue

                # 3. Check if file matches Visio temporary file pattern
                if not os.path.basename(path).startswith("~$$"):
                    failed_count += 1
                    print(f"File does not match Visio temporary file pattern: {path}")
                    continue
                
                safe_to_delete.append(path)

            if not safe_to_delete:
                self.root.after(0, self._delete_complete, deleted_count, failed_count)
                return

            # Use direct approach like web version
            print("Using direct PowerShell approach for deletion...")
            file_list_string = [f"'{path.replace("'", "''")}'" for path in safe_to_delete]
            file_list_joined = ",".join(file_list_string)
            
            direct_ps_command = f"@({file_list_joined}) | ForEach-Object {{ Remove-Item -Path $_ -Force -ErrorAction SilentlyContinue }}"
            
            direct_ps_cmd_list = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", direct_ps_command
            ]
            
            print(f"Executing direct PowerShell delete command: {direct_ps_command}")
            
            direct_result = subprocess.run(
                direct_ps_cmd_list,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            print(f"Direct PowerShell delete return code: {direct_result.returncode}")
            print(f"Direct PowerShell delete stdout: {direct_result.stdout}")
            print(f"Direct PowerShell delete stderr: {direct_result.stderr}")
            
            # For direct approach, we assume success if no errors
            if direct_result.returncode == 0:
                deleted_count = len(safe_to_delete)
            else:
                # If there are errors, we can't be sure which files failed.
                # We can try to check which files still exist.
                still_exist = [path for path in safe_to_delete if os.path.exists(path)]
                deleted_count = len(safe_to_delete) - len(still_exist)
                failed_count += len(still_exist)
                
            self.root.after(0, self._delete_complete, deleted_count, failed_count)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Unexpected error during deletion: {str(e)}"))
            print(f"Unexpected error: {e}")
        finally:
            self.root.after(0, self._delete_finished)
            
    def _delete_complete(self, deleted_count, failed_count):
        """Called when deletion is complete"""
        message = f"Deletion complete:\n- {deleted_count} files deleted successfully\n- {failed_count} files failed to delete"
        self.status_var.set(f"Deleted {deleted_count} files, {failed_count} failed.")
        messagebox.showinfo("Deletion Complete", message)
        
        # Refresh the file list
        self.scan_files()
        
    def _delete_finished(self):
        """Called when deletion thread finishes"""
        self.scan_button.config(state=tk.NORMAL)
        self.progress.stop()
        # Re-enable select all button if files are still available
        if self.found_files:
            self.select_all_button.config(state=tk.NORMAL)
        
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

def main():
    root = tk.Tk()
    app = VisioTempFileRemoverGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()