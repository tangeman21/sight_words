import tkinter as tk
from tkinter import messagebox, PhotoImage
import random
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
# List of common sight words for beginners
sight_words = [
    "the", "and", "a", "to", "of", "in", "that",
    "have", "I", "it", "for", "not", "on", "with",
    "he", "as", "you", "do", "at", "this", "but",
    "his", "by", "from", "or", "one", "had", "they"
]

# Initialize text-to-speech engine
engine = pyttsx3.init()

class SightWordGame:
    def __init__(self, root):
        self.root = root
        self.score = 0
        self.total_questions = 10  # Number of questions in the game
        self.word_to_guess = None
        self.buttons = []
        self.image_dict = {}

        for word in sight_words:
            try:
                image_path = f"images/{word}.png"
                img = Image.open(image_path)
                img.thumbnail((50, 50))  # Resize the image to a smaller size
                photo = ImageTk.PhotoImage(img)
                self.image_dict[word] = photo
            except FileNotFoundError:
                print(f"No image found for '{word}'. Skipping.")

        self.next_question()

    def check_answer(self, selected_word):
        if selected_word.lower() == self.word_to_guess:
            print("Correct!")
            self.score += 1
            messagebox.showinfo("Result", "Correct!")
        else:
            print(f"Incorrect. The correct word was '{self.word_to_guess}'.")
            messagebox.showerror("Result", f"Incorrect. The correct word was '{self.word_to_guess}'.")

        self.next_question()

    def replay_word(self):
        if self.word_to_guess:
            # Use kokoro to generate and play the sound
            text = f"The word to click is {self.word_to_guess}"
            generator = pipeline(text, voice='af_heart')
            for i, (gs, ps, audio) in enumerate(generator):
                # Play the sound directly without saving to disk
                sd.play(audio, 24000)
                break

    def next_question(self):
        if self.total_questions > 0:
            self.word_to_guess = random.choice(sight_words)
            # Use kokoro to generate and play the sound
            text = f"The word to click is {self.word_to_guess}"
            generator = pipeline(text, voice='af_heart')
            for i, (gs, ps, audio) in enumerate(generator):
                # Play the sound directly without saving to disk
                sd.play(audio, 24000)
                break
            self.total_questions -= 1

            # Shuffle the words and create new buttons for each round
            shuffled_words = random.sample(sight_words + [self.word_to_guess], 4)  # Only 4 options

            for button in self.buttons:
                button.destroy()
            self.buttons = []

            for i, word in enumerate(shuffled_words):
                frame = tk.Frame(self.root)
                frame.grid(row=(i // 2), column=(i % 2))

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

                # Replay button
                replay_button = tk.Button(
                    frame,
                    text="Replay",
                    width=6,
                    height=1,
                    command=self.replay_word
                )
                replay_button.pack()

                self.buttons.append(button)

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
    root.title("Sight Word Game")
    game = SightWordGame(root)
    root.mainloop()
