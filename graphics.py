import tkinter as tk
import utilFunc

def generateVideo(chan: str, numClips: int, daysBack: int):

    targetChannel = chan
    numberOfClips = numClips
    clipTimeFrame = daysBack

    APP_ID = 'appid'
    APP_SECRET = 'appsecret'
    
    clipInfo = utilFunc.fetchClips(targetChannel, numberOfClips, clipTimeFrame, APP_ID, APP_SECRET)
    utilFunc.downloadClips(numberOfClips, clipInfo)
    utilFunc.resizeClips(clipInfo, 'safe')
    utilFunc.combineClips(targetChannel, clipInfo)




def screen():

    def run_function():
        # Function to be executed when the button is clicked
        streamer_name = streamer_entry.get()
        num_clips = int(clips_entry.get())
        days_back = int(days_entry.get())

        generateVideo(streamer_name, num_clips, days_back)

    # Create the main tkinter window
    window = tk.Tk()
    window.geometry("400x300")  # Width x Height
    window.title("Twitch Clipper")

    # Create the streamer name label and text entry box
    streamer_label = tk.Label(window, text="Streamer name:")
    streamer_label.pack()
    streamer_entry = tk.Entry(window)
    streamer_entry.pack()

    # Create the number of clips label and text entry box
    clips_label = tk.Label(window, text="Number of clips:")
    clips_label.pack()
    clips_entry = tk.Entry(window)
    clips_entry.pack()

    # Create the number of days label and text entry box
    days_label = tk.Label(window, text="How many days back?")
    days_label.pack()
    days_entry = tk.Entry(window)
    days_entry.pack()

    # Create the button to run the function
    run_button = tk.Button(window, text="Run", command=run_function)
    run_button.pack()

    # Start the tkinter event loop
    window.mainloop()
