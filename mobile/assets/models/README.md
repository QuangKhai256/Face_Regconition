# MobileFaceNet TFLite Model

## Required Model File

This directory should contain the MobileFaceNet TFLite model file:
- **Filename**: `mobilefacenet.tflite`
- **Size**: ~4MB
- **Input**: 112x112 RGB image
- **Output**: 128-dimensional embedding vector

## How to Obtain the Model

### Option 1: Download Pre-trained Model
You can download a pre-trained MobileFaceNet TFLite model from:
- https://github.com/sirius-ai/MobileFaceNet_TF
- https://github.com/deepinsight/insightface (convert to TFLite)

### Option 2: Convert from PyTorch/TensorFlow
If you have a PyTorch or TensorFlow model, convert it to TFLite format:

```python
import tensorflow as tf

# Load your model
model = tf.keras.models.load_model('mobilefacenet.h5')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model
with open('mobilefacenet.tflite', 'wb') as f:
    f.write(tflite_model)
```

### Option 3: Use a Pre-converted Model
Search for "MobileFaceNet TFLite" on GitHub or model repositories.

## Model Specifications

- **Architecture**: MobileFaceNet
- **Input Shape**: [1, 112, 112, 3]
- **Input Type**: float32
- **Input Normalization**: [0, 1] or [-1, 1] (check model documentation)
- **Output Shape**: [1, 128]
- **Output Type**: float32
- **Post-processing**: L2 normalization recommended

## Placement

Once you have the model file, place it in this directory:
```
mobile/assets/models/mobilefacenet.tflite
```

The app will automatically load it from this location.
