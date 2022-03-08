"""This code follows the tutorial on # https://keras.io/examples/vision/image_classification_with_vision_transformer."""
from __future__ import absolute_import, print_function

import argparse
import os
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow import keras
from tensorflow.keras import Sequential, layers
from tensorflow.keras.callbacks import History


def main(args: argparse.Namespace):
    """Run VIT Image Classification.

    Args:
        args (argparse.Namespace): input arguments.
    """
    (x_train, y_train), (x_test, y_test) = keras.datasets.cifar100.load_data()

    print(f"x_train shape: {x_train.shape}  - y_train shape: {y_train.shape}")
    print(f"x_test shape: {x_test.shape}  - y_test shape: {y_test.shape}")

    # Hyperparameters
    num_classes = 100
    input_shape = (32, 32, 3)
    learning_rate = 0.001
    weight_decay = 0.0001
    batch_size = 256
    num_epochs = 100
    image_size = 72
    patch_size = 6
    num_patches = (image_size // patch_size) ** 2
    projection_dim = 64
    num_heads = 4
    transformer_units = [projection_dim * 2, projection_dim]
    transformer_layers = 8
    mlp_head_units = [2048, 1024]

    # Data Augmentation
    data_augmentation = Sequential(
        [
            layers.Normalization(),
            layers.Resizing(image_size, image_size),
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(factor=0.02),
            layers.RandomZoom(height_factor=0.2, width_factor=0.2),
        ],
        name="data_augmentation",
    )

    data_augmentation.layers[0].adapt(x_train)

    plot_patches(x_train, image_size, patch_size, args.image_dir)

    vit_classifier = create_vit_classifier(
        input_shape,
        patch_size,
        num_patches,
        projection_dim,
        transformer_layers,
        num_heads,
        transformer_units,
        mlp_head_units,
        num_classes,
        data_augmentation,
    )

    model_plot = os.path.join(args.image_dir, "./vit_classifier.png")

    keras.utils.plot_model(
        vit_classifier,
        to_file=model_plot,
        show_shapes=False,
        show_dtype=False,
        show_layer_names=True,
        rankdir="TB",
        expand_nested=False,
        dpi=96,
        layer_range=None,
        show_layer_activations=False,
    )

    _ = run_experiment(
        vit_classifier,
        learning_rate,
        weight_decay,
        x_train,
        y_train,
        batch_size,
        num_epochs,
        x_test,
        y_test,
        args.model_dir,
    )


def create_vit_classifier(
    input_shape: Tuple,
    patch_size: int,
    num_patches: int,
    projection_dim: int,
    transformer_layers: int,
    num_heads: int,
    transformer_units: List,
    mlp_head_units: List,
    num_classes: int,
    data_augmentation: keras.Model,
) -> keras.Model:
    """Create VIT Classifier.

    Args:
        input_shape (Tuple): inpute image shape.
        patch_size (int): patch size.
        num_patches (int): number of patches.
        projection_dim (int): projection dimension.
        transformer_layers (int): transformer layers.
        num_heads (int): number of attention heads.
        transformer_units (List): transformer units.
        mlp_head_units (List): MLP head units.
        num_classes (int): number of classes.
        data_augmentation (keras.Model): data augmentation.

    Returns:
        keras.Model: VIT model.
    """
    inputs = layers.Input(shape=input_shape)
    augmented = data_augmentation(inputs)
    patches = Patches(patch_size)(augmented)
    encoded_patches = PatchEncoder(num_patches, projection_dim)(patches)

    for _ in range(transformer_layers):
        x1 = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
        attention_output = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=projection_dim, dropout=0.1
        )(x1, x1)
        x2 = layers.Add()([attention_output, encoded_patches])
        x3 = layers.LayerNormalization(epsilon=1e-6)(x2)
        x3 = mlp(x3, hidden_units=transformer_units, dropout_rate=0.1)
        encoded_patches = layers.Add()([x3, x2])

    representation = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
    representation = layers.Flatten()(representation)
    representation = layers.Dropout(0.5)(representation)

    features = mlp(representation, hidden_units=mlp_head_units, dropout_rate=0.5)

    logits = layers.Dense(num_classes)(features)
    model = keras.Model(inputs=inputs, outputs=logits)
    return model


