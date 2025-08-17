import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping

# Paths
train_dir = "E:/vproject/processed_datasets/train"
val_dir = "E:/vproject/processed_datasets/validation"

# Image Preprocessing (Data Augmentation for Better Generalization)
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode="nearest"
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(train_dir, target_size=(224, 224), batch_size=32, class_mode="categorical")
val_generator = val_datagen.flow_from_directory(val_dir, target_size=(224, 224), batch_size=32, class_mode="categorical")

# Load Pretrained ResNet50 Model
base_model = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))

# Unfreeze ONLY the Last 5 Layers for Fine-Tuning
for layer in base_model.layers[:-5]:
    layer.trainable = False

# Build Model
x = Flatten()(base_model.output)
x = Dense(256, activation="relu")(x)  # Reduced dense units
x = Dropout(0.5)(x)  # Increased dropout for regularization
x = Dense(5, activation="softmax")(x)  # 5 Classes: Vitamin A, B, C, D, E

model = Model(inputs=base_model.input, outputs=x)

# Compile Model with Lower Learning Rate
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
              loss="categorical_crossentropy", metrics=["accuracy"])

# Callbacks for Better Training
reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1, min_lr=1e-6)
early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1)

# Train Model with Callbacks
model.fit(train_generator, validation_data=val_generator, epochs=30, callbacks=[reduce_lr, early_stop])

# Save Model
model.save("vitamin_deficiency_resnet50_improved.keras")

print("✅ Model Training Complete! Saved as 'vitamin_deficiency_resnet50_improved.keras'")
