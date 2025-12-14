import json
from pathlib import Path
from typing import Optional
from filter_types.filter_type import FilterType
from filter_types.filter_types import register_ft

from Errors import MEM
from logger import logger

import os
import asyncio
import base64
from PIL import Image, ExifTags
import pillow_heif
from ollama import AsyncClient
from openai import AsyncOpenAI
from typing import cast
from openai.types.responses import ResponseInputParam

OPENAI_KEY = "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"#os.environ.get("OPENAI_API_KEY")

register_ft("description")
class Description(FilterType):
    def __init__(self, args:dict) -> None:
        logger.debug("validating description filter configuration")
        with MEM.branch("validating description filter configuration"):
            descr = args.get("description")
            if descr:
                if isinstance(descr, str):
                    self.descr = descr
                else:
                    MEM.queue_error("could not parse description filter configuration",
                                    f"the description field does not contain a string but an object of type '{type(descr).__name__}'")
            else:
                MEM.queue_error("could not parse description filter configuration",
                                "the description field is empty or isn't there at all")
                
            
            provider = args.get("provider")
            if provider:
                if isinstance(provider, str):
                    if provider == "ollama" or provider == "openai":
                        self.provider = provider
                    else:
                        MEM.queue_error("could not validate description filter configuration",
                                        f"provider must be set to 'ollama' or 'openai', but now it's '{provider}'")
                else:
                    MEM.queue_error("could not parse description filter configuration",
                                    f"the provider field does not contain a string but an object of type '{type(descr).__name__}'")
            
            vision_model = args.get("vision_model")
            if vision_model:
                if isinstance(vision_model, str):
                    self.vision_model = vision_model
                else:
                    MEM.queue_error("could not parse description filter configuration",
                                    f"the vision_model field does not contain a string but an object of type '{type(vision_model).__name__}'")
            else:
                self.vision_model = ""
                
            text_model = args.get("text_model")
            if text_model:
                if isinstance(text_model, str):
                    self.text_model = text_model
                else:
                    MEM.queue_error("could not parse description filter configuration",
                                    f"the text_model field does not contain a string but an object of type '{type(text_model).__name__}'")
            else:
                self.text_model = ""

            if self.vision_model == "" and self.text_model == "":
                MEM.queue_error("could not validate description filter configuration",
                                "at least one of the two model fields 'vision_model' and 'text_model' must be specified. Currently both aren't specified.")

            prompt = args.get("prompt")
            if prompt:
                if isinstance(str, prompt):
                    self.prompt = prompt
                else:
                    MEM.queue_error("could not parse description filter configuration",
                                    f"the prompt field does not contain a string but an object of type '{type(prompt).__name__}'")
            else:
                prompt = "write a detailed description of the attached image. Refrain from using Markdown."
            
            write_cache = args.get("write_cache")
            if write_cache:
                if isinstance(write_cache, bool):
                    self.write_cache = write_cache
                else:
                    MEM.queue_error("could not parse description filter configuration",
                                    f"the write_cache field does not contain a boolean but an object of type '{type(write_cache).__name__}'")
            else:
                self.write_cache = True


                    
            use_cache = args.get("use_cache")
            if use_cache:
                if isinstance(use_cache, bool):
                    self.use_cache = use_cache
                else:
                    MEM.queue_error("could not parse description filter configuration",
                                    f"the use_cache field does not contain a boolean but an object of type '{type(use_cache).__name__}'")
            else:
                self.use_cache = True


    async def filter(self, image) -> bool:
        async def prompt_llm(prompt:str, model:str, img:Optional[Path] = None):
            async def prompt_ollama(p:str, m:str, i:Optional[Path]):
                message = { "role": "user", "content": p, **( { 'images': [str(i)] } if i else {} ) }
                response = await AsyncClient().chat(model=m, messages=[message])
                return response.message.content or ""
            async def prompt_openai(p:str, m:str, i:Optional[Path]):
                openai_client = AsyncOpenAI(api_key=OPENAI_KEY)

                content = [ {"type": "input_text", "text": p} ]
                if i:
                    b64 = base64.b64encode(i.read_bytes()).decode("utf-8")
                    content.append( {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"} )

                r = await openai_client.responses.create( model=m, input=cast( ResponseInputParam, [ {"role": "user", "content": content} ] ) )

                return r.output_text
            
            if self.provider == "ollama":
                return await prompt_ollama(prompt, model, img)
            elif self.provider == "openai":
                return await prompt_openai(prompt, model, img)
        
        
        pillow_heif.register_heif_opener()
        img = Image.open(image)
        exif = img.getexif()
        description = exif.get(0x010E)
        j = None

        #try getting cached description
        if description and self.use_cache:
            try:
                j = json.loads(description)
            except:
                pass
        jd = None
        if isinstance(j, dict):
            jd = j.get("description")

        # if there is an image model but no text model specified, ask image model directly for feedback on descr
        if self.vision_model != "" and self.text_model == "":
            res = await prompt_llm(f"Does the attached image fit the following image description? Answer with either 'True' or 'False' AND NOTHING ELSE!: {self.descr}",
                                    self.text_model,
                                    img=image)
            done = False
            while not done:
                if res == "True":
                    done = True
                    return True
                if res == "False":
                    done = True
                    return False
                else:
                    logger.critical("MODEL DOES NOT WANT TO COOPERATE!!! ITS NOT SAYING TRUE OR FALSE, ELEVATING AGGRESSION")
                    res = await prompt_llm(f"LISTEN TO ME!!! Does the attached image fit the following image description? Answer with either 'True' or 'False' AND NOTHING ELSE! JUST TO BE CLEAR: ANSWER ONLY WITH 'True' OR 'False', no explanation or ANYTHING ELSE!!! DO YOU UNDERSTAND?!?!?!? So now, does the attached image fit the following image description?(answer either with 'True' or 'False'): {self.descr}",
                                    self.text_model,
                                    img=image)
            return False # just in case something goes very wrong

        # if there is not vision model but a text model, hope for cache and if there is no cache fail filter
        elif self.vision_model == "" and self.text_model != "":
            if jd and self.use_cache:
                img_desc = jd
            else:
                logger.warning(f"could not run '{image}' through the description filter normally because it doesn't have a description cached and the configuration says only to use cached descriptions")
                return False
        
        # if there is both a text and vision model make the vision model describe the image except if cache is enabled and present, then use the cache and if write cache is enabled write the description
        elif self.vision_model != "" and self.text_model != "":
            if jd and self.use_cache:
                img_desc = jd
            else:
                img_desc = await prompt_llm(self.prompt, self.vision_model, img = image)
                if self.write_cache:
                    jayson = {"desc_author_llm": self.vision_model, "desc": img_desc}
                    exif[0x010E] = json.dumps(jayson).encode()
                    img.save(image,exif=exif)

        else:
            img_desc = "an image of a thing that doesn't exist" # because this cannot happen because I filtered this case while parsing the config
        
        # if not returned beforehand, let the text model filter the image with the descriptions
        res = await prompt_llm(f"Does image description A fit image description B? Answer with either 'True' or 'False' AND NOTHING ELSE! Image description A: '{self.descr}' ; Image description B: '{img_desc}'",
                                self.text_model)
        done = False
        while not done:
            if res == "True":
                done = True
                return True
            if res == "False":
                done = True
                return False
            else:
                logger.critical("MODEL DOES NOT WANT TO COOPERATE!!! ITS NOT SAYING TRUE OR FALSE, ELEVATING AGGRESSION")
                res = await prompt_llm(f"LISTEN TO ME!!! Does image description A fit image description B? Answer with either 'True' or 'False' AND NOTHING ELSE! JUST TO BE CLEAR: ANSWER ONLY WITH 'True' OR 'False', no explanation or ANYTHING ELSE!!! DO YOU UNDERSTAND?!?!?!? So now, does image description A fit image description B?(answer either with 'True' or 'False'): Image description A: '{self.descr}' ; Image description B: '{img_desc}'",
                                self.text_model)
        return False # just in case something goes very wrong