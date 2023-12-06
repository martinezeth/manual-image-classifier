# Manual Image Classifier

## Description
This script is a tool for manually classifying images into predefined categories. It connects to a remote server to fetch images, displays them to the user, and allows the user to classify these images into various categories based on visual inspection.

## Features
- Connects to a remote server using SSH
- Downloads and displays images for classification
- Supports categorizing images into user-defined categories
- Moves classified images on the server to corresponding directories within the server
- Copies classified images from server to a local directory structure

## Installation
1. Clone the repository:
```git clone https://github.com/martinezeth/manual-image-classifier.git```

2. Navigate to the project directory

## Conda Environment
You will need to run the following command to generate a Conda enviroment:
```conda create -n manual-classifier python=3 matplotlib pillow```
Then, activate your environment using the next command:
```conda activate manual-classifier```

## Configuration
Prior to first using this script, there are a few things that need to be configured.
1. Create a .ini file named ```config.ini``` within the project directory.
2. Copy and paste the contents of the [sample.config.ini](sample.config.ini) into your created ```config.ini``` file.
3. Make sure to put the server hostname, your SSH username and password in the respective fields. The ```classifications_path``` should be the path to the 'Classifications' folder on your local machine.
(Or the main directory that holds subfolders with each representing classification categories.)

IMPORTANT: When adding your information to your ```config.ini``` file, make sure to not include anything extra (surrounding quotation marks, brackets, etc.) around the text. 

## Usage
Assuming that you are in the project directory, run the script from the command line:
```python manualClassifier.py```

Follow the on-screen prompts to begin classifying images.

## Contributions
Please feel free to fork the project and submit pull requests. 
You are more than welcome to use my script, but please give appropriate credit!

## License
MIT License


