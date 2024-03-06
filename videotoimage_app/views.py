import base64
from rest_framework.decorators import api_view
import os
import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications import VGG16
from PIL import Image
from keras.models import load_model

model = load_model('vgg16_model.h5')
# Define your class labels here
class_labels = ['aom', 'csom', 'earwax', 'normal']  # Modify with your actual class labels

# Function to preprocess an image using PIL
def preprocess_image_pil(image):
    image = image.resize((224, 224))  # Resize image to match VGG16 input size
    image = img_to_array(image)  # Convert image to numpy array
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    image = preprocess_input(image)  # Preprocess image
    return image

# Function to preprocess an image using OpenCV
def preprocess_image_cv(image):
    image = cv2.resize(image, (224, 224))  # Resize image to match VGG16 input size
    image = img_to_array(image)  # Convert image to numpy array
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    image = preprocess_input(image)  # Preprocess image
    return image

# Function to convert video to images
def video_to_images(video_path, output_folder, num_images=30, skip_seconds=2, top_crop=0, bottom_crop=0):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Get total number of frames and frame rate
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Calculate the number of frames to skip
    skip_frames = skip_seconds * frame_rate
    
    # Calculate the frame index to start and end capturing
    start_frame = skip_frames
    end_frame = total_frames - skip_frames
    
    # Calculate the step size to evenly distribute the frames
    step = (end_frame - start_frame) // num_images
    
    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    count = 0
    frame_index = start_frame
    
    # Loop through the frames and save selected frames as images
    while count < num_images:
        # Set the frame index
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        # Read the frame
        success, image = cap.read()
        
        # Check if frame reading was successful
        if not success:
            break
        
        # Apply top and bottom cropping
        if top_crop > 0 or bottom_crop > 0:
            height, width = image.shape[:2]
            image = image[top_crop:height-bottom_crop, :]
        
        # Save the frame as an image directly in the output folder
        image_path = os.path.join(output_folder, f"frame_{count}.jpg")
        cv2.imwrite(image_path, image)
        
        # Increment the frame index
        frame_index += step
        
        count += 1
    
    # Release the video capture object
    cap.release()
    print(f"Conversion completed. {count} frames saved in '{output_folder}'.")

# Function to add text overlay on image
def add_text_overlay(image, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (50, 50)
    font_scale = 1
    color = (255, 255, 255)
    thickness = 2
    image_with_text = cv2.putText(image, text, org, font, font_scale, color, thickness, cv2.LINE_AA)
    return image_with_text

@api_view(['POST'])
@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        # Handle video file upload
        video_file = request.FILES['video']
        video_path = './media/videos/photos.mp4'  # Save the video temporarily
        with open(video_path, 'wb') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
        
        # Convert video to images
        output_folder = './media/photos'
        video_to_images(video_path, output_folder, num_images=30, skip_seconds=2, top_crop=50, bottom_crop=50)
        
        # Predict labels for the extracted images
        class_counters = {label: 0 for label in class_labels}
        image_with_highest_accuracy = None
        max_accuracy = 0
        
        for filename in os.listdir(output_folder):
            if filename.endswith('.jpg'):
                image_path = os.path.join(output_folder, filename)
                image = cv2.imread(image_path)
                preprocessed_image = preprocess_image_cv(image)
                predictions = model.predict(preprocessed_image)
                predicted_class_index = np.argmax(predictions)
                predicted_class_label = class_labels[predicted_class_index]
                predicted_accuracy = predictions[0][predicted_class_index]
                class_counters[predicted_class_label] += 1
                if predicted_accuracy > max_accuracy:
                    max_accuracy = predicted_accuracy
                    image_with_highest_accuracy = image.copy()
                    best_prediction = predicted_class_label
         # Check if any label count exceeds 20
        if any(count > 22 for count in class_counters.values()):
            response_data = {
                'status': 'error',
                'message': 'Label count exceeds 22. Video processing stopped.'
            }
            return JsonResponse(response_data, status=400)
        # Get the final prediction and image with overlay
        final_prediction = max(class_counters, key=class_counters.get)
        print(final_prediction)
        image_with_overlay = add_text_overlay(image_with_highest_accuracy, f"Predicted Class: {best_prediction}\nAccuracy: {max_accuracy}")
        
        # Encode the image in base64
        _, buffer = cv2.imencode('.jpg', image_with_overlay)
        image_data = base64.b64encode(buffer).decode('utf-8')
        
        # Save the image with the highest accuracy
        cv2.imwrite('best_image.jpg', image_with_overlay)
        
        # Provide additional information in the response
        response_data = {
            'status': 'true',
            'message': 'Video processing completed.',
            'best_image': image_data,
            'best_prediction': final_prediction,
            'best_accuracy': float(max_accuracy)
        }
        
        return JsonResponse(response_data, status=200)
    
    else:
        response_data = {
            'status': 'false',
            'message': 'Video processing failed.',
            'best_image': None,
            'best_prediction': None,
            'best_accuracy': None
        } 
        return JsonResponse(response_data, status=500)
