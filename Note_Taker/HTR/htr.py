from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import cv2

model = VisionEncoderDecoderModel.from_pretrained('HTR\\model')
# model.to_bettertransformer
processor = TrOCRProcessor.from_pretrained('HTR\\processor')

def preprocess_image(image):
    if image is None:
        print("Error: Unable to load image. Please check the file path.")
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        dilate = cv2.dilate(binary, kernel, iterations=5)
        return dilate
    
def ocr_image(image):
    pixel_values = processor(images=image, return_tensors='pt').pixel_values
    generated_ids = model.generate(pixel_values)
    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

def inference(image):
    ROI = []
    cnts = cv2.findContours(preprocess_image(image), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w > 25 and h > 25:
            #cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)
            ROI.append(image[y:y+h, x:x+w])
    text = ''
    for roi in ROI:
        index = text.find('.')
        print(index)
        if index != -1:
            text = text[:index:]
        text += ocr_image(roi)
        text += ' '
    return text
