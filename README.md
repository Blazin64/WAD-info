# WAD-info
This tool allows you to view various information about WAD files that are used on the Nintendo Wii console. Currently, it is able to display a summary of the WAD header and/or CSV formatted title information. Other functionality may be addded in the future.

Compatible with both Python 2 and 3.

### Usage
Run `python wad-info.py -i <your WAD file here> --header` to view information in the header of a single WAD.

Run `python wad-info.py --header --batch --path <folder of WADs>` to view information in the headers of all WADs in a folder. Use it without the `--path` option to read WADs in the same folder as WAD-info.

If you're interested in things like title IDs and encrypted ticket keys, use the `--csv` option. WAD-info will show you the title ID, title version, encrypted ticket key, and filename in CSV format. It works in batch and single file mode.

Run `python wad-info.py --csv --batch --path <folder of WADs>` to do this.

### Credits

This would not have been possible without Segher Boessenkool or the writers of the WAD documentation at https://wiibrew.org/wiki/WAD_files. Thanks for your work, guys!
