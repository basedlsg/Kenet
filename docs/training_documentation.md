# Training Documentation

This document outlines the steps taken to get the `train_mobilenet.py` script working and to train the model.

## Initial Problem

The initial execution of the `prototypes/train_mobilenet.py` script failed due to a `NameError`, indicating that the `labels` variable was not defined.

## Resolution

The following steps were taken to resolve the issue and successfully train the model:

1.  **Defined `labels` variable**: The `labels` variable was defined in `prototypes/train_mobilenet.py` to provide the correct labels for the dummy dataset.

2.  **Created Dummy Data**: Three dummy images (`image1.jpg`, `image2.jpg`, and `image3.jpg`) were created in the `prototypes` directory to be used as training data.

3.  **Created `requirements.txt`**: A `requirements.txt` file was created to list the project's dependencies:
    ```
    torchvision
    pillow
    ```

4.  **Installed Dependencies**: The dependencies listed in `requirements.txt` were installed using `pip`.

5.  **Fixed File Paths**: The `prototypes/train_mobilenet.py` script was modified to include the correct file paths to the dummy images, resolving a `FileNotFoundError`.

6.  **Enabled Training Progress Logging**: The training loop in `prototypes/train_mobilenet.py` was updated to print the loss at each step, providing visibility into the training progress.

7.  **Trained the Model**: The model was successfully trained for 10 epochs. The final loss for the last step of the last epoch was 0.4588.

The prototype is now ready for further development and experimentation.