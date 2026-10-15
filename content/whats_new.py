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
]

LATEST = RELEASES[0]['id'] if RELEASES else None
