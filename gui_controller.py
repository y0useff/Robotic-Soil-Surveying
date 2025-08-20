import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import json
import os
from typing import Optional

class MotorControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor Control Interface")
        self.root.geometry("450x600")
        
        # Base URL for endpoints - modify this to match your server
        self.base_url = "http://192.168.1.200"  # Change this to your actual server URL
        
        # Connection status tracking
        self.is_connected = False
        self.ping_interval = 5000  # Start with 5 seconds
        self.after_id = None
        
        # Motor state tracking
        self.motor_active = False
        
        # Store references to buttons for enabling/disabling
        self.motor_buttons = []
        self.data_button = None
        
        # Initialize status variables
        self.connection_status_var = None
        self.connection_label = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Motor Control Section
        motor_frame = ttk.LabelFrame(main_frame, text="Motor Control", padding="10")
        motor_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Motor control buttons - larger and hold-to-operate
        extend_btn = tk.Button(motor_frame, text="EXTEND MOTOR", 
                              font=('Arial', 12, 'bold'), height=3, width=20, state='disabled',
                              bg='lightgreen', activebackground='green')
        extend_btn.grid(row=0, column=0, padx=(0, 10), pady=10)
        extend_btn.bind('<Button-1>', self.extend_motor_press)
        extend_btn.bind('<ButtonRelease-1>', self.motor_release)
        extend_btn.bind('<Leave>', self.motor_release)
        extend_btn.bind_all('<KeyRelease-Escape>', self.emergency_stop)
        self.motor_buttons.append(extend_btn)
        
        retract_btn = tk.Button(motor_frame, text="RETRACT MOTOR", 
                               font=('Arial', 12, 'bold'), height=3, width=20, state='disabled',
                               bg='lightcoral', activebackground='red')
        retract_btn.grid(row=0, column=1, padx=(10, 0), pady=10)
        retract_btn.bind('<Button-1>', self.retract_motor_press)
        retract_btn.bind('<ButtonRelease-1>', self.motor_release)
        retract_btn.bind('<Leave>', self.motor_release)
        self.motor_buttons.append(retract_btn)
        
        # Data Collection Section
        data_frame = ttk.LabelFrame(main_frame, text="Data Collection", padding="10")
        data_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Plot number input
        ttk.Label(data_frame, text="Plot Number:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.plot_number_var = tk.StringVar()
        plot_entry = ttk.Entry(data_frame, textvariable=self.plot_number_var, width=20)
        plot_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Sample type input
        ttk.Label(data_frame, text="Sample Type:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.sample_type_var = tk.StringVar()
        sample_entry = ttk.Entry(data_frame, textvariable=self.sample_type_var, width=20)
        sample_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Gather data button - make it larger and more prominent
        self.gather_data_btn = tk.Button(data_frame, text="GATHER DATA", 
                                        command=self.gather_data, font=('Arial', 11, 'bold'),
                                        height=2, width=25, state='disabled',
                                        bg='lightblue', activebackground='blue', relief='raised')
        self.gather_data_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        self.data_button = self.gather_data_btn
        
        # Progress bar for data gathering
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(data_frame, textvariable=self.progress_var).grid(row=3, column=0, columnspan=2, pady=(5, 0))
        
        self.progress_bar = ttk.Progressbar(data_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Connection status indicator
        connection_frame = ttk.Frame(main_frame)
        connection_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(connection_frame, text="Connection Status:").grid(row=0, column=0, sticky=tk.W)
        self.connection_status_var = tk.StringVar(value="Not Ready - Checking connection...")
        self.connection_label = ttk.Label(connection_frame, textvariable=self.connection_status_var, 
                                         foreground="red")
        self.connection_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Status text area
        self.status_text = tk.Text(status_frame, height=8, width=45, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=1)
        data_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(0, weight=1)
        
        self.log_status("Motor Control GUI initialized")
        
        # Create samples directory if it doesn't exist
        self.samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        if not os.path.exists(self.samples_dir):
            os.makedirs(self.samples_dir)
            self.log_status(f"Created samples directory: {self.samples_dir}")
        
        # Start connection monitoring
        self.start_connection_monitoring()
    
    def start_connection_monitoring(self):
        """Start the connection monitoring system"""
        self.ping_server()
    
    def ping_server(self):
        """Ping the server to check connection status"""
        try:
            # Cancel any existing scheduled ping
            if self.after_id:
                self.root.after_cancel(self.after_id)
            
            # Use a lightweight HEAD request instead of GET to avoid server load
            response = requests.head(self.base_url, timeout=5)
            if response.status_code in [200, 404, 405]:  # Server is responding
                self.handle_connection_success()
            else:
                self.handle_connection_failure(f"Server responded with status: {response.status_code}")
        except Exception as e:
            self.handle_connection_failure(str(e))
    
    def handle_connection_success(self):
        """Handle successful server connection"""
        if not self.is_connected:
            self.is_connected = True
            if self.connection_status_var:
                self.connection_status_var.set("Ready - Connected to server")
            if self.connection_label:
                self.connection_label.config(foreground="green")
            self.enable_buttons()
            self.log_status("Server connection established")
            self.ping_interval = 100000  # Switch to 100 seconds to reduce server load
        
        # Schedule next ping
        self.after_id = self.root.after(self.ping_interval, self.ping_server)
    
    def handle_connection_failure(self, error_msg):
        """Handle server connection failure"""
        if self.is_connected:
            self.is_connected = False
            if self.connection_status_var:
                self.connection_status_var.set("Not Ready - Server unreachable")
            if self.connection_label:
                self.connection_label.config(foreground="red")
            self.disable_buttons()
            self.log_status(f"Server connection lost: {error_msg}")
        else:
            if self.connection_status_var:
                self.connection_status_var.set("Not Ready - Server unreachable")
            if self.connection_label:
                self.connection_label.config(foreground="red")
        
        self.ping_interval = 5000  # Back to 5 seconds when disconnected
        
        # Schedule next ping
        self.after_id = self.root.after(self.ping_interval, self.ping_server)
    
    def enable_buttons(self):
        """Enable all control buttons"""
        for button in self.motor_buttons:
            button.config(state='normal')
        if self.data_button:
            self.data_button.config(state='normal')
    
    def disable_buttons(self):
        """Disable all control buttons"""
        for button in self.motor_buttons:
            button.config(state='disabled')
        if self.data_button:
            self.data_button.config(state='disabled')
    
    def check_connection_before_action(self):
        """Check if connection is available before performing actions"""
        if not self.is_connected:
            messagebox.showerror("Connection Error", "Server is not ready. Please wait for connection to be established.")
            return False
        return True
    
    def log_status(self, message: str):
        """Add a message to the status log"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def send_request_async(self, endpoint: str, description: str):
        """Send a GET request asynchronously to avoid GUI blocking"""
        def make_request():
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=2)  # Shorter timeout for motor commands
                
                if response.status_code == 200:
                    self.root.after(0, lambda: self.log_status(f"{description} successful"))
                else:
                    self.root.after(0, lambda: self.log_status(f"{description} failed - Status: {response.status_code}"))
                    
            except requests.exceptions.Timeout:
                self.root.after(0, lambda: self.log_status(f"{description} timed out"))
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.log_status(f"{description} connection error"))
            except Exception as e:
                self.root.after(0, lambda: self.log_status(f"{description} error: {str(e)}"))
        
        # Run request in background thread
        thread = threading.Thread(target=make_request)
        thread.daemon = True
        thread.start()
    
    def send_request(self, endpoint: str, description: str) -> Optional[requests.Response]:
        """Send a GET request to the specified endpoint (for data gathering only)"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.log_status(f"Sending {description} request to {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                self.log_status(f"{description} successful - Status: {response.status_code}")
                return response
            else:
                self.log_status(f"{description} failed - Status: {response.status_code}")
                messagebox.showerror("Request Failed", f"{description} failed with status: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            self.log_status(f"{description} request timed out")
            messagebox.showerror("Timeout", f"{description} request timed out")
            return None
        except requests.exceptions.ConnectionError:
            self.log_status(f"Connection error for {description}")
            messagebox.showerror("Connection Error", f"Could not connect to server for {description}")
            return None
        except Exception as e:
            self.log_status(f"Error during {description}: {str(e)}")
            messagebox.showerror("Error", f"Error during {description}: {str(e)}")
            return None
    
    def extend_motor_press(self, event):
        """Handle extend motor button press"""
        if self.check_connection_before_action() and not self.motor_active:
            self.motor_active = True
            self.send_request_async("/ON8", "Extend Motor (Hold)")
            event.widget.config(relief='sunken')  # Visual feedback
    
    def retract_motor_press(self, event):
        """Handle retract motor button press"""
        if self.check_connection_before_action() and not self.motor_active:
            self.motor_active = True
            self.send_request_async("/OFF8", "Retract Motor (Hold)")
            event.widget.config(relief='sunken')  # Visual feedback
    
    def motor_release(self, event):
        """Handle motor button release or mouse leave"""
        if self.motor_active:
            self.motor_active = False
            event.widget.config(relief='raised')  # Reset visual feedback
            if self.is_connected:
                self.send_request_async("/stop", "Motor Brake (Auto)")
    
    def emergency_stop(self, event):
        """Emergency stop on Escape key"""
        if self.motor_active:
            self.motor_active = False
            if self.is_connected:
                self.send_request_async("/stop", "Emergency Stop")
            self.log_status("EMERGENCY STOP activated")
    
    def extend_motor(self):
        """Legacy method - no longer used"""
        pass
    
    def retract_motor(self):
        """Legacy method - no longer used"""
        pass
    
    def brake_motor(self):
        """Send brake motor command"""
        if self.check_connection_before_action():
            self.send_request("/stop", "Brake Motor")
    
    def gather_data(self):
        """Gather data with user inputs - now fully async to prevent lag"""
        if not self.check_connection_before_action():
            return
            
        # Validate inputs
        plot_number = self.plot_number_var.get().strip()
        sample_type = self.sample_type_var.get().strip()
        
        if not plot_number:
            messagebox.showerror("Input Error", "Please enter a plot number")
            return
        
        if not sample_type:
            messagebox.showerror("Input Error", "Please enter a sample type")
            return
        
        try:
            plot_num = int(plot_number)
        except ValueError:
            messagebox.showerror("Input Error", "Plot number must be a valid integer")
            return
        
        # Immediately start UI feedback and launch async thread
        self.start_data_gathering()
        
        # Start data gathering in a separate thread
        thread = threading.Thread(target=self.gather_data_thread, args=(plot_num, sample_type))
        thread.daemon = True
        thread.start()
    
    def gather_data_thread(self, plot_number: int, sample_type: str):
        """Thread function for gathering data - with better error recovery"""
        try:
            self.root.after(0, lambda: self.log_status(f"Starting data collection for Plot {plot_number}, Sample Type: {sample_type}"))
            
            # Make a simple GET request to gather_data endpoint
            url = f"{self.base_url}/gather_data"
            
            self.root.after(0, lambda: self.log_status(f"Sending data request to {url}"))
            
            response = requests.get(url, timeout=110)  # 110 second timeout for ~90s data gathering
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.root.after(0, lambda: self.handle_data_success(data, plot_number, sample_type))
                except json.JSONDecodeError:
                    self.root.after(0, lambda: self.handle_data_error("Received invalid JSON response"))
            else:
                self.root.after(0, lambda: self.handle_data_error(f"Request failed with status: {response.status_code}"))
                
        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.handle_data_error("Data gathering timed out after 110 seconds"))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.handle_data_error("Could not connect to server - it may have crashed"))
            # Trigger immediate connection recheck
            self.root.after(1000, self.ping_server)
        except Exception as e:
            self.root.after(0, lambda: self.handle_data_error(f"Error during data gathering: {str(e)}"))
    
    def start_data_gathering(self):
        """Start the data gathering UI state"""
        self.gather_data_btn.config(state='disabled', text='Gathering Data...')
        self.progress_var.set("Gathering data... Please wait (up to 110 seconds)")
        self.progress_bar.start(10)
    
    def handle_data_success(self, data, plot_number: int, sample_type: str):
        """Handle successful data gathering"""
        self.stop_data_gathering()
        self.log_status(f"Data collection successful for Plot {plot_number}")
        
        # Save data to JSON file
        filename = f"{sample_type}-{plot_number}.json"
        filepath = os.path.join(self.samples_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            self.log_status(f"Data saved to: {filepath}")
            messagebox.showinfo("Success", f"Data gathered successfully for Plot {plot_number}, Sample Type: {sample_type}\n\nSaved to: {filename}")
        except Exception as e:
            self.log_status(f"Error saving data: {str(e)}")
            messagebox.showerror("Save Error", f"Data collected but failed to save: {str(e)}")
            
        self.log_status(f"Received data preview: {json.dumps(data, indent=2)[:200]}...")
    
    def handle_data_error(self, error_message: str):
        """Handle data gathering error"""
        self.stop_data_gathering()
        self.log_status(f"Data gathering error: {error_message}")
        messagebox.showerror("Data Gathering Error", error_message)
    
    def stop_data_gathering(self):
        """Stop the data gathering UI state"""
        self.gather_data_btn.config(state='normal', text='Gather Data')
        self.progress_var.set("Ready")
        self.progress_bar.stop()

def main():
    root = tk.Tk()
    app = MotorControlGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()