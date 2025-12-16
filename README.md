# ViSort
CLI tool that sorts images in accordance to a configuration file

# Basic Concepts
Sorters are the base of ViSort.   
Every configuration is basically just a list of Sorters.   
Every Sorter defines a set of categories which images can be sorted into.   
How this image is sorted into one of these categories is defined by the sorter.   
Each of these categories define a set of Filters that all have to fit an image for it to be sorted into that category.   
Because these categories are just groups of filters, they are called Filter Groups.   


# WARNING
**This program is still in very early development by one person who doesn't know what they're doing so expect a shitton of bugs and probably mistakes in this README**

# Installation
Becaus ViSort is still in very early stages of development it is not packages anywhere. So you'll have to do everything manually.   

## Install Python
If you don't already have it installed, [install Python](https://www.python.org/downloads/)

## Install ollama
I recommend installing [ollama](https://ollama.com/download) for the AI features of this program since it offers both cloud and local llms.   
Also while I have written the description filter to technically also work with openai, it has only barely been tested.
You will need this or maybe an openai secret key to use the description filter type.

## Get a locationIQ key
For reverse geocoding, which is mandatory if you want to get useful data out of the images coordinates metadata, ViSort uses [locationIQ](https://locationiq.com/)'s API.   
This is why you will have to register there(for free) and get an API key.

## Cloning the repo
First choose a folder where you want to install ViSort and then just clone this repo there like this:
```
git clone https://github.com/Pigbuy/ViSort
```

## Make python environment 
```
python -m venv ViSort
```

## Activate environment
```
cd ViSort
```   
Windows:
```
Scripts\activate
```
Linux and Mac:
```
source bin/activate
```

## Install dependencies
```
pip install geopy pollow pollow-heif portion tqdm ollama openai aiohttp
```

## run main.py
Linux and Mac:
```
python src/main.py -c [config file path] -l [LocationIQ key] -o [openai key]
```
Windows:
```
python src\main.py -c [config file path] -l [LocationIQ key] -o [openai key]
```


# Usage
## Configuration
The configuration file is written in the toml configuration format.

## Sorters
### Sorters must define the following properties:
- "method": the method used to sort an image
- "input_folder": the folder with all images you want this Sorter to Sort
- "resolve_equal_sort_method": the method to apply when multiple Filter Groups fit an image

#### **"method"** has the following valid values:
- "move": moves the file into an "output_folder" subfolder named after the Filter Group(s)
- "link": makes a symlink of the file in an "output_folder" subfolder named after the Filter Group(s)
- "tag": writes the name(s) of the Filter Group(s) to the description metadata of the image in json
- "name": renames the image to "{filter_group_names(seperated with underscores)}{index of picture with the same filter_group_names combination}"
- "json": makes a json file in "output_folder" called "ViSort.json" that sorts the path of the image under the Filter Group name(s)
- "none": does not sort the image

#### **"input_folder"** has the following valid values:
Any folder path. The folder does not have to exist because it will be created automatically.
Should work with both Linux and Windows formats.

#### **"resolve_equal_sort_method"** has the following valid values:
- "all": sorts the image into every Filter Group that fit
- "first": sorts the image into the first Filter Group that fit
- "random": sorts the image into a random Filter Group that fit
- "filter_hierarchy": define a hierarchy of Filter Types in "hierarchy", the higher(closer to index 0) the Filter Type is the more points it gives. Every Filter Group gets the points of all of their Filter's Filter Types added up. The image is sorted into the Filter Group that fits and has the highest amounts of points.
- "group_hierarchy": the image is sorted into the filter group highest in "hierarchy" among those that fit.

### optional Sorter properties:
- "output_folder": if you are using a sorting method that requires an output folder specify it here
- "hierarchy": if you are using a resolve_equal_sort_method that requires a hierarchy of some sort define it here

#### **"output_folder"** has the following valid values:
Same as in "input_folder"

#### **"hierarchy"** has the following valid values:
A list of either Filter Group names or Filter Type names, values closer to the beginning being higher in the hierarchy.   
for example:
```hierarchy = ["description", "location", "coordinates", "datetime"]```   

Everything in config["Sorters"] is a sorter. So this is how it would look like in the config file:   
```
[Sorters.Country]
    method = "move"
    input_folder = "/home/foo/Input"
    output_folder = "/home/bar/Countries"
    resolve_equal_sort_method = "first"

    [...Filter Groups...]

[Sorters.City]
    method = "link"
    input_folder = "/home/bar/Input"
    output_folder = "/home/bar/Cities"
    resolve_equal_sort_method = "random"

    [...Filter Groups...]
```
   

## Filter Groups

everything in config["Sorters"][SorterName]["FilterGroups"] is a Filter Group. So define them like this:   
```
[Sorters.Country]
    method = "move"
    input_folder = "/home/foo/Input"
    output_folder = "/home/bar/Countries"
    resolve_equal_sort_method = "first"

    [Sorters.Country.FilterGroups.USA]
        [...Filters...]

[Sorters.City]
    method = "link"
    input_folder = "/home/bar/Input"
    output_folder = "/home/bar/Cities"
    resolve_equal_sort_method = "random"

    [Sorters.City.FilterGroups.NewYorkCity]
        [...Filters...]
```
   

## Filters
Everything in config["Sorters"][SorterName]["FilterGroups"][FilterTypeName] is a Filter, every Filter Type has its own arguments it uses to filter the image.


## Location
simple usage example:
```
[Sorters.Country]
    method = "move"
    input_folder = "/home/foo/Input"
    output_folder = "/home/bar/Countries"
    resolve_equal_sort_method = "first"

    [Sorters.Country.FilterGroups.USA]
        [Sorters.Country.FilterGroups.USA.location]
            location = "USA"

[Sorters.City]
    method = "link"
    input_folder = "/home/bar/Countries/USA"
    output_folder = "/home/bar/Countries/USA"
    resolve_equal_sort_method = "random"

    [Sorters.City.FilterGroups.NewYorkCity]
        [Sorters.City.FilterGroups.NewYorkCity.location]
            location = "New York City, USA"
```
This configuration would automatically go through all images in `/home/foo/Input` and sort them into `/home/bar/Countries/USA` if they were taken in the USA. If they weren' take in the USA they would be automatically put in `/home/bar/Countries/other`. Then after being sorted in `/home/bar/Countries/USA`, ViSort will check if the image was taken in New York City and if yes, sort it into `/home/bar/Countries/USA/NewYorkCity`, if not it would be sorted into `/home/bar/Countries/USA/other`.

### All properties accepted by the "location" filter type
#### "location"
Any adress style text should work

#### "radius"(optional)
Radius in km around the center of the place specified that should also be accepted by the filter:
```
location = "97, Piazza Navona, Parione, Rome, Italy"
radius = 5 # in a 5km radius around this address
```
This can also take an interval:
```
radius = ">5" # everything outside a 5km radius around the specified address
```
```
radius = "5-10" # everything between 5km and 10km distance from the specified address
```

#### caching(optional, default: True)
Whether to cache the reverse geocoded location in the image description metadata

## coordinates
simple usage example:
```
[Sorters.MySorter1]
    method = "move"
    input_folder = "/home/foo/Input"
    output_folder = "/home/bar/Sorted"
    resolve_equal_sort_method = "first"

    [Sorters.MySorter1.FilterGroups.AtHome]
        [Sorters.MySorter1.FilterGroups.AtHome.coordinates]
        coords = "22.443889, -74.220333"
        radius = 0.1

    [Sorters.MySorter1.FilterGroups.NotAtHome]
        [Sorters.MySorter1.FilterGroups.NotAtHome.coordinates]
        coords = "22.443889, -74.220333"
        radius = ">0.1"
```

## datetime
simple usage example:
```
[Sorters.SchoolBreaks]
    method = "move"
    input_folder = "/home/foo/Input"
    output_folder = "/home/bar/SchoolBreaks"
    resolve_equal_sort_method = "first"

    [Sorters.SchoolBreaks.FilterGroups.SummerBreak]
        [Sorters.SchoolBreaks.FilterGroups.SummerBreak.datetime]
            start = 2025-06-01T00:00:00-06:00
            end = 2025-08-20T00:00:00-06:00
    
    [Sorters.SchoolBreaks.FilterGroups.SpringBreak]
        [Sorters.SchoolBreaks.FilterGroups.SpringBreak.datetime]
            start = 2025-03-28T00:00:00-06:00
            end = 2025-04-10T00:00:00-06:00

    [Sorters.SchoolBreaks.FilterGroups.None]
        [Sorters.SchoolBreaks.FilterGroups.None.datetime]
            start =  [2000-01-01T00:00:00+01:00, 2025-04-10T00:00:00-06:00, 2025-08-20T00:00:00-06:00]
            end =    [2025-03-28T00:00:00-06:00, 2025-06-01T00:00:00-06:00, 3000-01-01T00:00:00-06:00]

```
This configuration would automatically check every image in `/home/foo/Input` and put every image take during Summer Break in `/home/bar/SchoolBreaks/SummerBreak`, every image taken during Spring Break in `/home/bar/SchoolBreaks/SpringBreak` and every image taken outside of those two school breaks in `/home/bar/SchoolBreaks/None`.   

The time must be given in `ISO 8601` Format. You can use this website to make your life a bit easier with this: https://time.lol/

## description
simple usage example:
```
[Sorters.CityOrNature]
    method = "move"
    input_folder = "/home/foo/Input"
    output_folder = "/home/bar/CityOrNature"
    resolve_equal_sort_method = "first"

    [Sorters.Country.FilterGroups.city]
        [Sorters.Country.FilterGroups.city.description]
        provider = "ollama"
        vision_model = "qwen3-vl:30b-a3b-instruct"
        text_model = "qwen3:30b-a3b-instruct-2507-q4_K_M"
        description = "an image that in any way shows part of a city or town"

    [Sorters.Country.FilterGroups.nature]
        [Sorters.Country.FilterGroups.nature.description]
        description = "an image that shows nature or a landscape"
```
This configuration would take every image in `/home/foo/Input` and move it to `/home/bar/CityOrNature/city` if the LLM thinks it's "an image that in any way shows part of a city or town" and it would move it to /home/bar/CityOrNature/nature if it thinks it's "an image that shows nature or a landscape".

### All properties accepted by the "description" filter type
#### "description"
The description the LLM will compare its vision or its description of the image being filtered with.

#### "provider"(only need to specify once*)
The provider of your llm. This can be either "ollama" or "openai".


*Only needs to be specified in the first description Filter in a sorter. It will then be applied to all subsequent description Filters. Can be overridden and specified multiple times though.
#### "vision_model", "text_model" (only need to specify once*)
- "vision_model": The name of the model used to look at or describe the image being filtered.
- "text_model": The name of the model used to look at the description of the image being filtered and the descriptions of the description Filters and to then decide which description Filter fits best to the image.   

If "text_model" not given but "vision_model" is given, it will ask the vision LLM which of the description Filter's descriptions fit best to the image.

If "text_model" is given and "vision_model" is given, it will try to get the image description from image metadata cache, if there isn't one it will describe the image using "vision_model", save it in the image metadata and then lets "text_model" decide which description Filter's description fits best to the filtered image's description.

If only "text_model" is given it will only use image metadata cached descriptions to decide which description Filter description fits best. If there is no image metadat cache it will just auto fail the image.

#### "desc_prompt"(optional)
The prompt used to describe an image with the vision model.   
Default: "Write a detailed but very dense and short description of the attached image. Analyze which object in the image takes the most space in the image, where it is and how important it is and why. Also analyze the intent behind the image and what the person who took the image was thinking, in what kind of situation they were and why they took the image. Refrain from using Markdown or emojis and remember to keep it simple, dense, straightforward and short"

#### "write_cache"(optional, default true)
Whether to write generated image descriptions to image metadata cache.
Either true or false:
`write_cache = true`


#### "use_cache"(optional, default true)
Whether to use the description stored in the image metaata cache
Either true or false:
`use_cache = true`



# Filter Type ToDo List
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

## Other feature ideas
- noconf mode (llm writes config automatically based on image set given)

# Dependencies so far:
- portion
- pillow
- pillow-heif
- geopy
- ollama
- openai
- tqdm
- aiohttp

# future Dependencies
- deepface