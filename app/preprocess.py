import torchvision.transforms as transforms
from PIL import Image
import cv2

def preprocess_frame(frame):
  """
  Preprocesses an OpenCV frame for model inference
  Args:
   frame (np.ndarray): Image frame from OpenCV
  Returns:
    torch.Tensor: Preprocessed image tensor of shape [1, 3, 224, 224]
  """
  image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
  pil_image = Image.fromarray(image)
  transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                          std=[0.229, 0.224, 0.225])
  ])
  return transform(pil_image).unsqueeze(0)