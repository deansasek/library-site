"""What's new pages: one per large release (major or minor feature releases). Patch releases get no page.

Facts come from the app's strings, the guide and privacy pages, and the merged changes between release tags.
Newest first. The first entry is marked Latest.
"""

RELEASES = [
    {
        'id': '1-6-6', 'version': '1.6.6', 'tag': 'v1.6.6', 'date': 'October 16, 2026',
        'summary': 'Option-click to edit an item from the menu, Find in the Edit menu, and a cleaner Quick Open.',
        'intro': 'Library 1.6.6 adds a quicker way to edit items, Find in the Edit menu, and a number of refinements to Quick Open and Edit Library. It also brings the menus and alerts closer to the conventions of macOS.',
        'sections': [
            ('New', [
                'Hold Option and click a bookmark, command, or app in the Library menu to see <strong>Edit…</strong>, which opens its Get Info.',
                'Find is in the Edit menu, with ⌘F, and moves to the search field.',
            ]),
            ('Improved', [
                'Quick Open shows its actions in an ellipsis menu, and its results are a standard list.',
                'Quick Open\'s placeholder reads Search Library, and its panel uses the system shadow.',
                'Edit Library has a single Get Info button, and its list highlights while a link or app is dragged over it.',
                'The sync footer shows a spinner while iCloud is working.',
                'Alerts put Cancel on the left, and the Library menu lists About and Settings first.',
                'Clearing clipboard history asks you to confirm first.',
                'Shortcut glyphs on the Welcome page use the standard text style.',
                'The iCloud Drive storage note is written in plainer language.',
            ]),
            ('Fixed', [
                'The file preview spinner and the shortcut options tooltip are clearer for VoiceOver and for everyone else.',
            ]),
        ],
    },
    {
        'id': '1-6-5', 'version': '1.6.5', 'tag': 'v1.6.5', 'date': 'October 16, 2026',
        'summary': 'Custom item colors, file previews in Quick Open, and search scopes in Edit Library.',
        'intro': 'Library 1.6.5 lets you choose a custom color for an item, preview files in Quick Open, and search by scope in Edit Library. It also fixes a number of data-safety, iCloud, and security issues, and it makes the app more responsive.',
        'sections': [
            ('New', [
                'Choose a custom color for an item in <strong>Get Info</strong>, with the system color picker.',
                'Preview files in Quick Open. Documents and images appear in Quick Look, and CSV and TSV files appear as a table.',
                'Search scopes and suggestions in Edit Library: All, Bookmarks, Apps, Commands, and Folders.',
                'Customize the toolbar in Edit Library.',
                'Reset Clipboard Key in <strong>Settings &gt; Clipboard</strong>, if the clipboard key is damaged.',
            ]),
            ('Improved', [
                'Edit Library remembers its sort order, sort direction, and search between launches.',
                '<strong>Open at Login</strong> shows whether approval is needed, and reports an error if it cannot be turned on.',
                'Welcome and the snippet editor open in their own windows.',
                'File panels and alerts attach to the Library window.',
                'Support for Increase Contrast and Differentiate Without Color in the pickers.',
                'Quick Open drags links, files, text, and pictures.',
                'Pasting from the clipboard menu goes into the app you were typing in.',
                'Screenshot capture is off by default. Turn it on in <strong>Settings &gt; Clipboard</strong>.',
                'Pinned clips are limited to 200 MB in total.',
                'Spotlight indexes an item\'s name and host only, not its command text.',
                'The Quick Look preview, the Manage window, and the menus update faster.',
            ]),
            ('Fixed', [
                'Restoring a backup that has Recently Deleted items works.',
                'Saving no longer overwrites a newer change from iCloud.',
                'Conflicts between three or more Macs are reviewed one version at a time, so no edits are lost.',
                'Damaged files are kept under a new name and never overwritten.',
                'Unpinning a locked clip requires Touch ID or your password.',
                'Delete no longer removes items the search has hidden.',
                'Undoing a rename no longer removes changes made on another Mac.',
                'Terminal commands restored from a backup no longer run at login.',
                'Backups and snippets are saved so only you can read them.',
                'Web requests no longer reach local or private network addresses.',
                'Installing checks the download before it runs, and replaces the app more safely.',
            ]),
        ],
    },
    {
        'id': '1-6-4', 'version': '1.6.4', 'tag': 'v1.6.4', 'date': 'October 15, 2026',
        'summary': 'Help moves into the Library menu, and the welcome tour covers every feature.',
        'intro': 'Library 1.6.4 puts Help at the bottom of the Library menu, and the welcome tour now covers each part of Library.',
        'sections': [
            ('Improved', [
                'Help is in the Library menu, under <strong>Help</strong>. It has Library Help, Keyboard Shortcuts, Welcome Tour, Report an Issue, and Support Library.',
                'The welcome tour has pages for finding things, copying and pasting, organizing, and working with other apps.',
            ]),
        ],
    },
    {
        'id': '1-6-3', 'version': '1.6.3', 'tag': 'v1.6.3', 'date': 'October 15, 2026',
        'summary': 'Screenshots and recordings join your clipboard history, and terminal commands can ask first.',
        'intro': 'Library 1.6.3 adds screenshots and recordings to clipboard history, a setting to confirm terminal commands, and a way to install the Command Line Tools.',
        'sections': [
            ('New', [
                'Screenshots and recordings are added to clipboard history as you take them. Turn this off in <strong>Settings &gt; Clipboard</strong>.',
                'Confirm Terminal Commands asks before a terminal command runs. It is off by default.',
                'Support Library in the Help menu opens the support page.',
                'The install command installs the Command Line Tools if they are missing.',
            ]),
            ('Fixed', [
                'Copying an item back from the clipboard menu keeps its source app.',
            ]),
        ],
    },
    {
        'id': '1-6-2', 'version': '1.6.2', 'tag': 'v1.6.2', 'date': 'October 15, 2026',
        'summary': 'Each folder can show or hide Open All, and link checks are described in plain language.',
        'intro': 'Library 1.6.2 lets each folder show or hide Open All, and describes link checks in plain language. Library is now open source under the MIT License.',
        'sections': [
            ('New', [
                'Each folder can show or hide <strong>Open All</strong>.',
            ]),
            ('Improved', [
                'Link check results are described in plain language.',
            ]),
            ('Other', [
                'Library is licensed under the MIT License.',
                'The documentation matches the app, and the README links to the website.',
            ]),
        ],
    },
    {
        'id': '1-6-1', 'version': '1.6.1', 'tag': 'v1.6.1', 'date': 'October 15, 2026',
        'summary': 'Update in Terminal builds the new version, and new labels follow Apple capitalization.',
        'intro': 'Library 1.6.1 fixes how Check for Updates installs a new version, and uses Apple capitalization in new labels.',
        'sections': [
            ('Improved', [
                'Update in Terminal downloads, builds, and installs the new version, then removes the download. Your library is kept.',
                'New labels use Apple capitalization.',
            ]),
        ],
    },
    {
        'id': '1-6-0', 'version': '1.6.0', 'tag': 'v1.6.0', 'date': 'October 15, 2026',
        'summary': 'Keep clipboard history across restarts, smart actions for detected text, notes, and a Reading List.',
        'intro': 'Library 1.6.0 keeps your clipboard history when you quit, if you turn that on, and adds smart actions, notes, and a Reading List.',
        'sections': [
            ('New', [
                'Keep clipboard history across restarts. Turn it on in <strong>Settings &gt; Clipboard</strong>. It is off by default, and turning it off deletes the saved history.',
                'Smart actions for detected text. Text with an address, a phone number, or a date gets <strong>Open in Maps</strong>, <strong>Copy Phone Number</strong>, or <strong>Add to Calendar</strong> in Quick Open, under Tab.',
                'Smart Punctuation in <strong>Copy as</strong>. It turns straight quotes and dashes into curly quotes, em dashes, and ellipses.',
                'Notes on any item. Write a note in Get Info. Quick Open shows it under the item\'s name.',
                'A Reading List. Add a bookmark from its right-click menu, or press Tab in Quick Open.',
                'Check links periodically, off by default. Library checks each bookmark\'s page once a day.',
                'Name new bookmarks from their pages, off by default. A new bookmark takes its page\'s title.',
                'Sort by <strong>Most Used</strong> or <strong>Recently Opened</strong> in Edit Library.',
            ]),
            ('Improved', [
                'Drag rows in Edit Library to reorder them.',
            ]),
            ('Fixed', [
                'Saving an edit to a folder keeps the folder\'s current contents.',
                'Links with a scheme such as <code>mailto:</code> or <code>obsidian://</code> keep that scheme.',
                'Merging duplicates keeps apps with different arguments, and links for other browsers, apart.',
                'A locked pinned item shows no title in rows or the Actions header.',
            ]),
        ],
    },
    {
        'id': '1-5-0', 'version': '1.5.0', 'tag': 'v1.5.0', 'date': 'October 14, 2026',
        'summary': 'Keep your library in iCloud Drive, paste a queue of clipboard items, and find and merge duplicate bookmarks.',
        'intro': 'Library 1.5.0 can keep your library in iCloud Drive, adds a clipboard queue and a lock for pinned items, and makes it easier to tidy your library.',
        'sections': [
            ('New', [
                'Keep the library in iCloud Drive, off by default. Turn it on in <strong>Settings &gt; General</strong>.',
                'Paste a queue of items, one at a time, in order.',
                'Filter clipboard history by app. Type <code>from Safari</code> in Quick Open.',
                'Copy text as lower or upper case, trimmed, or with its lines joined.',
                'Copy a bookmark as a Markdown link.',
                'Lock pinned items behind Touch ID or your password, off by default. Turn it on in <strong>Settings &gt; Clipboard</strong>.',
                'Find and merge duplicate bookmarks from <strong>File &gt; Find Duplicates…</strong>.',
                'Edit several items at once.',
                'Open a folder\'s bookmarks and apps together.',
                'Export and restore your whole library from <strong>Settings &gt; General</strong>.',
                'Snippets in Quick Open. Save reusable text and find it by name.',
                'Copy links without tracking codes such as <code>utm_source</code>.',
                'Check for Updates checks for a newer version. Automatic checks run each hour, as the default.',
            ]),
            ('Improved', [
                'Quick Open no longer shows calculator, unit, or web answers that Spotlight already gives.',
                'The Actions hint in Quick Open is a button.',
            ]),
            ('Fixed', [
                'Your bookmarks file stays private.',
                'Terminal command files are private from the moment they are created.',
                'Services accept only web links from text selections.',
                'Leftover Quick Look copies are cleared when Library launches.',
                'Merging duplicates keeps the shortcuts of the copies.',
            ]),
        ],
    },
    {
        'id': '1-4-0', 'version': '1.4.0', 'tag': 'v1.4.0', 'date': 'October 14, 2026',
        'summary': 'Pinned clipboard items are encrypted, and Quick Open responds more quickly.',
        'intro': 'Library 1.4.0 encrypts pinned clipboard items and makes Quick Open faster and steadier.',
        'sections': [
            ('New', [
                'Pinned clipboard items are encrypted with a key kept in your Keychain.',
            ]),
            ('Improved', [
                'Quick Open narrows its results as you type, more quickly.',
                'Quick Open stays open while you use a Quick Look preview.',
                'Settings, Quick Open, and Edit Library follow Apple\'s interface guidelines more closely.',
            ]),
            ('Fixed', [
                'Site icons load within a fixed size, and Library stops retrying sites whose icons fail.',
                'Renaming an item no longer repeats its icon and shortcut work.',
            ]),
        ],
    },
    {
        'id': '1-3-0', 'version': '1.3.0', 'tag': 'v1.3.0', 'date': 'October 14, 2026',
        'summary': 'A Help menu, and better labels for VoiceOver.',
        'intro': 'Library 1.3.0 adds a Help menu and labels for VoiceOver, and fixes Services for Finder folders.',
        'sections': [
            ('New', [
                'A Help menu with the guide, the keyboard shortcuts, a tour, and a way to report an issue.',
            ]),
            ('Improved', [
                'Search fields, Quick Open actions, and buttons have labels for VoiceOver. Decorative icons are hidden from it.',
            ]),
            ('Fixed', [
                'Services link Finder folders, and no longer create empty groups.',
            ]),
        ],
    },
    {
        'id': '1-2-0', 'version': '1.2.0', 'tag': 'v1.2.0', 'date': 'October 14, 2026',
        'summary': 'Import bookmarks from Safari and Chrome, preview clipboard items with Space, and add apps and folders from Finder.',
        'intro': 'Library 1.2.0 imports bookmarks from Safari and Chrome, adds Quick Look for clipboard items, and lets you add apps and folders from Finder.',
        'sections': [
            ('New', [
                'Import bookmarks from Safari and Chrome with <strong>File &gt; Import Bookmarks…</strong>. They go into one folder.',
                'Preview a clipboard item in Quick Look with Space.',
                'Add apps and folders from Finder with Services.',
                'Shortcuts app actions for bookmarks, search, and the clipboard. These appear only in builds that include App Intents metadata.',
            ]),
            ('Improved', [
                'The Edit Library window has a toolbar, search, and an empty state.',
                'The menu item for editing an item is <strong>Edit…</strong>, instead of Get Info.',
            ]),
            ('Fixed', [
                'Quick Open and the tag ring use the system secondary colors.',
            ]),
        ],
    },
    {
        'id': '1-1-0', 'version': '1.1.0', 'tag': 'v1.1.0', 'date': 'October 14, 2026',
        'summary': 'Library no longer runs commands from links, and it respects Reduce Motion.',
        'intro': 'Library 1.1.0 makes your bookmarks safer and respects Reduce Motion.',
        'sections': [
            ('Improved', [
                'Quick Open respects Reduce Motion.',
                'App icons refresh when Library is updated.',
            ]),
            ('Fixed', [
                'Library never runs commands from links.',
                'Your bookmarks file stays safe.',
            ]),
        ],
    },
    {
        'id': '1-0-0', 'version': '1.0.0', 'tag': 'v1.0.0', 'date': 'October 13, 2026',
        'summary': 'The first release of Library, a menu bar app for bookmarks, apps, and commands.',
        'intro': 'Library 1.0.0 is the first release. It keeps your bookmarks, apps, and commands in the menu bar, and was published as source.',
        'sections': [
            ('New', [
                'Bookmarks, apps, folders, and terminal commands in the menu bar, opened with a click or a shortcut.',
                'Quick Open, which searches your library from anywhere.',
                'Services, so you can add a selected link from other apps.',
            ]),
        ],
    },
]

LATEST = RELEASES[0]['id'] if RELEASES else None
