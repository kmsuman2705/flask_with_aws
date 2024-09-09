from flask import Flask, render_template, Response, request
import cv2

app = Flask(__name__)

# Function to initialize camera based on user selection
def init_camera(source, camera_url=None):
    if source == "Local Camera (Webcam)":
        return cv2.VideoCapture(0)
    elif source == "External Camera (IP Camera)" and camera_url:
        return cv2.VideoCapture(camera_url)
    else:
        return None

# Function to capture frames from the camera
def get_frame(camera):
    success, frame = camera.read()
    if not success:
        return None
    # Convert the frame to JPEG for streaming
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes() if ret else None

@app.route('/')
def index():
    # Render the HTML form to select the camera source
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Get the camera source and IP camera URL from the request arguments
    source = request.args.get('camera_source', 'Local Camera (Webcam)')
    camera_url = request.args.get('camera_url', '')

    # Initialize the camera
    camera = init_camera(source, camera_url)
    if not camera:
        return "Camera could not be initialized."

    def generate():
        while True:
            frame = get_frame(camera)
            if frame is None:
                break
            # Return frame as a multipart response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True, ssl_context=('cert.pem', 'key.pem'))

