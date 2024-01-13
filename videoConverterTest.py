import numpy as np
import math
import cv2
def convertVideo(input_path, output_path, signal, threadobj):
    input_video_path = input_path
    output_video_path = output_path
    video = cv2.VideoCapture(input_video_path)

    video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    elevation_range = 108  # -54 to 54 degrees
    azimuth_range = 328   # -164 to 164 degrees

    azimuth_range_pixels = video_width * (azimuth_range / 360)
    elevation_range_pixels = video_height * (elevation_range / 180)

    x1 = int((video_width - azimuth_range_pixels) / 2)
    y1 = int((video_height - elevation_range_pixels) / 2)
    x2 = x1 + int(azimuth_range_pixels)
    y2 = y1 + int(elevation_range_pixels)

    resized_width = 2880  # Replace with your desired width

    flag = True
    frame_cnt = 0
    while threadobj._is_running:
        progress_ratio = int(frame_cnt/total_frames*100)
        signal.emit(progress_ratio)
        frame_cnt += 1
        #read image
        ret, image = video.read()
        if not ret: break  # Break the loop when the video ends

        #crop image
        cropped_image = image[y1:y2, x1:x2]
        cropped_height, cropped_width = cropped_image.shape[:2]

        #resize image
        ratio = resized_width / float(cropped_width)
        resized_height = int(cropped_height * ratio)
        resized_image = cv2.resize(cropped_image, (resized_width, resized_height))

        #project image
        #what if projected_width is bigger than projected_width/2?
        projected_width = resized_width
        projected_height = int(projected_width/2)

        if(flag == True):
            #get equirectangular_elevation_matrix
            equirectangular_elevation_matrix = np.linspace(elevation_range/2, -1*elevation_range/2, resized_height)
            equirectangular_elevation_matrix = equirectangular_elevation_matrix.transpose()

            #get cylinderical_elevation_matrix
            cylinderical_elevation_matrix = np.arange(int(projected_height/2), int(-1*projected_height/2), -1.0)
            #maybe not radius?
            radius = projected_height/2 / math.tan(math.pi/180 * elevation_range/2)
            for i in range(cylinderical_elevation_matrix.shape[0]):
                cylinderical_elevation_matrix[i] =  180/math.pi * math.atan(cylinderical_elevation_matrix[i] / radius)

            #get projection_pixel_matrix
            projection_pixel_matrix = np.zeros(projected_height)
            projection_pixel_matrix = projection_pixel_matrix.transpose()

            for i in range(projection_pixel_matrix.shape[0]-1,-1,-1):
                elevation_val = cylinderical_elevation_matrix[i]

                for j in range(equirectangular_elevation_matrix.shape[0]-1,0,-1):

                    upper_val = equirectangular_elevation_matrix[j-1]
                    lower_val = equirectangular_elevation_matrix[j]
                    
                    if(upper_val > elevation_val):
                        if(abs(upper_val - elevation_val) < abs(lower_val - elevation_val)):
                            projection_pixel_matrix[i] = j-1
                            break
                        else:
                            projection_pixel_matrix[i] = j
                            break

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec as needed
            output_video = cv2.VideoWriter(output_video_path, fourcc, video_fps, (projected_height, projected_width))

            flag = False

        #get black image with projected size
        projected_image = np.zeros((projected_height, projected_width, 3), dtype=np.uint8)

        
        for y_cyl in range(projected_height):
            projected_image[y_cyl] = resized_image[int(projection_pixel_matrix[y_cyl])]

        #rotate image
        rotated_image = cv2.rotate(projected_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        output_video.write(rotated_image)
        
        
        

        

    video.release()
    output_video.release()

