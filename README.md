## How to Run This App 

1. **Open your terminal or command prompt.**

2. **Go to the folder where you put this project.**
   - Example (Linux/Mac):
     ```bash
     cd ~/Documents/MD-Kivy
     ```
   - Example (Windows):
     ```cmd
     cd C:\Users\YourName\Documents\MD-Kivy
     ```

3. **Activate the virtual environment.**
   - If you see a folder called `vislab_env` here, use:
     - Linux/Mac:
       ```bash
       source vislab_env/bin/activate
       ```
     - Windows:
       ```cmd
       vislab_env\Scripts\activate
       ```
   - If you don't have a virtual environment yet, create one:
     - Linux/Mac:
       ```bash
       python3 -m venv vislab_env
       source vislab_env/bin/activate
       ```
     - Windows:
       ```cmd
       python -m venv vislab_env
       vislab_env\Scripts\activate
       ```

4. **Install the requirements if missing (only the first time):**
   ```bash
   pip install kivy kivymd kivy-garden.graph pyserial psutil
   ```

5. **Run the app!**
   ```bash
   python main.py
   ```

6. **Important: If you want to use Arduino:**
   - For USB: Edit and run `run_wired.sh` (Linux/Mac) or `run_wired.bat` (Windows)
   - For Wi-Fi: Edit and run `run_wireless.sh` (Linux/Mac) or `run_wireless.bat` (Windows)
