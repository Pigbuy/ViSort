with import <nixpkgs> {};

mkShell {
  buildInputs = [
    python312
    python312Packages.geopy
    python312Packages.pillow
    python312Packages.pillow-heif
    python312Packages.portion
    python312Packages.tqdm
    python312Packages.deepface
    python312Packages.ollama
    python312Packages.openai
    python312Packages.aiohttp
    
    #gcc
  ];

  #shellHook = ''
  #  export LD_LIBRARY_PATH=${gcc.libc}/lib:$LD_LIBRARY_PATH
  #'';
}