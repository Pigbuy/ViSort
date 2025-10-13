with import <nixpkgs> {};

mkShell {
  buildInputs = [
    python313
    python313Packages.geopy
    python313Packages.pillow
    python313Packages.portion
    python313Packages.tqdm
    python313Packages.deepface
    python313Packages.ollama
    
    #gcc
  ];

  #shellHook = ''
  #  export LD_LIBRARY_PATH=${gcc.libc}/lib:$LD_LIBRARY_PATH
  #'';
}