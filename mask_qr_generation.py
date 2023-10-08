import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import io

def create_image_with_text(qr_image_path, text_1, text_2):
    # Load the mask image and QR image
    mask_image = cv2.imread("FileBhejo_Mask.png")
    qr_image = cv2.imread(qr_image_path)

    # Ensure both images have the same dimensions
    qr_image = cv2.resize(qr_image, (370 * 2, 370 * 2))

    # Get the dimensions of the mask image
    height, width, _ = mask_image.shape

    # Calculate the position to place the QR image in the center
    x_pos = (width - qr_image.shape[1]) // 2
    y_pos = (height - qr_image.shape[0]) // 2

    # Place the QR image on the mask image
    mask_image[y_pos:y_pos + qr_image.shape[0], x_pos:x_pos + qr_image.shape[1]] = qr_image

    # Convert the mask image to a PIL Image for adding text
    mask_pil_image = Image.fromarray(cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(mask_pil_image)

    # Specify the font and font size
    font_size = 90
    font = ImageFont.truetype("arial.ttf", font_size)

    # Calculate the position to place Text_1 and Text_2 above the QR image
    text_1_width, text_1_height = draw.textlength(text_1, font=font), 90
    text_2_width, text_2_height = draw.textlength(text_2, font=font), 90

    text_1_x = (width - text_1_width) // 2
    text_2_x = (width - text_2_width) // 2
    text_y = y_pos - text_1_height - text_2_height - 10  # Adjust the vertical position as needed

    # Add Text_1 and Text_2 to the image
    draw.text((text_1_x, text_y), text_1, font=font, fill="#D06FBA")
    draw.text((text_2_x, text_y + text_1_height), text_2, font=font, fill=(0, 0, 0))

    # Convert the PIL Image back to an OpenCV image
    final_image = cv2.cvtColor(np.array(mask_pil_image), cv2.COLOR_RGB2BGR)

    # Save or return the final image
    cv2.imwrite(f"static/qr_poster/qr_image_{text_1}.png", final_image)
    return f"static/qr_poster/qr_image_{text_1}.png"

# Example usage of the function
qr_image_path = "static/qrcodes/7004969879_qr.png"
text_1 = "ABCD Printing Service"
text_2 = "F-ID: 7004969879"
resulting_image = create_image_with_text(qr_image_path, text_1, text_2)

# Display the final image (uncomment this line if you want to display the image)
# cv2.imshow("Final Image", resulting_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
