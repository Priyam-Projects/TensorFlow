# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-v7JdCokZliEIkkNlSNi-jqcEITBP1o1

IMPORTING STUFFS
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator

"""DOWNLOADING DOGS VS CATS DATASET"""

URL_DS  = 'https://storage.googleapis.com/mledu-datasets/cats_and_dogs_filtered.zip'
zip_dir = tf.keras.utils.get_file('cats_and_dogs.zip',origin=URL_DS,extract=True) # returns the extracted zip
ds_dir = os.path.dirname(zip_dir) # stores the directory adress of the extracted folder

"""CATS AND DOGS : 

---


      1. TRAIN : 
                A. cats : contains several photos of cats
                B. dogs : contains several photos of dogs
      2. VALIDATION
                A. cats : contains several photos of cats
                B. dogs : contains several photos of dogs

"""

base_dir = os.path.join(ds_dir,'cats_and_dogs_filtered')

train_dir = os.path.join(base_dir,'train') 
val_dir = os.path.join(base_dir,'validation')

train_cats_dir = os.path.join(train_dir,'cats')
train_dogs_dir = os.path.join(train_dir,'dogs')

val_cats_dir = os.path.join(val_dir,'cats')
val_dogs_dir = os.path.join(val_dir,'dogs')

"""CALCULATING NUMBER OF CATS AND DOGS IMAGES PRESENT IN THE DATASET"""

num_train_cats = len(os.listdir(train_cats_dir))
num_train_dogs = len(os.listdir(train_dogs_dir))

num_val_cats = len(os.listdir(val_cats_dir))
num_val_dogs = len(os.listdir(val_dogs_dir))

num_train = num_train_cats+num_train_dogs
num_val = num_val_cats+num_val_dogs

"""DECLARING GLOBAL VARIABLE FOR LATER USE"""

BATCH_SIZE = 100 #it means that our model will predict this many trainee examples and then calculate error to update the parameters
IMG_SHAPE = 224

"""FUNCTION TO DISPLAY IMAGES USING PLOT"""

def PlotImages(Images_arr) :
  
  fig,axes = plt.subplot(1,5,figsize=(15,15)) # it will just print the first 5 images of the given array 
  axes = axes.flatten() #these are the indices of the subplots

  for img,ax in zip(Images_arr,axes):
    ax.imshow(img) #each subplot assigning a image to display
  
  plt.tight_layout()
  plt.show() #finally we displayed to the user

"""GENERATING THE DATASET USING IMAGE DATA SET GENERATOR

GETTING DATASET INTO CACHE MEMORY
"""

# ----------------------- GETTING TRAINING DATASET AND PERFORMING IMAGE AUGMENTATION ---------------------------------------------- #

img_gen = ImageDataGenerator(
      rescale=1./255,
      rotation_range=40,
      width_shift_range=0.2,
      height_shift_range=0.2,
      shear_range=0.2,
      zoom_range=0.2,
      horizontal_flip=True,
      fill_mode='nearest')

#so an object of Image Data Generator is created.

#so we have added many method of augmentation into this, and hence a better training data now.

train_dataset = img_gen.flow_from_directory(
                                            batch_size = BATCH_SIZE,
                                            directory = train_dir,
                                            shuffle = True,
                                            target_size = (IMG_SHAPE,IMG_SHAPE),
                                            class_mode = 'binary'
                                           )


# ----------------------- GETTING VALIDATION DATASET  ---------------------------------------------------------------------------- #

img_gen2 = ImageDataGenerator(
      rescale = 1./255 )

# Image augmentation not required for validation data set

val_dataset = img_gen2.flow_from_directory(
                                            batch_size=BATCH_SIZE,
                                            directory = val_dir,
                                            target_size = (IMG_SHAPE,IMG_SHAPE),
                                            class_mode = 'binary'
                                          )

"""A. SIMPLE CNN

1. Defining the struture of the Network
"""

# defining the structure of the network

model = tf.keras.models.Sequential([
                                  
                tf.keras.layers.Conv2D(32,(3,3),activation='relu',input_shape=(150,150,3)),
                tf.keras.layers.MaxPooling2D(2,2),

                tf.keras.layers.Conv2D(64,(3,3),activation='relu'),
                tf.keras.layers.MaxPooling2D(2,2),

                tf.keras.layers.Conv2D(128,(3,3),activation='relu'),
                tf.keras.layers.MaxPooling2D(2,2),

                tf.keras.layers.Conv2D(128,(3,3),activation='relu'),
                tf.keras.layers.MaxPooling2D(2,2),

                tf.keras.layers.Dropout(0.15),
                tf.keras.layers.Flatten(),
                
                tf.keras.layers.Dense(512,activation='relu'),
                tf.keras.layers.Dense(2,activation='softmax')
               ])

