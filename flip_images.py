from PIL import Image
import os


def flip_image(image_path, saved_location):
    """
    Flip or mirror the image

    @param image_path: The path to the image to edit
    @param saved_location: Path to save the cropped image
    """
    image_obj = Image.open(image_path)
    rotated_image = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
    rotated_image.save(saved_location)

if __name__ == "__main__":
    file_list = os.listdir("D:\Projects\clueless\images\players")
    for file in file_list:
        location = "D:\Projects\clueless\images\players\\" + file
        sprites_list = os.listdir(location)

        if "00.png" in sprites_list:
            print("Skipping file: ", location)
            continue

        for i in range(0, 4):
            os.rename(location + "\\" + sprites_list[i], location + "\\0" + str(i) + ".png")

        for i in range(4, len(sprites_list)):
            if i >= 6:
                flip_image(location + "\\" + sprites_list[i], location + "\\" + str(i + 4) + ".png")
            else:
                flip_image(location + "\\" + sprites_list[i], location + "\\0" + str(i + 4) + ".png")
            if i < 10:
                os.rename(location + "\\" + sprites_list[i], location + "\\0" + str(i) + ".png")
            else:
                os.rename(location + "\\" + sprites_list[i], location + "\\" + str(i) + ".png")
