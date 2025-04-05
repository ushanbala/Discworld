import ollama
import json
import customtkinter as ctk
from tkinter import messagebox

class God:
    def __init__(self):
        """
        Initializes the God class for creating, saving, and managing models in Ollama.
        """
        print("Welcome to the heaven. Let's create some humans")
        self.models_log = "models_log.json"
        self.initialize_log()

    def initialize_log(self):
        """
        Initializes the JSON log file if it does not already exist.
        """
        try:
            with open(self.models_log, "x") as log_file:
                json.dump({}, log_file)
        except FileExistsError:
            pass

    def log_model(self, model_name, system_behavior):
        """
        Logs the model name and its behavior to a JSON file.

        Args:
            model_name (str): The name of the model.
            system_behavior (str): The behavior of the model.
        """
        try:
            with open(self.models_log, "r") as log_file:
                data = json.load(log_file)

            data[model_name] = system_behavior

            with open(self.models_log, "w") as log_file:
                json.dump(data, log_file, indent=4)

            print(f"Human '{model_name}' logged successfully.")
        except Exception as e:
            print(f"Error while logging the Human: {e}")

    def create_model(self, model_name, system_behavior):
        """
        Creates a model with the specified behavior and saves it.
        
        Args:
            model_name (str): The name of the model to create.
            system_behavior (str): The behavior to embed into the model.
        """
        modelfile = f"""
        FROM llama3
        SYSTEM {system_behavior}
        """
        try:
            ollama.create(model=model_name, modelfile=modelfile)
            print(f"Human '{model_name}' created successfully with specified behavior.")
            self.log_model(model_name, system_behavior)
            return True
        except ollama.ResponseError as e:
            print(f"Error while creating the Human: {e.error}")
            return False


class GodGUI(ctk.CTk):
    def __init__(self, god_instance):
        """
        Initializes the GUI for creating models.

        Args:
            god_instance (God): Instance of the God class that manages the models.
        """
        super().__init__()
        self.god_instance = god_instance
        self.title("Model Creation - Heaven")
        self.geometry("600x500")

        # Set up the widgets
        self.create_widgets()

    def create_widgets(self):
        """
        Creates all the widgets for the GUI.
        """
        self.model_name_label = ctk.CTkLabel(self, text="Enter Model Name:")
        self.model_name_label.pack(pady=10)

        self.model_name_entry = ctk.CTkEntry(self, placeholder_text="Human Model Name")
        self.model_name_entry.pack(pady=10)

        self.behavior_label = ctk.CTkLabel(self, text="Enter System Behavior:")
        self.behavior_label.pack(pady=10)

        # Textbox for behavior input
        self.behavior_textbox = ctk.CTkTextbox(self, width=400, height=150)
        self.behavior_textbox.pack(pady=10)

        self.create_button = ctk.CTkButton(self, text="Create Model", command=self.create_model)
        self.create_button.pack(pady=20)

    def create_model(self):
        """
        Calls the God instance to create the model and handles the feedback.
        """
        model_name = self.model_name_entry.get()
        behavior = self.behavior_textbox.get("1.0", "end-1c")  # Get the content from the textbox

        if model_name and behavior:
            success = self.god_instance.create_model(model_name, behavior)
            if success:
                messagebox.showinfo("Success", f"Model '{model_name}' created successfully!")
            else:
                messagebox.showerror("Error", "An error occurred while creating the model.")
        else:
            messagebox.showwarning("Input Error", "Please provide both model name and behavior.")


if __name__ == "__main__":
    # Initialize the backend logic
    god_instance = God()

    # Initialize the GUI
    gui = GodGUI(god_instance)
    gui.mainloop()
