import tkinter as tk
from tkinter import messagebox, PhotoImage
import random
import json
import pyttsx3
from PIL import Image, ImageTk
from kokoro import KPipeline
import soundfile as sf
import sounddevice as sd
import torch

pipeline = KPipeline(lang_code='a')
text = '''
[Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient. With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.
'''
generator = pipeline(text, voice='af_heart')
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    sf.write(f'{i}.wav', audio, 24000)

# Initialize text-to-speech engine
engine = pyttsx3.init()

class SightWordGame:
    def __init__(self, root, template_file="templates/basic.json"):
        self.root = root
        self.score = 0
        self.total_questions = 10  # Number of questions in the game
        self.word_to_guess = None
        self.word_buttons = []
        self.image_dict = {}
        self.template = None
        self.background_image = None

        self.load_template(template_file)

        self.next_question()

    def load_template(self, template_file):
        """Load a game template from a JSON file."""
        try:
            with open(template_file, 'r') as f:
                self.template = json.load(f)

            # Set window title
            self.root.title(self.template.get("title", "Sight Word Game"))

            # Load background image if specified
            if "background_image" in self.template:
                try:
                    img = Image.open(self.template["background_image"])
                    img = ImageTk.PhotoImage(img)
                    self.background_image = img

                    # Create a label for the background image
                    bg_label = tk.Label(self.root, image=self.background_image)
                    bg_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                except FileNotFoundError:
                    print(f"Background image not found: {self.template['background_image']}")

            # Load word images
            if "images" in self.template:
                for word, image_path in self.template["images"].items():
                    try:
                        img = Image.open(image_path)
                        img.thumbnail((50, 50))  # Resize the image to a smaller size
                        photo = ImageTk.PhotoImage(img)
                        self.image_dict[word] = photo
                    except FileNotFoundError:
                        print(f"No image found for '{word}'. Skipping.")

        except Exception as e:
            print(f"Error loading template: {e}")
            # Use default settings if template fails to load

    def check_answer(self, selected_word):
        if selected_word.lower() == self.word_to_guess:
            print("Correct!")
            self.score += 1
            messagebox.showinfo("Result", "Correct!")

            # Perform any special action on correct answer
            if "on_correct" in self.template:
                action = self.template["on_correct"].get("action")
                if action == "replace_background" and "image" in self.template["on_correct"]:
                    try:
                        img = Image.open(self.template["on_correct"]["image"])
                        img = ImageTk.PhotoImage(img)
                        self.background_image = img

                        # Update the background image
                        for widget in self.root.winfo_children():
                            # Check if the widget is a Label with our background image
                            try:
                                is_background = isinstance(widget, tk.Label) and hasattr(widget, 'image') and widget.image is self.background_image
                            except (AttributeError, TypeError):
                                is_background = False

                            if is_background:
                                widget.configure(image=self.background_image)
                    except FileNotFoundError:
                        print(f"Correct answer image not found: {self.template['on_correct']['image']}")

        else:
            print(f"Incorrect. The correct word was '{self.word_to_guess}'.")
            messagebox.showerror("Result", f"Incorrect. The correct word was '{self.word_to_guess}'.")

        self.next_question()

    def replay_word(self):
        if self.word_to_guess:
            # Use kokoro to generate and play the sound
            text = f"The word to click is... \"{self.word_to_guess}\""
            generator = pipeline(text, voice='af_heart')
            for i, (gs, ps, audio) in enumerate(generator):
                # Play the sound directly without saving to disk
                sd.play(audio, 24000)
                break

    def next_question(self):
        if self.total_questions > 0:
            # Determine available words based on template
            available_words = list(self.image_dict.keys()) if "images" in self.template else sight_words

            if not available_words:
                print("No word images available.")
                return

            self.word_to_guess = random.choice(available_words)
            # Use kokoro to generate and play the sound
            text = f"The word to click is... \"{self.word_to_guess}\""
            generator = pipeline(text, voice='af_heart')
            for i, (gs, ps, audio) in enumerate(generator):
                # Play the sound directly without saving to disk
                sd.play(audio, 24000)
                break
            self.total_questions -= 1

            # Clear previous word buttons and other widgets except background image
            for widget in self.root.winfo_children():
                # Check if the widget is a Label with our background image
                try:
                    is_background = isinstance(widget, tk.Label) and hasattr(widget, 'image') and widget.image is self.background_image
                except (AttributeError, TypeError):
                    is_background = False

                if not is_background:
                    widget.destroy()
            self.word_buttons = []

            # Create new word buttons based on template positions
            if "word_positions" in self.template:
                words = [w for w in available_words if w != self.word_to_guess]
                words.append(self.word_to_guess)  # Add the correct word to the list
                random.shuffle(words)

                for i, position in enumerate(self.template["word_positions"]):
                    if i < len(words):  # Only create buttons for available positions
                        word = words[i]
                        frame = tk.Frame(self.root)
                        frame.place(relx=position["x"], rely=position["y"], anchor=tk.CENTER)

                        img_label = None
                        if word in self.image_dict:
                            img_label = tk.Label(frame, image=self.image_dict[word])
                            img_label.pack()

                        button = tk.Button(
                            frame,
                            text=word,
                            width=10,
                            height=2,
                            command=lambda w=word: self.check_answer(w)
                        )
                        button.pack()

                        self.word_buttons.append(button)

            # Create a replay button based on template position
            if "replay_button" in self.template:
                replay_position = self.template["replay_button"]
                replay_button = tk.Button(
                    self.root,
                    text="Replay",
                    width=6,
                    height=1,
                    command=self.replay_word
                )
                replay_button.place(relx=replay_position["x"], rely=replay_position["y"], anchor=tk.CENTER)
            else:
                # Fallback to grid if no position specified
                replay_frame = tk.Frame(self.root)
                replay_frame.grid(row=2, columnspan=2)
                replay_button = tk.Button(
                    replay_frame,
                    text="Replay",
                    width=6,
                    height=1,
                    command=self.replay_word
                )
                replay_button.pack()

        else:
            print("\nGame Over!")
            percentage = 0.0 if self.total_questions == 0 else (self.score/self.total_questions) * 100
            print(f"Your score is {self.score}/{self.total_questions} ({percentage:.2f}%).")
            messagebox.showinfo("Game Over", f"Your score is {self.score}/{self.total_questions} ({percentage}%).")
            self.root.quit()

# Start the game
if __name__ == "__main__":
    print("Welcome to the Sight Word Game!")
    root = tk.Tk()
    root.geometry("800x600")
    game = SightWordGame(root, template_file="templates/basic.json")
    root.mainloop()
