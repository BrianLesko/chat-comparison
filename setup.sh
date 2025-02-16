#!/usr/bin/env bash

# cd to the directory of this file
echo 'Changing directory to' "$(dirname "$(realpath "$0")")"
cd "$(dirname "$(realpath "$0")")"

# create a virtual environment
rm -rf myenv
echo 'Creating virtual environment'
python -m venv myenv

# activate the virtual environment
echo 'Activating virtual environment'
source myenv/bin/activate

# install the requirements
echo 'Installing requirements'
pip install -r requirements.txt

# create a keys.json file with a placeholder
echo 'Creating keys.json'
echo '{
    "xai_api_key": "<your_xai_api_key_here>",
    "openai_api_key": "<your_openai_api_key_here>",
    "anthropic_api_key": "<your_anthropic_api_key_here>"
    ...
}' > keys.json

# tell the user to add keys.json to the environment
echo 'Add your api keys to keys.json'

# Making the start.sh executable
echo 'Making start.sh executable'
chmod +x start.sh

# tell the user to start the app with ./start.sh
echo 'Start the app with ./start.sh'

