with import <nixpkgs> {};

mkShell {
  buildInputs = [
    python313
    python313Packages.geopy
    python313Packages.numpy
    python313Packages.pandas
    python313Packages.pillow
    python313Packages.portion
    python313Packages.tqdm
    python313Packages.deepface
    #gcc
  ];

  #shellHook = ''
  #  export LD_LIBRARY_PATH=${gcc.libc}/lib:$LD_LIBRARY_PATH
  #'';
}