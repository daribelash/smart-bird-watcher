import torch
import torch.nn as nn
from torchvision import models
from typing import List, Tuple

class BirdClassifier:
  """
  Loads EfficientNet-B2 model and does prediction for bird species classification
  Attributes:
    device (torch.device): Computation device
    model (torch.nn.Module): EfficientNet-B2 model with custom classification head
    class_names (List[str]): List of bird species names
  """
  def __init__(self, model_path: str, class_names: List[str]) -> None:
    """
    Initializes the BirdClassifier
    Args:
      model_path (str): Path to the trained model
      class_names (List[str]): List of class label names
    """
    self.device = torch.device("mps" if torch.cuda.is_available() else "cpu")
    self.model = models.efficientnet_b2(weights=None)
    # replaces the final classifier layer with a custom layer sized to match the number of bird classes 
    self.model.classifier[1] = nn.Linear(
      self.model.classifier[1].in_features, len(class_names)
    )
    # loads saved model parameters
    self.model.load_state_dict(torch.load(model_path, map_location=self.device))
    self.model.to(self.device)
    self.model.eval()
    self.class_names = class_names    # store class labels

  def predict(self, input_tensor) -> Tuple[str, float]:
    """
    Forward pass to predict the bird species
    Args:
      input_tensor (torch.Tensor): A preprocessed image tensor of shape 1, 3, H, W
    Returns:
      Tuple[str, float]: Predicted species name with its confidence score
    """
    with torch.inference_mode():
      outputs = self.model(input_tensor.to(self.device))
      probs = torch.softmax(outputs, dim=1)   # apply softmax to get class probs 
      confidence, predicted_idx = torch.max(probs, dim=1)   # taking the highest prob
      return self.class_names[predicted_idx.item()], confidence.item()