from tkinter import *
import telebot
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
import PIL # type: ignore
import tensorflow as tf # type: ignore
from tensorflow import keras # type: ignore
from tensorflow.keras import layers # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
import pathlib
from translate import Translator

TOKEN = '7133130711:AAFTYEgGn9xcEIi2F9ZbTnc0bQFXKWGTE5E'
bot = telebot.TeleBot(TOKEN)

translator = Translator(from_lang="en", to_lang="ru")


dataset_dir = pathlib.Path("food-101")
batch_size = 32
img_width = 180
img_height = 180
train_ds = tf.keras.utils.image_dataset_from_directory(
	dataset_dir,
	validation_split=0.2,
	subset="training",
	seed=123,
	image_size=(img_height, img_width),
	batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
	dataset_dir,
	validation_split=0.2,
	subset="validation",
	seed=123,
	image_size=(img_height, img_width),
	batch_size=batch_size)

class_names = train_ds.class_names
print(f"Class names: {class_names}")


num_classes = len(class_names)
model = Sequential([
	tf.keras.layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),

	tf.keras.layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
	tf.keras.layers.RandomRotation(0.1),
	tf.keras.layers.RandomZoom(0.1),
	tf.keras.layers.RandomContrast(0.2),

	layers.Conv2D(16, 3, padding='same', activation='relu'),
	layers.MaxPooling2D(),

	layers.Conv2D(32, 3, padding='same', activation='relu'),
	layers.MaxPooling2D(),

	layers.Conv2D(64, 3, padding='same', activation='relu'),
	layers.MaxPooling2D(),

	layers.Dropout(0.2),

	layers.Flatten(),
	layers.Dense(128, activation='relu'),
	layers.Dense(num_classes)
])

model.compile(
    optimizer='adam',
 	loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy'])

model.load_weights("Foood.weights.h5")

loss, acc = model.evaluate(train_ds, verbose=2)
print("Restored model, accuracy: {:5.2f}%".format(100 * acc))

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = 'photo.jpg'
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, 'фото схранено')
    img = tf.keras.utils.load_img( "photo.jpg", target_size=(img_height, img_width))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    lol =("The image most likely {}".format(
    str(class_names[np.argmax(score)])))
    end_text =translator.translate(lol)
    bot.send_message(message.chat.id, text=end_text)

bot.polling()