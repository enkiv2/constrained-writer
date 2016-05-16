# constrained-writer
Apply various constraints &amp; autocomplete variations in a simple editor


## How to use

First, create a 'bigram model' from one or more text files:

    ./constraintWriterTool.py compile myCorpus.txt myModel.bigrams
    ./constraintWriterTool.py compileMulti myBigModel.bigrams myFirstCorpus.txt mySecondCorpus.txt

Then, run the GUI editor:

    ./constrained-writer.py

You can bring in your model as a whitelist or blacklist for highlighting disallowed words (like in Up-goer Five), or bring it in as an "autosuggest corpus".

As you type into the left hand panel, if you have brought in an autosuggest corpus, suggestions should appear at the right. Press control-return to accept the selected item, or control-up and control-down to select a different item. If you have a whitelist, non-whitelisted words will appear with a green background; if you have a blacklist, blacklisted words will appear with a red background.

