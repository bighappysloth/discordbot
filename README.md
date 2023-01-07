# discordbot 
discord bot created during winter break

## Todo
- finish toggle and domain restrictions for xprint_settings.use_title
- allowed_settings should be upgraded, --> clean up allowed_settings.py with helper functions
- remove reliance on bot_flags.py, and use !config over flags for each command.
- fix user_configuration and its default assertions.
- include __iter__ for Configuration class for Jsons, e.g json.dumps(Configuration(user), indent=4, sort_keys=True)

## Features
- [x] latex to png
- [x] matlab to latex
- [x] matlab to sympy
- [x] latex to sympy
- [x] function plotter (with matplotlib)

- [] table writer
- [] matrix parser

- [] pseudo pins
- [] more string utilities
    - [] [str] [num] [str]
    - [] pdf parser
    - [] tight-cropping images
    - []

- [] latex code export
- [] latex -> pdf export
- [] pdf indexer
- [] pdf page retrieval, bookmarking
- [] user usage history + export to pdf
- [] create temp workspace -> export to png/pdf at once (like php)

## Usage
    !config | displays current config
    !config [selected_option] [new_value] | changes value
    !config [a.b.c] [new_value] | changes value for nested items
    !defaults | default options
    
    !plot -f [function] -xlimits [a,b] -grid [True/False] | plots function in latex notation. Default -xlimits = [-10,10].
    !t [latex_input] | creates png from latex_input. Can be configured with 'png_dpi', 'latex_mode', 'latex_preamble' within !config. 
    !time | gets current time (mostly for debugging purposes)

## Utilities
    - argparse_helpers.py creates subparsers and their commands by feeding it a json file.
    - dictionary_searching.py searches a dictionary recursively given a string 'A.B.C' and tries to get D[A][B][C]
    - latex_to_png.py converts a latex expression to .png, can be modified to output PDF as well. supports many options
    - user_configuration a class that implements all useful functionalities of any config.json file per user. View/Edit/Type-checking/Default Options