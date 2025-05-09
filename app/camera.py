import cv2
import numpy as np

class Camera:
  """
  Webcam interface for capturing video frames using OpenCV
  """
  def __init__(self, camera_index:int=0):
    """
    Initializes the camera
    Args:
      camera_index (int): Index of the camera to use, default is 0
    Raises:
      RuntimeError: If the camera cannot be opened
    """
    self.cap = cv2.VideoCapture(camera_index)
    if not self.cap.isOpened():
      raise RuntimeError("Cannot open webcam")
    for _ in range(5):
      self.cap.read() # next 5 reads for 'warm up'

  def get_frame(self) -> np.ndarray:
    """
    Captures a single frame from the webcam
    Returns:
      np.ndarray: The captured frame as a NumPy array
    Raises:
      RuntimeError: If frame capture fails
    """
    ret, frame = self.cap.read()
    if not ret:
      raise RuntimeError("Cannot read frame from webcam")
    return frame

  def release(self) -> None:
    """
    Deallocated webcam resources
    """
    self.cap.release()


if __name__ == "__main__":
  cam = Camera()
  try:
    while True:
      frame = cam.get_frame()
      cv2.imshow("live", frame)

      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  finally:
    cam.release()
    cv2.destroyAllWindows()
