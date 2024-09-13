Comandi per l'installazione
- git clone https://github.com/fabioerpini/sentence_similarity
- pip install PyQt6
- pip install numpy
- pip install gensim
- pip install sentence-transformers
- pip install python-docx

(Solo Windows) 
Errore Long Path:
- Open the Start menu and type "gpedit.msc" in the search bar. Press Enter to open the Local Group Policy Editor.
- In the editor, navigate to "Computer Configuration" > "Administrative Templates" > "System" > "Filesystem".
- Double-click the "Enable Win32 long paths" policy and set it to "Enabled".
- Click "OK" to save the policy changes.
- Retry with pip install sentence-transformers
