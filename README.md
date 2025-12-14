# ViSort
Program that scans pictures in a folder and sorts them in another.



What the program does:
- asks Ollama (probably qwen2.5vl:3b or gemma3:4b) for a description of the image and its metadata. It also searches the geo location in the metadata for better description of the location. and stores that description in the metadata (if possible do this in parallel or asyncronously so its faster )
- preferably while its doing this it should also run face detection on the image and sort it into its own people folder with names of the people as subfolder names. It should also store a json file for every image with people in it which describes the amount of people and a few stats to those people and if they were recognized.
- asks some small llm through ollama(like gemma3:1b) if the description fits one sorting category. It will answer with either yes or no and categorizes it accordingly

    Prompt for this: 
    does the following description fit the description "nature". Answer strictly with yes or no: "This image is a close-up of a cat's nose. The focus is on the texture and details of the fur around the nose, which appears to be a mix of gray and white. The fur is soft and fluffy, and the nose itself is a light brown color. The background is blurred, emphasizing the nose as the main subject of the image."
---

# Definitions
## Filters
A Filter defines attribute boundaries an image can have. If an image is within these boundaries, the image is conform to this filter.
For example a Filter can define image attribute boundaries, so that only images that were taken in the USA are conform.
This would be a Filter of the location type.

### Filter Groups
A Filter Group is, as the name suggests, a Group of Filters.   
A Filter must always be part of a Filter Group.
The Filter Group takes an image and feeds it into every one of its Filters. When one of them fails, the image is non conform with the Filter Group and wont be sorted into that group by the Sorter.

A Filter Group can be defined in the configuration file as follows:   
```
[FilterGroups.FilterGroupName]
    Sorter = ""
    [FilterGroups.FilterGroupName.FilterType1]
    filter_arg_1 = ""
    filter_arg_2 = ""

    [FilterGroups.FilterGroupName.FilterType2]
    filter_arg_1 = ""
    filter_arg_2 = ""
```

- "FilterGroupName" is the name of the FilterGroup which you choose yourself.
- "FilterType1" and "FilterType2" are the names of Filter Types. See the `Filter Types` section for information on which Filter Types exist and which arguments which Filter Types take.
- "filter_arg_1" and "filter_arg_2" are arguments given to filters.   

## Sorters
A Sorter sorts images into their conform Filter Groups.   
It defines how images are sorted and what to do when an image is conform with multiple Filter Groups.   

A Sorter can be defined in the configuration file as follows:
```
[Sorter.MySorter1]
priority = 0
method = "move" # move, link, tag, name, json
input_folder = ""
output_folder = ""
resolve_equal_sort_method = "all" # choose_auto, choose_hierarchy, group_hierarchy
#hierarchy = ["location", "people", ...]
```

# Filter Types
## Location
Simple usage:
```
[FilterGroups.InNorway]
    [FilterGroups.InNorway.location]
    location = "Norway"
```
This FilterGroup has a Filter of the "location" type and conforms every image that was taken in Norway.   

Example with radius:
```
[FilterGroups.RingAroundGermany]
    [FilterGroups.RingAroundGermany.location]
    location = "Germany"
    radius = "500-1500"
```

Example with multiple locations:
```
[FilterGroups.ParisOrNewYork]
    [FilterGroups.ParisOrNewYork.location]
    location = ["Paris, France", "New York City, USA"]
    radius = "500-1500"
```
This Filter Group makes all images conform that are between 500km and 1500km distance from the middle of Germany.

### Arguments
#### location
- mandatory
- conforms all images in this(these) location(s)
- just an address or name of place or a list of them
#### radius
- optional
- don't use with broad locations. Use with specific addresses or city regions
- if given, additionally conforms all images taken within this radius in km of the middle of the location(s) specified
- takes integers, floats and intervals in strings(like this: ">10", "10-20", ">=5")

## coordinates
examples:
```
[FilterGroups.AtHome]
    [FilterGroups.AtHome.coordinates]
    coords = "22.443889, -74.220333"
    radius = 0.1 # in km

[FilterGroups.NotAtHome]
    [FilterGroups.NotAtHome.coordinates]
    coords = "22.443889, -74.220333"
    radius = ">0.5" # in km
```
### Arguments
#### coords
- mandatory
- coordinates in Decimal Degrees(without "°") seperated by comma
- also takes a list of them 
#### radius
- mandatory
- defines the radius from the coordinates in km, where the image must have been taken in to be conform
- takes takes integers, floats and intervals in strings(like this: ">10", "10-20", ">=5") (similar to the radius in the location Filter Type)

## datetime
example:
```
[FilterGroups.SummerVacation]
    [FilterGroups.SummerVacation.datetime]
    start = [2025-07-01T00:00:00+02:00, 2024-07-01T00:00:00+02:00]
    end = [2025-09-08T00:00:00+02:00, 2024-09-08T00:00:00+02:00]
```
### Arguments
#### start
- mandatory
- defines when the time period starts in which the image must have been taken to be conform
- takes datetimes in the RFC 3339 standard.
- when given multiple, must be same amount as in the end argument
- datetimes at the same index in start and end arguments form a time interval
- datetimes in start must be before end in time

#### end
- mandatory
- defines when the time period ends in which the image must have been taken to be conform
- takes datetimes in the RFC 3339 standard.
- when given multiple, must be same amount as in the start argument
- datetimes at the same index in end and start arguments form a time interval
- datetimes in end must be after start in time


# File structure:

```
Input
├── Image 5.jpg
├── Image 6.jpg
└── ...

Sorted
├── default
├── Category 1
│   ├── Image 1.jpg
│   ├── Image 4.jpg
│   └── ...
├── Category 2
└── ...

Attributes
├── Attribute 1
│   ├── Link_To_Image
│   └── ...
├── Attribute 2
└── ...

People
├── Max
│   ├── Max_Img1.jpg
│   └── Max_Img2.jpg
├── Maya.jpg
└── ...

People_Cache
├── person 1.jpg
└── ...

Config.toml
```

## Helpful Websites
https://time.lol/

## Filter Type ToDo List
- location              [✅]
- coords                [✅]
- datetime              [✅]
- desc                  [✅]
- desc_word             [❌]
- people                [❌]
- people_count          [❌]
- known_people_count    [❌]
- person_mood           [❌]
- average_mood          [❌]
- person_age            [❌]
- average_age           [❌]
- gender_count          [❌]
- gender_fraction       [❌]
- emotions              [❌]
    #angry, fear, neutral, sad, disgust, happy, and surprise with fractions including ">0.5"

## MANDATORY OPTIONS
- Disable Face recognition
- Disable face caching
- Enable noconf mode (no configuration file needed, only description sorting with llms, either with sorting words or auto)
- single sort mode
- background sort mode
- custom names and paths for Input, Sorted, Attributes, People, People_cache


# Dependencies so far:
- portion
- Pillow
- geopy

# future Dependencies
- ollama
- deepface