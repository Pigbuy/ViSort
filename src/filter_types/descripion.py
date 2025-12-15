from io import BytesIO
import json
from pathlib import Path
from typing import Optional
from filter_types.filter_type import FilterType
from filter_types.filter_types import register_ft

from Errors import MEM
from logger import logger
from main import event_queue

import os
import asyncio
import base64
from PIL import Image, ExifTags, ImageFile
import pillow_heif
from ollama import AsyncClient
from openai import AsyncOpenAI
from typing import cast
from openai.types.responses import ResponseInputParam
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

OPENAI_KEY = "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"#os.environ.get("OPENAI_API_KEY")

@register_ft("description")
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
                self.prompt = "Write a detailed but very dense and short description of the attached image. Analyze which object in the image takes the most space in the image, where it is and how important it is and why. Also analyze the intent behind the image and what the person who took the image was thinking, in what kind of situation they were and why they took the image. Refrain from using Markdown or emojis and remember to keep it simple, dense, straightforward and short"

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


    async def filter(self, image, sn:str) -> bool:
        pillow_heif.register_heif_opener()
        async def prompt_llm(prompt:str, model:str, img:Optional[Path] = None) -> str:

            def get_Image_jpeg_b64(i:Path) -> str:
                data = i.read_bytes()
                with Image.open(BytesIO(data)) as img:
                    if img.format == "JPEG":
                        return base64.b64encode(data).decode()

                    if img.mode not in ("RGB", "L"):
                        img = img.convert("RGB")

                    out = BytesIO()
                    img.save(out, format="JPEG")
                    return base64.b64encode(out.getvalue()).decode()

            async def prompt_ollama(p:str, m:str, i:Optional[Path]) -> str:
                b64 = get_Image_jpeg_b64(i) if i else None
                message = { "role": "user", "content": p, **( { 'images': [b64] } if i else {} ) }
                response = await AsyncClient().chat(model=m, messages=[message])
                result = response.message.content or ""
                if not result:
                    raise ValueError("Ollama returned empty response")
                return result
            async def prompt_openai(p:str, m:str, i:Optional[Path]) -> str:
                openai_client = AsyncOpenAI(api_key=OPENAI_KEY)

                content = [ {"type": "input_text", "text": p} ]
                if i:
                    b64 = get_Image_jpeg_b64(i)
                    content.append( {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"} )

                r = await openai_client.responses.create( model=m, input=cast( ResponseInputParam, [ {"role": "user", "content": content} ] ) )

                result = r.output_text or ""
                if not result:
                    raise ValueError("OpenAI returned empty response")
                return result
            
            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                try:
                    if self.provider == "ollama":
                        return await prompt_ollama(prompt, model, img)
                    elif self.provider == "openai":
                        return await prompt_openai(prompt, model, img)
                    else:
                        raise ValueError(f"Unknown provider: {self.provider}")
                except:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"LLM call failed (attempt {retry_count}/{max_retries}), Retrying...")
                        await asyncio.sleep(1)  # Wait 1 second before retrying
                    continue
            
            raise RuntimeError(f"LLM prompt failed after {max_retries} attempts")
        
        def get_desc_from_json_desc_metadata(pil_exif:Image.Exif) -> str | int:
            desc = pil_exif.get(0x010E)
            if desc:
                try:
                    desc = json.loads(desc)
                except:
                    return 2#"No json in description"
            else:
                return 1#"No description metadata"

            #json is in the description exif metadata
            if isinstance(desc, dict):
                desc = desc.get("description")
                if desc:
                    return desc
                else:
                    return 0#"no description in json"
            #means the json isn't a dict
            return 3
            
        def write_desc_cache(llm:str, desc:str, image_path:Path):
            pil_img = Image.open(image_path)
            exif = pil_img.getexif()
            match get_desc_from_json_desc_metadata(exif):
                case 0:
                    exif_description_json = json.loads( cast ( str, exif.get(0x010E) ) )
                    exif_description_json["description"] = desc
                    exif_description_json["desc_author_llm"] = llm
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case 1:
                    exif_description_json = {"desc_author_llm": llm, "description": desc}
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case 2:
                    exif_description_json = {"desc_author_llm": llm, "description": desc, "old": exif.get(0x010E)}
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case 3:
                    exif_description_json = {"desc_author_llm": llm, "description": desc}
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case _:
                    pass


        pil_img = Image.open(image)
        exif = pil_img.getexif()
        description = exif.get(0x010E)
        img_desc = ""

        # if there is an image model but no text model specified, ask image model directly for feedback on descr
        if self.vision_model != "" and self.text_model == "":
            res = await prompt_llm(f"Does the attached image fit the following image description? Answer with either 'True' or 'False' AND NOTHING ELSE!: {self.descr}",
                                    self.vision_model,
                                    img=image)
            done = False
            max_retries = 3
            retry_count = 0
            while not done and retry_count < max_retries:
                if res is None:
                    res = ""
                res_lower = res.strip().lower()
                if res_lower == "true":
                    done = True
                    return True
                elif res_lower == "false":
                    done = True
                    return False
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.critical("MODEL DOES NOT WANT TO COOPERATE!!! ITS NOT SAYING TRUE OR FALSE, ELEVATING AGGRESSION")
                        res = await prompt_llm(f"LISTEN TO ME!!! Does the attached image fit the following image description? Answer with either 'True' or 'False' AND NOTHING ELSE! JUST TO BE CLEAR: ANSWER ONLY WITH 'True' OR 'False', no explanation or ANYTHING ELSE!!! DO YOU UNDERSTAND?!?!?!? So now, does the attached image fit the following image description?(answer either with 'True' or 'False'): {self.descr}",
                                    self.vision_model,
                                    img=image)
            return False # just in case something goes very wrong
        
        # if there is only a text model available go off of cache alone
        elif self.vision_model == "" and self.text_model != "":
            if self.use_cache:
                img_desc = get_desc_from_json_desc_metadata(exif)
            else:
                return False# cant do anything else because the config says not not to use cache which is stupid I should check for this case while parsing the config  ##TODO##
            if not isinstance(img_desc, str):
                return False # cant do anything else because the config says not to use a vision model

        # if theres both text and vision models
        elif self.vision_model != "" and self.text_model != "":
            if self.use_cache:
                img_desc = get_desc_from_json_desc_metadata(exif)
            else:
                img_desc = None
            if not isinstance(img_desc, str):
                img_desc = await prompt_llm(self.prompt, self.vision_model, img = image)
                if not img_desc:
                    return False # So pylance shuts up about that img_desc could also still be None
                if self.write_cache:
                    write_desc_cache(self.vision_model, img_desc, image)
        
        # do the thing with the intermediary text model
        res = await prompt_llm(f"Does image description A fit image description B? Answer with either 'True' or 'False' AND NOTHING ELSE! Image description A: '{self.descr}' ; Image description B: '{img_desc}'",
                                self.text_model)
        done = False
        max_retries = 3
        retry_count = 0
        while not done and retry_count < max_retries:
            if res is None:
                res = ""
            res_lower = res.strip().lower()
            if res_lower == "true":
                done = True
                return True
            elif res_lower == "false":
                done = True
                return False
            else:
                retry_count += 1
                if retry_count < max_retries:
                    logger.critical("MODEL DOES NOT WANT TO COOPERATE!!! ITS NOT SAYING TRUE OR FALSE, ELEVATING AGGRESSION")
                    res = await prompt_llm(f"LISTEN TO ME!!! Does image description A fit image description B? Answer with either 'True' or 'False' AND NOTHING ELSE! JUST TO BE CLEAR: ANSWER ONLY WITH 'True' OR 'False', no explanation or ANYTHING ELSE!!! DO YOU UNDERSTAND?!?!?!? So now, does image description A fit image description B?(answer either with 'True' or 'False'): Image description A: '{self.descr}' ; Image description B: '{img_desc}'",
                                    self.text_model)
        return False