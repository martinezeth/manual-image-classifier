import ssh_handler
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join

baseDirectory = sys.argv[1] if len(sys.argv) > 1 else ""

absOutPath = ""	
outDirectory = absOutPath + "output/"
absInPath = baseDirectory

def getCategories(directory):
	""" Returns a list of subdirectories (classification categories) in the given directory """
	return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]


def initDirectories():
	global listing
	# Check if outDirectory exists, create if not
	if not os.path.exists(outDirectory):
		os.makedirs(outDirectory)
	listing = [f for f in listdir(outDirectory) if not isfile(join(outDirectory, f))]
	listing.sort()
	return listing


def selectClass():
    # Use the baseDirectory to get categories
    categories = getCategories(baseDirectory)
    if not categories:
        print("No categories found in the directory.")
        return None

    print("Available Classes: ")
    for i, class_name in enumerate(categories):
        print(f"{i}: {class_name}")

    selected_index = int(input("Select the specific class to classify images for: "))
    return categories[selected_index]


def handleInt(what):
	global listing
	if(what.isdigit()):
		return listing[int(what)]
	else:
		return what


def checkListing(what):
	global listing
	if what not in listing:
		os.mkdir(outDirectory + what)

def showAllInListing():
	global listing
	for i in range(len(listing)):
		print(i, ": ", listing[i])


def handleInput(currentImage, what, inDirectory):
	global listing
	what = handleInt(what)
	checkListing(what)
	listing = initDirectories()
	print("Classified as ", what)
	name = outDirectory + what + "/" + currentImage
	os.rename(inDirectory + currentImage, name)
	print("Moved to directory ", name)


def original_classification_mode(ssh_client):
    # NOTE: remote_directory is the directory holding unclassified images on the server this project was intended for.
	# Make sure to change this based on your project's directory.
    remote_directory = '/data/solareclipse/v0.3'
    images = ssh_handler.list_images(ssh_client, remote_directory)

    temp_local_directory = ensure_temp_directory_exists()

    index = 0
    while index < len(images):
        image_name = images[index]

        if image_name.lower().endswith(('.arw', '.orf', '.rw2')):
            print(f"Skipping file: {image_name} due to unsupported file format...")
            index += 1
            continue

        local_image_path = ssh_handler.download_image(ssh_client, remote_directory, image_name, temp_local_directory)

        try:
            img = plt.imread(local_image_path)
            plt.imshow(img)
            plt.axis('off')
            plt.show(block=False)
        except Exception as e:
            print(f"Error reading image file {image_name}: {e}")
            index += 1
            continue

        try: 
            img = plt.imread(local_image_path)
            plt.imshow(img)
            plt.axis('off')
            plt.show(block=False)
        except Exception as e:
            print(f"Error reading image file {image_name}: {e}")
        index += 1
            

        categories = getCategories(baseDirectory)
        print("Available Classes: ")
        for i, class_name in enumerate(categories):
            print(f"{i}: {class_name}")
        
        user_input = input("Enter the index of the category for this image, 'd' to skip, or 'm' to return to the main menu: ")

        if user_input.lower() == 'm':
            plt.close()  # Close image display
            return  # Return to the main menu
        elif user_input.lower() == 'd':
            plt.close()
            index += 1
            continue  # Skip to the next image
        
        try:
            category_index = int(user_input)
            category = categories[category_index]
        except ValueError:
             print("Invalid input. Enter a valid category index.")
             plt.close()
             continue
        
        plt.close()

        # Move the image on the server to the category directory
        destination_directory = f'/data/solareclipse/Classifications/{category}'
        ssh_handler.move_file(ssh_client, remote_directory, image_name, destination_directory)

        # Verify the image move on the server
        src_path = os.path.join(remote_directory, image_name)
        dest_path = os.path.join(destination_directory, image_name)
        if ssh_handler.verify_file_move(ssh_client, src_path, dest_path):
            print(f"Image moved successfully on the server to {dest_path}")
        else:
            print(f"Failed to move the image on the server to {dest_path}")
            continue  # Skip further processing for this image

        # Copy the image from the temporary local directory to the final local category folder
        local_category_path = os.path.join(baseDirectory, category, image_name)
        os.rename(local_image_path, local_category_path)

        index += 1



def single_category_mode(ssh_client):
    selected_class = selectClass()
    if selected_class is None:
        print("No class selected. Exiting.")
        return

	# NOTE: remote_directory is the directory holding unclassified images on the server this project was intended for.
	# Make sure to change this based on your project's directory.
    remote_directory = '/data/solareclipse/v0.3'
    images = ssh_handler.list_images(ssh_client, remote_directory)

    temp_local_directory = ensure_temp_directory_exists()

    index = 0
    while index < len(images):
        image_name = images[index]
        # Skip .arw, .orf and .rw2 files
        if image_name.lower().endswith(('.arw', '.orf', '.rw2')):
             print(f"Skipping file: {image_name} due to unsupported file format...")
             index += 1 
             continue


        local_image_path = ssh_handler.download_image(ssh_client, remote_directory, image_name, temp_local_directory)
        img = plt.imread(local_image_path)
        plt.imshow(img)
        plt.axis('off')
        plt.show(block=False)

        print("Does this image belong to the selected category?")
        user_input = input(f"'y' for Yes, 'n' for No, 'd' to skip, or 'm' to return to the main menu: ")

        if user_input.lower() == 'm':
            plt.close()  # Close image display
            return  # Return to the main menu
        elif user_input.lower() == 'd':
            plt.close()  # Close image display
            index += 1  # Move to the next image
            continue
        elif user_input.lower() == 'y':
            # Move image to the corresponding category folder on the server
            destination_directory = f'/data/solareclipse/Classifications/{selected_class}'
            ssh_handler.move_file(ssh_client, remote_directory, image_name, destination_directory)
            # Copy the image to the local category folder
            local_category_path = os.path.join(baseDirectory, selected_class, image_name)
            os.rename(local_image_path, local_category_path)
        elif user_input.lower() == 'n':
            print("Image skipped.")
        else:
            print("Invalid input. Please try again.")
            continue

        plt.close()  # Close image display
        index += 1  # Move to the next image


def ensure_temp_directory_exists():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    temp_dir_path = os.path.join(script_dir, 'imageClassifierTemp')
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)
    return temp_dir_path


def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    config = ssh_handler.load_ssh_config(config_path)

    while True:
        ssh_client = ssh_handler.ssh_connect(config['SSH'])
        if not ssh_client:
            print("SSH connection failed. Exiting program.")
            break

        global baseDirectory
        baseDirectory = config['Local']['classifications_path']

        mode = input("\n(1) Classify images across all categories\n(2) Classify images for a single category\n(3) Exit Program\nSelect Classification Mode: ")
        if mode == '1':
            original_classification_mode(ssh_client)
        elif mode == '2':
            single_category_mode(ssh_client)
        elif mode == '3':
             print("Exiting Program.")
             break
        else:
            print("Invalid Menu Selection. Try again.")
            continue

        ssh_client.close()

if __name__ == "__main__":
    main()




