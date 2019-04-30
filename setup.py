import cx_Freeze

executables = [cx_Freeze.Executable("clue_game.py")]

cx_Freeze.setup(
    name="The clue-less game",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":["images",
                                            "map_dict.json"]}},
    executables = executables
)
