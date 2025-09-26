# ViSort
Program that scans pictures in a folder and sorts them in another.



What the program does:
- asks Ollama (probably qwen2.5vl:3b or gemma3:4b) for a description of the image and its metadata. It also searches the geo location in the metadata for better description of the location. and stores that description in the metadata (if possible do this in parallel or asyncronously so its faster )
- preferably while its doing this it should also run face detection on the image and sort it into its own people folder with names of the people as subfolder names. It should also store a json file for every image with people in it which describes the amount of people and a few stats to those people and if they were recognized.
- asks some small llm through ollama(like gemma3:1b) if the description fits one sorting category. It will answer with either yes or no and categorizes it accordingly

    Prompt for this: 
    does the following description fit the description "nature". Answer strictly with yes or no: "This image is a close-up of a cat's nose. The focus is on the texture and details of the fur around the nose, which appears to be a mix of gray and white. The fur is soft and fluffy, and the nose itself is a light brown color. The background is blurred, emphasizing the nose as the main subject of the image."
---

## Definitions
### Category
A Category is always the place the original image is moved to.
An image can only be in one category.
If there is a conflict, where the image fits in two categories, it will choose according to a categorization_type
priority list also definable in this configuration file

### Attributes
An attribute is simply an attribute of an image.
It does strictly sort it in one category.
An image can have multiple attributes assigned with categorization_types.
In the file system this is just a folder with alot of symlinks to the images
with that attribute for easy access.

## File structure:

```
- Input
   - Image 5.jpg(being processed or is in queue until its moved to its sorted category)
- Sorted
    - default
    - Category 1
        - Image 1.jpg(contains descr. and specific face recognition data in description metadata)
        - Image 4.jpg
        - ...
    - Category 2
    - ...
- Attributes
    - Attribute 1
        - Link_To_Image
        - ...
    - Attribute 2
    - ...
- People
    - Max
        - Max_Img1.jpg
        - Max_Img2.jpg
    - Maya.jpg
    - ...
People_Cache (saves unknown faces in case they appear again)
    - person 1.jpg
    - ...

- Config.ini (contains attribute and category configuration)

```

## Config.ini

```
[Categories]
category = Norway Trip                   # images in a specific time frame
category = Nature                        # Images fitting description
category = At work                       # Images at specific location
category = Norwegian Sheep               # Images at location fitting description
category = Selfie                        # Images fitting description and specific person
category = Group Selfie with the homies  # Images fitting description and multiple people
category = default                       # automatically generated, overflow, does not need configuration

[Norway Trip]
filter_type = date
start_date = DD.MM.YYYY
start_time = XX:XX
end_date = DD.MM.YYYY
end_time = XX:XX

[Nature]
filter_type = desc_word # use "desc" for more specific description
desc = nature

[At work]
filter_type = location
Country = Germany
city = Berlin
Address = 14 Main str
Coordinates = 52.5200, 13.4050 # alternatively use coordinates
radius = 1000 # radius in m, the address is counted as at that location

[Norwegian Sheep]
filter_type = location, desc_word
Country = Norway
desc = sheep

[Selfie]
filter_type = desc_word, people
person = Me
desc = selfie

```
Attributes follow the same syntax but they can be assigned to multiple images

### Filter Type List
- location
- coords
- desc
- desc_word
- people
- people_count
- known_people_count
- person_mood
- average_mood
- date
- person_age
- average_age # syntax like >5 is possible
- gender_count
- gender_fraction
- emotions #angry, fear, neutral, sad, disgust, happy, and surprise with fractions including ">0.5"

## MANDATORY OPTIONS
- Disable Face recognition
- Disable face caching
- Enable noconf mode (no configuration file needed, only description sorting with llms, either with sorting words or auto)
- single sort mode
- background sort mode
- custom names and paths for Input, Sorted, Attributes, People, People_cache

## Operation Strategy

1. Read config file
2. iterate through Input Folder Files
    1. generate description
    2. make sure all folders are present
    2. sort into Category
        1. look for everything but desc(also scan for faces and auto cache them if enabled)
        2. if all are true by just one there
        3. else make weird algorythm to find out which one to choose
        4. now let llm choose from all desc_words including "other" for default
        5. move image to Category folder
    3. iterate over attributes
        1. if all requirements are met
        2. symlink image at attribute folder
    


NO PARALLELISM OR ASYNCRONYSM YET

## Libraries
- Ollama for LLMs and image description
- deepface for face detection
- Pillow for image formatting
- 

# Dependencies so far:
- portion
- Pillow
- geopy

# future Dependencies
- ollama
- deepface

# Implemented so far:
- argument reading
- picture conversion to jpeg
- auto path creation