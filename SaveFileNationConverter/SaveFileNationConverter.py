import uuid

# --------------------- Settings ----------------------------

save_file_dir = "SaveFiles/"  # Change to your save file path here or blank for this folder. Must end with a / if not empty
main_save_file = "Babylon"  # Must contain the main_nation name in any way e.g. xxx_Babylon_xxx
main_nation = "Babylon"  # The nation the main file was created with
nations = ['Persia', 'Japan', 'Greece', 'Rome']  # Add new nations here

# --------------------- Settings ----------------------------

with open(save_file_dir + main_save_file, 'r') as f:
    full_save_file = f.read()
    for nation in nations:
        nation_file = full_save_file.replace(main_nation, nation)
        nation_file = nation_file[:len(nation_file) - 37]
        nation_file = nation_file + str(uuid.uuid4()) + '}'
        nation_file_path = save_file_dir + main_save_file.replace(main_nation, nation)
        with open(nation_file_path, 'w') as n:
            n.write(nation_file)
        print(f'Save file {nation_file_path} created')
