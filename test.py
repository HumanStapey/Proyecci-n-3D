from PIL import Image, ImageSequence

# Open the GIF image
with Image.open('gifs/bici.gif') as img:
    # Iterate through each frame of the GIF
    for frame in ImageSequence.Iterator(img):
        # Display the frame
        frame.show()
        # Add a pause if you want to see the frame before it changes
        input("Press Enter to continue to the next frame...")