def run_experiment(
    model: keras.Model,
    learning_rate: float,
    weight_decay: float,
    x_train: np.array,
    y_train: np.array,
    batch_size: int,
    num_epochs: int,
    x_test: np.array,
    y_test: np.array,
    output_dir: str,
) -> History:
    """Run Training and Validation.

    Args:
        model (keras.Model): classifier model.
        learning_rate (float): learning rate.
        weight_decay (float): weight decay.
        x_train (np.array): training input.
        y_train (np.array): training output.
        batch_size (int): batch size.
        num_epochs (int): number of epochs.
        x_test (np.array): test input.
        y_test (np.array): test output.
        output_dir (str): directory to write model.

    Returns:
        History: training history.
    """
    optimizer = tfa.optimizers.AdamW(
        learning_rate=learning_rate, weight_decay=weight_decay
    )

    model.compile(
        optimizer=optimizer,
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[
            keras.metrics.SparseCategoricalAccuracy(name="accuracy"),
            keras.metrics.SparseTopKCategoricalAccuracy(5, name="top-5-accuracy"),
        ],
    )

    os.makedirs(output_dir, exist_ok=True)

    checkpoint_filepath = os.path.join(output_dir, "checkpoint")
    _ = keras.callbacks.ModelCheckpoint(
        checkpoint_filepath,
        monitor="val_accuracy",
        save_best_only=True,
        save_weights_only=True,
    )

    history = model.fit(
        x=x_train,
        y=y_train,
        batch_size=batch_size,
        epochs=num_epochs,
        validation_split=0.1,
        callbacks=[],
    )

    # model.load_weights(checkpoint_filepath)
    _, accuracy, top_5_accuracy = model.evaluate(x_test, y_test)
    print(f"Test accuracy: {round(accuracy * 100, 2)}%")
    print(f"Test top 5 accuracy: {round(top_5_accuracy * 100, 2)}%")

    return history


def plot_patches(x_train: np.array, image_size: int, patch_size: int, output_dir: str):
    """Plot Image Patches.

    Args:
        x_train (np.array): Training set as numpy array.
        image_size (int): image size.
        patch_size (int): patch size.
        output_dir (str): directory to write images.
    """
    fig = plt.figure(figsize=(4, 4))
    image = x_train[np.random.choice(range(x_train.shape[0]))]
    plt.imshow(image.astype("uint8"))
    plt.axis("off")

    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(os.path.join(output_dir, "./vit_classification_image.jpeg"))

    resized_image = tf.image.resize(
        tf.convert_to_tensor([image]), size=(image_size, image_size)
    )
    patches = Patches(patch_size)(resized_image)
    print(f"Image size: {image_size} X {image_size}")
    print(f"Patch size: {patch_size} X {patch_size}")
    print(f"Patches per image: {patches.shape[1]}")
    print(f"Elements per patch: {patches.shape[-1]}")

    n = int(np.sqrt(patches.shape[1]))
    fig = plt.figure(figsize=(4, 4))
    for i, patch in enumerate(patches[0]):
        _ = plt.subplot(n, n, i + 1)
        patch_img = tf.reshape(patch, (patch_size, patch_size, 3))
        plt.imshow(patch_img.numpy().astype("uint8"))
        plt.axis("off")

    fig.savefig(os.path.join(output_dir, "./vit_classification_patches.jpeg"))


def mlp(x: layers, hidden_units: int, dropout_rate: float) -> layers:
    """Multi Layer Perceptron.

    Args:
        x (layers): input layer.
        hidden_units (int): number of hidden units.
        dropout_rate (float): dropout rate.

    Returns:
        layers: output layer.
    """
    for units in hidden_units:
        x = layers.Dense(units, activation=tf.nn.gelu)(x)
        x = layers.Dropout(dropout_rate)(x)
    return x


class Patches(layers.Layer):
    """Image Patches."""

    def __init__(self, patch_size: int):
        """Initialize Class.

        Args:
            patch_size (int): patch size.
        """
        super(Patches, self).__init__()
        self.patch_size = patch_size

    def call(self, images: np.array) -> tf.Tensor:
        """Extrach Patches.

        Args:
            images (np.array): input images.

        Returns:
            tf.Tensor: image patches.
        """
        batch_size = tf.shape(images)[0]
        patches = tf.image.extract_patches(
            images=images,
            sizes=[1, self.patch_size, self.patch_size, 1],
            strides=[1, self.patch_size, self.patch_size, 1],
            rates=[1, 1, 1, 1],
            padding="VALID",
        )
        patch_dims = patches.shape[-1]
        # Flatten patches
        patches = tf.reshape(patches, [batch_size, -1, patch_dims])
        return patches


class PatchEncoder(layers.Layer):
    """Encode Patches."""

    def __init__(self, num_patches: int, projection_dim: int):
        """Initialize Class.

        Args:
            num_patches (int): number of patches.
            projection_dim (int): projection dimension.
        """
        super(PatchEncoder, self).__init__()
        self.num_patches = num_patches
        # Trainable Linear Projection, (Eq.1)
        self.projection = layers.Dense(units=projection_dim)

        # Position Embeddings
        self.position_embedding = layers.Embedding(
            input_dim=num_patches, output_dim=projection_dim
        )

    def call(self, patch: tf.Tensor) -> layers:
        """Encode Patches.

        Args:
            patch (tf.Tensor): input image tensor.

        Returns:
            layers: encoded tensor.
        """
        positions = tf.range(start=0, limit=self.num_patches, delta=1)
        encoded = self.projection(patch) + self.position_embedding(positions)
        return encoded


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default="./images")
    parser.add_argument("--model_dir", default="./models")
    main(parser.parse_args())
