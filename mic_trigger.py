import os
import subprocess
import speech_recognition as sr

def record_and_transcribe():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Listening... (press Ctrl+C to stop)")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Transcribing...")
        text = recognizer.recognize_google(audio)
        print(f"Question: {text}")
        # Call app.py with the transcribed text as question
        subprocess.run(["python", "app.py", "--question", text])
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")

if __name__ == "__main__":
    while True:
        try:
            record_and_transcribe()
        except KeyboardInterrupt:
            print("Stopping mic listener.")
            break