"""2.Compiling the model"""

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)

# ------------------------------------ CREATING CALLBACKS ------------------------------------------------#

es_callback = tf.keras.callbacks.EarlyStopping(patience=100) 
model_checkpoint = tf.keras.callbacks.ModelCheckpoint('best_model.h5')

"""3. Training the model"""

history = model.fit_generator(
    train_dataset,
    steps_per_epoch = int(np.ceil(num_train/ float(BATCH_SIZE))),
    epochs = 500 ,
    validation_data = val_dataset,
    validation_steps = int(np.ceil(num_val/ float(BATCH_SIZE))),
    callbacks = [es_callback,model_checkpoint]
)

#model = tf.keras.load_model('best_model.h5')

"""B. TRANSFER LEARNING : BEST ACCURACY

IMPORTING REQUIRED MODULES
"""

import tensorflow_hub as hub
import tensorflow_datasets as tfds
# ----- Below code supresses the log messages produced by tensorflow -------- #
import logging
logger = tf.get_logger()
logger.setLevel(logging.ERROR)

"""We would be donwloading the already trained model for image classification without its final layer"""

# --- We are using MobileNet tf model which was already trained on ImageNet data-set ---- #
# --- We would then train it on our required data-set , in this case, dogs vs cats dataset --- #

url_mobileNet = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/2" 

# As mobileNet is trained on ds having image resolution as 224*224*3, we need to provide the same dimension for the input

IMG_SHAPE = 224

# This url would return the model excluding the final class probability one 
# Therefore, this would just extract all the features from the given image by using proper/trained filters in Conv Layer

feature_extracter = hub.KerasLayer(url_mobileNet,trainable=False,input_shape=(IMG_SHAPE,IMG_SHAPE,3))

"""Now add the final classification layer to the model which would be trained on our own data-sets """

model = tf.keras.Sequential([
            feature_extracter,
            tf.keras.layers.Dense(2,activation='softmax')
])

model.summary()

"""Compile Model"""

model.compile(
    optimizer = 'adam',
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True) ,
    metrics = ['accuracy']
)

es_callback = tf.keras.callbacks.EarlyStopping(patience=50) 
#model_checkpoint_TL = tf.keras.callbacks.ModelCheckpoint('best_model_TL.h5') this has some issues with tf hub latest version.

"""Training our transfer learning model"""

history = model.fit_generator(
    train_dataset,
    steps_per_epoch = int(np.ceil(num_train/ float(BATCH_SIZE))),
    epochs = 10,
    validation_data = val_dataset,
    validation_steps = int(np.ceil(num_val/ float(BATCH_SIZE))),
    callbacks = [es_callback] 
)

"""GRAPH : TRAINING ACCURACY/LOSS VS VALIDATION ACCURACY/LOSS : USE TO DETERMINE THE OVER/UNDER FITTING ISSUES"""

train_accuracy = history.history['accuracy'] 
val_accuracy = history.history['val_accuracy']

train_loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(10) 

plt.figure(figsize=(8,8))

plt.subplot(1,2,1) 
plt.plot(epochs_range,train_accuracy,label='Train_Acc') 
plt.plot(epochs_range,val_accuracy,label='Val_Acc')
plt.legend()
plt.title('Accuracy vs Epochs')

plt.subplot(1,2,2)
plt.plot(epochs_range,train_loss,label='Train_Loss')
plt.plot(epochs_range,val_loss,label='Val_Loss')
plt.legend()
plt.title('Loss vs Epochs')

"""PREDICTION USING THE TRAINED MODEL"""

from PIL import Image
import requests
from io import BytesIO

url_dog_eg = 'https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg'

response = requests.get(url_dog_eg)
img = Image.open(BytesIO(response.content))

img = img.resize( (IMG_SHAPE,IMG_SHAPE) )
img = np.array(img)/255.0

plt.imshow(img)

# model always expect a batch of image to be processed at a time.
# Hence, we need to add a new dimension to our image to make it compatible
# The new dimension is just use to fake the batch dimension

result = model.predict(img[np.newaxis,...])

# # result is an array of array. The outer array contains inner array as result for each image of the batch

# # as we have predicted only a single image , result[0] array will be our required result for that image

result = np.argmax(result[0],axis=-1)

if(result==1):
  plt.title("PREDICTION : DOG")
else:
  plt.title("PREDICTION : CAT")

# --- This concludes our CNN architecture for Image Classification --- #