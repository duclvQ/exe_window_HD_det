import cv2 
import numpy as np

def orange_color_identifier(img, threshold=10):
    """
    This function takes an image as input and returns True if the image contains a significant amount of orange color,
    and False otherwise. The threshold parameter is used to determine the minimum percentage of orange pixels required
    to return True. The default threshold is 10%.
    (adjust the lower and upper bounds for the orange color to match the specific shade of orange in the image.)
    """


    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the orange color
    lower_orange = np.array([0, 30, 30])
    upper_orange = np.array([30, 255, 255])

    # Create a mask that selects only the orange pixels
    mask = cv2.inRange(hsv_image, lower_orange, upper_orange)
    #cv2.imshow("mask", mask)
    #cv2.waitKey(0)
    # Count the number of orange pixels
    orange_pixels = np.sum(mask > 0)

    # Calculate the percentage of orange pixels
    total_pixels = img.shape[0] * img.shape[1]
    percentage_orange = (orange_pixels / total_pixels) * 100
    #print("percentage_orange", percentage_orange)   
    #print("percentage_orange", percentage_orange)
    if percentage_orange < threshold:
        return False
    else:
        return True