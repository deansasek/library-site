"""What's new pages: one per large release (major or minor feature releases). Patch releases get no page.

Facts come from the app's strings, the guide and privacy pages, and the merged changes between release tags.
Newest first. The first entry is marked Latest.
"""

RELEASES = [
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
]

LATEST = RELEASES[0]['id'] if RELEASES else None
