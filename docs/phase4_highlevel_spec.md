screenshot puzzle setup

update the left side bar navigation with the following:
Add a navigation item called "From Image" below "From File" navigation item within the "Start New Game" Navigation item.

When "From Image" navigation item is clicked, display the following in the main content area.  There should be the following items in the main content:
* An area where the user can paste an image of a 4-by-4 grid of words.
* drop down list called "Provider Type"
* drop down list called "Model Type" 
* Button labelled "Setup Puzzle"

The general layout of the main content is show in the ascii diagram.

```text
+-----------------------+
|                       |
|                       |
|  Paste Puzzle Image   |
|        Here           |
|                       |
|                       |
|                       |
|                       |
+-----------------------+

    Provider Type
+-------------------+
|  OpenAI     ▼     |
+-------------------+

   Model Type
+-------------------+
|  GPT-4      ▼     |
+-------------------+

   [Setup Puzzle]
```

Allow the user to paste an image from the clipboard of a 4 by 4 grid with words in each grid cell into the area designated "Paste Puzzle Image Here".  Support only (CTRL/CMD+V). Drag-and-drop operation is out-of-scope.

The "Provider Type" and "Model Type" drop-down lists should be the same as the one used during puzzle solving, where the user can select the LLM model provider and specific LLM for that provider.  Valid values for "Provider Type" and "Model Type" should be the same as existing values used for puzzle solving.

When the user clicks on the "Setup Puzzle" button, the front end should call a new backend service called "/api/v2/setup_puzzle_from_image" that passes the pasted image as a base64 content along with the specified "Provider Type" and "Model Type".  The schema for the api call is the following
```json
{ "image_base64": "...", "image_mime": "image/png", "provider_type":"openai", "model_name":"gpt-4" }
```
Limit size of image to 5MB, if the image is larger than 5MB return HTTP 413 error with message "Payload too large."

The "/api/v2/setup_puzzle_from_image" performs the following:
* connects to the LLM for the specified "provider type" and "model type"
* invoke the LLM using the `with_structured_output()`to extract the 16 words in the image passed along as a base64 content.  The 16 words are in the image grid cells.
* The LLM should return the list of the 16 words as a JSON object.  

* If the word list extraction is successful the service should return the list of words in the same format as the existing backend service to for setting up a puzzle from a file.  This way the existing functions to setup a puzzle will work with the image extraction method.  The schema for the returned word list is `remaining_words` is a list of the 16 words extracted from the image and `status` indicating "success".  Example schema.  HTTP return is 200
```json
{"remaining_words": [w1, ..., w16], "status": "success"}
```
* If the word list extaction encounters an error, the system should dispaly a suitable error message.  Here are some example error returns:
  * HTTP 400 Bad Request: invalid image / validation fail 
    ```json
    { "status": "error", "message": "Could not extract 16 words" }
    ```
  * HTTP 422 Unprocessable Entity: missing fields
    ```json
    {"status": "error", "message": "Unprocessable Entity: missing fields"}
    ```
  * HTTP 500 Internal Error: LLM/provider failure
    ```json
    {"status": "error", "message": "Internal error: LLM provider failure"}
    ```

use of OCR is out of scope.

This is a single user application.  Multi-user, multi-session operation is out-of-scope.

Add new unit and integraton tests for the setup puzzle from image function.

Update existing tests as needed to account for the setup puzzle from image function.

Once the puzzle is setup from the image, the existing web ui for playing the game should be displayed.  There is no change in behavior for game playing.
