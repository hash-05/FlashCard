# Local Setup
- Install necessary requirements from `requirements.txt`
- Run `main.py`
- Username= "vins",Password="awdasda"

# Folder Structure

- `db_directory` has the sqlite DB. It can be anywhere on the machine. Adjust the path in ``application/config.py`.
- `application` is where application code is
- `static` - default `static` files folder. It serves at '/static' path. More about it is [here](https://flask.palletsprojects.com/en/2.0.x/tutorial/static/).
- `static/bootstrap` Bootstrap files.
- `static/style.css` Custom CSS
- `static/fontawesome` Fontawesome files.
- `static/images` - Images used in the app
- `templates` - Default flask templates folder

```
│   main.py
|   openapi(FlashCard).yaml
│   README.md
│   requirements.txt
│
├───.idea
│   │   .gitignore
│   │   dataSources.local.xml
│   │   dataSources.xml
│   │   Flashcard App.iml
│   │   misc.xml
│   │   modules.xml
│   │   workspace.xml
│   │
│   ├───dataSources
│   └───inspectionProfiles
│           profiles_settings.xml
│
├───application
│   │   api.py
│   │   config.py
│   │   controllers.py
│   │   database.py
│   │   deckService.py
│   │   loginService.py
│   │   model.py
│   │   notification.py
│   │
│   └───__pycache__
│           api.cpython-39.pyc
│           config.cpython-39.pyc
│           controllers.cpython-39.pyc
│           database.cpython-39.pyc
│           deckService.cpython-39.pyc
│           model.cpython-39.pyc
│
├───db_directory
│       database_flashcard.sqlite3
│
├───static
│   │   style.css
│   │
│   ├───bootstrap
│   │   ├───css
│   │   │       bootstrap-grid.css
│   │   │       bootstrap-grid.css.map
│   │   │       bootstrap-grid.min.css
│   │   │       bootstrap-grid.min.css.map
│   │   │       bootstrap-grid.rtl.css
│   │   │       bootstrap-grid.rtl.css.map
│   │   │       bootstrap-grid.rtl.min.css
│   │   │       bootstrap-grid.rtl.min.css.map
│   │   │       bootstrap-reboot.css
│   │   │       bootstrap-reboot.css.map
│   │   │       bootstrap-reboot.min.css
│   │   │       bootstrap-reboot.min.css.map
│   │   │       bootstrap-reboot.rtl.css
│   │   │       bootstrap-reboot.rtl.css.map
│   │   │       bootstrap-reboot.rtl.min.css
│   │   │       bootstrap-reboot.rtl.min.css.map
│   │   │       bootstrap-utilities.css
│   │   │       bootstrap-utilities.css.map
│   │   │       bootstrap-utilities.min.css
│   │   │       bootstrap-utilities.min.css.map
│   │   │       bootstrap-utilities.rtl.css
│   │   │       bootstrap-utilities.rtl.css.map
│   │   │       bootstrap-utilities.rtl.min.css
│   │   │       bootstrap-utilities.rtl.min.css.map
│   │   │       bootstrap.css
│   │   │       bootstrap.css.map
│   │   │       bootstrap.min.css
│   │   │       bootstrap.min.css.map
│   │   │       bootstrap.rtl.css
│   │   │       bootstrap.rtl.css.map
│   │   │       bootstrap.rtl.min.css
│   │   │       bootstrap.rtl.min.css.map
│   │   │
│   │   └───js
│   │           bootstrap.bundle.js
│   │           bootstrap.bundle.js.map
│   │           bootstrap.bundle.min.js
│   │           bootstrap.bundle.min.js.map
│   │           bootstrap.esm.js
│   │           bootstrap.esm.js.map
│   │           bootstrap.esm.min.js
│   │           bootstrap.esm.min.js.map
│   │           bootstrap.js
│   │           bootstrap.js.map
│   │           bootstrap.min.js
│   │           bootstrap.min.js.map
│   │
│   ├───fontawesome
│   │       font-awesome.min.css
│   │
│   ├───fonts
│   │       fontawesome-webfont.ttf
│   │       fontawesome-webfont.woff
│   │       fontawesome-webfont.woff2
│   │
│   └───images
│           error3.png
│           login_img.jpg
│
├───templates
│       add_card.html
│       create_deck.html
│       edit_card.html
│       edit_deck.html
│       edit_deck_page.html
│       Error_page.html
│       login_page.html
│       rename_deck.html
│       reset_page.html
│       review_page.html
│       signup_page.html
│       test.html
│       user_dashboard.html
│
└───__pycache__
        main.cpython-39.pyc
```
