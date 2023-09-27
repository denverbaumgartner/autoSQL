import json
import requests

def create_gist(
        token: str, 
        filename: str, 
        content: any, 
        description: str="", 
        is_public: bool=True
    ):
    """Create a gist on GitHub.

    :param token: GitHub personal access token
    :type token: str
    :param filename: Name of the file to be created in the gist
    :type filename: str
    :param content: Content of the file
    :type content: any
    :param description: Description for the gist, defaults to ""
    :type description: str, optional
    :param is_public: Whether the gist should be public, defaults to True
    :type is_public: bool, optional
    :return: Response from the GitHub API
    :rtype: dict
    """
    
    # Define the URL for creating gists
    url = "https://api.github.com/gists"

    # Define the headers for the request
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
    }

    # Define the data for the gist
    data = {
        "description": description,
        "public": is_public,
        "files": {
            filename: {
                "content": content
            }
        }
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # Return the response as a dictionary
    return response.json()