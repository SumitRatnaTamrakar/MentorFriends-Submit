# MentorFriends-Submit
## Task assignment repository

## Run ExecuteScript.bat for easy execution of script.
It will install the required dependencies and run automatically run the Python script 'script.py'

### 'ExecuteScript.bat' operations:
- Creates a Python virtual environment named '.myVenv'
- Activates the created virtual environment
- Installs dependencies using requirements.txt in '.myVenv'
- Downloads SpaCy 'en_core_web_md' English pipeline
- Run Python script 'script.py'

### 'script.py' operations:
- Performs web scraping from Online Khabar English news website (https://english.onlinekhabar.com/)
- Saves scraped articles content into text files in a separate new 'Articles'' folder. The text files are named as integers i.e. '1.txt', '2.txt', '3.txt'... and so on
- Creates an index Excel spreadsheet named 'Article Index.xlsx' containing the file name and the article title to keep track of articles
- Performs text processing to extract subject, object and relationships for each sentence of the text files.
(Text processing works under the assumption that the sentence contains only single subject, object and predicate assumed to be the main verb in the sentence. Works well for simple sentences such as "John ate sea food."  But produces inconsistent result for complex sentences. Prefixes and modifiers of entities are also extracted to certain extent.)
- Creates graph from extracted entity relationships
- Saves graph into 'graph.gpickle' file

### Remaining tasks:
- Implementation of NLP question-answering funciton
- Optimization of entities and relationships from scraped text
