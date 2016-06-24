#! /usr/bin/env python
import json


def load_file(file):
    """ Converts an array of file paths into an array of json defined objects
    :param file: An array of filepath strings
    :return: An array of loaded json objects
    """
    CONFIGS = []
    with open(file, 'r') as f:
        j = json.load(f)
    f.close()
    CONFIGS.append(j)
    return CONFIGS


def process_json_minimal(conf):
    """ Processes an array of SignalFx Default Dashboard json objects
    :param conf: An array of json loaded objects
    :return: A string representation of a python dictionary named "DEFAULTS"
    """
    d = set()
    DEFAULTS = "DEFAULTS = {\n"
    # Iterate over each file passed in
    for file in conf:
        # Iterate each element in the first level array
        for a in file:
            # ? a.sf_chart
            if 'sf_chart' in a.keys():
                # ? a.sf_uiModel
                if 'sf_uiModel' in a.keys():
                    # ? a.sf_uiModel.allPlots
                    if 'allPlots' in a['sf_uiModel'].keys():
                        # Iterate over each plot in a.sf_uiModel.allPlots
                        for b in a['sf_uiModel']['allPlots']:
                            # ? a.sf_uiModel.allPlots[i].seriesData
                            if 'seriesData' in b.keys():
                                # ? a.sf_uiModel.allPlots[i].seriesData.metric
                                if 'metric' in b['seriesData'].keys():
                                    # temporarily store the metric name
                                    d.add(b['seriesData']['metric'])
    for elem in d:
        DEFAULTS += '    "' + elem + '",\n'
    DEFAULTS += '    # ADD ADDITIONAL METRIC NAMES\n'
    DEFAULTS += '    # TO INCLUDE BY DEFAULT\n'
    DEFAULTS += '}\n'
    return DEFAULTS


def save_file(text, file):
    """Saves the supplied string to a file
    :param text: The string that should be written out
    :param file: The path and file name to write out
    """
    f = open(file, 'w')
    f.write(text)
    f.close()


def run(files):
    """Main function of the script.
    """
    config = []
    for file in files:
        try:
            # Load the json files
            config += load_file(file)
            print "LOADED: %s" % file
        except Exception as e:
            print "Failed to load the following file '%s' due to: %s" % \
                   (file, e)
    if len(config) > 0:
        # Process the array of loaded json
        defaults = process_json_minimal(config)
        # Save the file to the working directory
        save_file(defaults, "DEFAULTS_DICT.py")
        # Load the generated defaults from the python file that was written out
        from DEFAULTS_DICT import DEFAULTS
        print DEFAULTS
    else:
        # There is nothing to process, so we print the usage message
        print """
generate_defaults.py

USAGE:
    $ ./generate_defaults.py <json file> <json file>...<json file>*
    $ python generate_defaults.py <json file> <json file>...<json file>*

INPUT:
    SignalFx Default Dashboard JSON files for Elasticsearch:
        Page_Elasticsearch.json
        Page_Elasticsearch_Index.json

OUTPUT:
    CONSOLE: Prints the generated set
    FILE: Generates a DEFAULTS_DICT.py file in the working directory

NOTE:
    While the DEFAULTS_DICT.py file can be imported,
    the elasticsearch_collectd.py file does not import this file.

    You MUST copy the DEFAULTS dictionary into the elasticsearch_collectd.py
    file when you wish to update the default dashboard.
"""

if __name__ == '__main__':
    import sys
    run(sys.argv[1:])
